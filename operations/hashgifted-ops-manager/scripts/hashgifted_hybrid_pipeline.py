#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ALLOWED_ACTIONS={'manual_review','no_action','send_message','approved_reserve','select_accept','reject_human'}
ALLOWED_CLASSIFICATIONS={'initial_outreach','awaiting_creator','needs_gate_clarification','qualified','qualified_reserve','routine_support','support_needs_reply','exception_needs_review','human_command','ambiguous','no_action'}
AUTO_ACTIONS={'send_message','approved_reserve','select_accept'}
REQUIRED_FACTS=('delivery_eligible','brief_confirmed')
LEGACY_PATH='/opt/data/tmp/hashgifted_reflexed_selection_sweep.py'
PER_CAMPAIGN_WEEKLY_CAP=3
CAMPAIGN_TIMEZONE=ZoneInfo('Australia/Melbourne')
REFLEXED_CAMPAIGNS={'Reflexed Roses - Red','Reflexed Roses - White','Reflexed Roses - Pastel Pink'}
RESERVE_NOTIFICATION_MARKERS=(
    'approved in our queue',
    'ranked waiting pool',
    'limited number of gifts each week',
    'weekly limit on creator gifts',
)


def load_legacy():
    spec=importlib.util.spec_from_file_location('hashgifted_legacy',LEGACY_PATH)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def norm(text):
    return ' '.join(str(text or '').split()).casefold()


def sha256_text(text):
    return hashlib.sha256(str(text or '').encode()).hexdigest()


def campaigns_in_scope(gifts):
    return [g for g in gifts if g.get('name') in REFLEXED_CAMPAIGNS and str(g.get('status') or '').upper() in {'ACTIVE','CLOSED'}]


def fetch_operational_gifts(h,token):
    """Discover active and intake-closed gifts without relying on a tmp helper API."""
    gifts=[]; seen=set()
    for status in ('ACTIVE','CLOSED'):
        result=h.req('GET',f'{h.BASE}/producer/brands/{h.BRAND_ID}/gifts?status={status}',token)
        if not result.get('ok') or not isinstance(result.get('data'),list):
            raise RuntimeError(f'gift discovery failed for {status} HTTP {result.get("status")}')
        for gift in result['data']:
            uid=gift.get('uid')
            if uid and uid not in seen:
                seen.add(uid); gifts.append(gift)
    return gifts


def live_preflight(candidate, live_transcript):
    current=sha256_text(live_transcript)
    if current!=candidate.get('thread_sha256'):
        return {'ok':False,'reason':'thread_changed_since_llm_review','expected':candidate.get('thread_sha256'),'actual':current}
    return {'ok':True,'reason':'thread_unchanged'}


def effective_action(decision,candidate):
    action=decision.get('action')
    if action=='select_accept' and candidate.get('selection_window_open') is False:
        return 'approved_reserve'
    if action=='select_accept' and int(candidate.get('selected_this_week') or 0)>=int(candidate.get('weekly_cap') or PER_CAMPAIGN_WEEKLY_CAP):
        return 'approved_reserve'
    return action


def reply_block_reason(text):
    t=norm(text)
    if not t: return 'empty_message'
    if len(text)>2500: return 'message_too_long'
    if any(x in t for x in ['unit number','street address','full address','delivery address is','send your address','what is your address']):
        return 'asks_for_detailed_address'
    if any(x in t for x in ['payment will be','we will pay','invoice us','discount code','commission','exclusive partnership']):
        return 'commercial_terms_need_review'
    if 'notion.site' in t and 'abrupt-paneer-687.notion.site' not in t:
        return 'possible_private_notion_link'
    return ''


def build_candidate(gift_id,wave_uid,campaign,status,handle,messages,selected_this_week,weekly_cap):
    ordered=sorted(messages,key=lambda m:str(m.get('created_at') or ''))
    lines=[]
    for m in ordered:
        who='Fig & Bloom' if m.get('is_brand') else 'Creator'
        lines.append(f"[{m.get('created_at') or 'unknown time'}] {who}: {m.get('raw_text') or m.get('text') or ''}")
    transcript='\n\n'.join(lines)
    return {
        'gift_id':gift_id,'wave_uid':wave_uid,'campaign':campaign,'status':status,
        'handle':handle,'conversation_url':f'https://brands.hashgifted.com/gift-view/{gift_id}?wave={wave_uid}',
        'messages':ordered,'transcript':transcript,'thread_sha256':sha256_text(transcript),
        'selected_this_week':selected_this_week,'weekly_cap':weekly_cap,
    }


def validate_decision_bundle(collection, decisions):
    errors=[]; valid=[]
    if decisions.get('run_id')!=collection.get('run_id'):
        return {'ok':False,'errors':[{'bundle':['run_id_mismatch']}],'valid_decisions':[]}
    candidates={(x.get('gift_id'),x.get('wave_uid')):x for x in collection.get('candidates',[])}
    seen=set()
    for d in decisions.get('decisions',[]):
        key=(d.get('gift_id'),d.get('wave_uid')); derr=[]
        c=candidates.get(key)
        if not c: derr.append('candidate_not_in_collection')
        if key in seen: derr.append('duplicate_candidate_decision')
        seen.add(key)
        action=d.get('action')
        if d.get('classification') not in ALLOWED_CLASSIFICATIONS: derr.append('unsupported_classification')
        if action not in ALLOWED_ACTIONS: derr.append('unsupported_action')
        if action in AUTO_ACTIONS and d.get('confidence')!='high': derr.append('auto_action_requires_high_confidence')
        if action=='send_message':
            block=reply_block_reason(d.get('reply_text') or '')
            if block: derr.append(f'reply_blocked:{block}')
        if action=='manual_review' and not str(d.get('manual_question') or '').strip():
            derr.append('manual_question_required')
        if not str(d.get('reason') or '').strip(): derr.append('reason_required')
        if c:
            transcript=norm(c.get('transcript'))
            pending=c.get('pending_human_commands') or []
            if pending:
                command=pending[0]
                if d.get('human_command_id')!=command.get('comment_id'):
                    derr.append('latest_human_command_must_be_acknowledged')
                elif command.get('type')=='send' and command.get('mode')=='draft_only' and action!='no_action':
                    derr.append('draft_only_command_must_not_send')
                elif command.get('type')=='send' and command.get('mode')!='draft_only' and (action!='send_message' or norm(d.get('reply_text'))!=norm(command.get('message'))):
                    derr.append('send_command_must_use_exact_message')
                elif command.get('type')=='reject' and action!='reject_human':
                    derr.append('reject_command_must_use_reject_human')
                elif command.get('type')=='approve' and action not in {'select_accept','approved_reserve','manual_review'}:
                    derr.append('approve_command_not_reflected_in_action')
            if action=='reject_human' and not any(x.get('type')=='reject' for x in pending):
                derr.append('reject_requires_explicit_human_command')
            if c.get('candidate_type')=='accepted_support' and action in {'approved_reserve','select_accept','reject_human'}:
                derr.append('action_invalid_for_accepted_creator')
            for fact,quote in (d.get('fact_evidence') or {}).items():
                if quote and norm(quote) not in transcript:
                    derr.append(f'evidence_quote_not_in_transcript:{fact}')
            if action in {'approved_reserve','select_accept'}:
                facts=d.get('facts') or {}; evidence=d.get('fact_evidence') or {}
                for fact in REQUIRED_FACTS:
                    if facts.get(fact) is not True: derr.append(f'qualification_fact_not_true:{fact}')
                    if not str(evidence.get(fact) or '').strip(): derr.append(f'qualification_evidence_missing:{fact}')
                reel_ok=facts.get('reel_confirmed') is True and bool(str(evidence.get('reel_confirmed') or '').strip())
                exception_ok=facts.get('deliverable_exception_approved') is True and bool(str(evidence.get('deliverable_exception_approved') or '').strip())
                if not (reel_ok or exception_ok):
                    derr.append('approved_deliverable_evidence_missing')
                if action=='approved_reserve':
                    already_notified=any(marker in transcript for marker in RESERVE_NOTIFICATION_MARKERS)
                    reply=str(d.get('reply_text') or '').strip()
                    if not already_notified and not reply:
                        derr.append('reserve_notification_required')
                    if reply:
                        block=reply_block_reason(reply)
                        if block: derr.append(f'reserve_reply_blocked:{block}')
        if derr: errors.append({'gift_id':key[0],'wave_uid':key[1],'errors':derr})
        else: valid.append(d)
    missing=[{'gift_id':k[0],'wave_uid':k[1],'errors':['decision_missing']} for k in candidates if k not in seen]
    errors.extend(missing)
    return {'ok':not errors,'errors':errors,'valid_decisions':valid if not errors else []}


def collect_live(output_path=None):
    """Read active and intake-closed operational Reflexed Rose threads without side effects."""
    h=load_legacy(); h.load_env(); token=h.login(); now=datetime.now(timezone.utc)
    gifts=campaigns_in_scope(fetch_operational_gifts(h,token)); campaign_ids={g['name']:g['uid'] for g in gifts}
    rows_by_campaign={name:h.fetch_waves(token,gid) for name,gid in campaign_ids.items()}
    start=h.week_start(now); selected_by_campaign={}
    for campaign,rows in rows_by_campaign.items():
        selected_by_campaign[campaign]=0
        for row in rows:
            if row.get('status') not in {'ACCEPTED','COMPLETED'}: continue
            dt=h.parse_dt(row.get('accepted_at') or row.get('status_updated_at') or row.get('completed_at'))
            if dt and dt>=start: selected_by_campaign[campaign]+=1
    selection_window_open=now.astimezone(CAMPAIGN_TIMEZONE).weekday()==0
    candidates=[]; failures=[]
    trello_audit={'warnings':[],'trello_support_errors':[]}; trello_ctx=h.trello_context(trello_audit)
    for campaign,gid in campaign_ids.items():
        for row in rows_by_campaign[campaign]:
            status=row.get('status')
            if status not in {'SHORTLISTED','ACCEPTED'}: continue
            uid=row.get('uid'); inf,handle=h.inf_summary(row)
            detail=h.req('GET',f'{h.BASE}/producer/gifts/{gid}/waves/{uid}?markAsSeen=false',token)
            if not detail.get('ok'):
                failures.append({'campaign':campaign,'wave_uid':uid,'error':f"detail_read_failed_http_{detail.get('status')}"}); continue
            msgs=h.collect_messages(detail.get('data') or {})
            c=build_candidate(gid,uid,campaign,status,handle,msgs,selected_by_campaign[campaign],PER_CAMPAIGN_WEEKLY_CAP)
            pending=[]; card=None
            if trello_ctx:
                title=h.support_card_title(handle,inf.get('name'),campaign)
                card=h.find_trello_card(trello_ctx,title,uid,handle,campaign)
                if card:
                    actions=h.trello_req('GET',f"/cards/{card['id']}/actions",{'filter':'commentCard','limit':'100'})
                    all_texts=[((x.get('data') or {}).get('text') or '') for x in (actions.get('data') or [])]
                    for a in actions.get('data') or []:
                        aid=a.get('id'); text=((a.get('data') or {}).get('text') or '')
                        if any(marker in x and str(aid) in x for x in all_texts for marker in ['CREATOR DECISION ACTIONED','CREATOR DECISION BLOCKED','SENT TO CREATOR','NOT SENT TO CREATOR']):
                            continue
                        dec=h.parse_creator_decision_comment(text)
                        send_cmd=h.parse_manual_send_comment(text)
                        if dec: pending.append({'comment_id':aid,'type':dec.get('decision'),'reason':dec.get('reason'),'raw':text})
                        elif send_cmd: pending.append({'comment_id':aid,'type':'send','message':send_cmd.get('message'),'mode':send_cmd.get('mode'),'raw':text})
            c.update({
                'creator_name':inf.get('name'),'candidate_type':'shortlisted_qualification' if status=='SHORTLISTED' else 'accepted_support',
                'trello_card':({'id':card.get('id'),'url':card.get('url')} if card else None),'pending_human_commands':pending,
                'brief':h.BRIEF_BY_CAMPAIGN.get(campaign),
                'selection_window_open':selection_window_open,
                'policy':{
                    'approved_delivery_regions':['Melbourne metro','Sydney metro','Brisbane metro','Geelong','Bannockburn','Sunshine Coast','Gold Coast'],
                    'per_campaign_weekly_platform_accept_cap':PER_CAMPAIGN_WEEKLY_CAP,
                    'selection_window':'Monday in Australia/Melbourne',
                    'auto_reject_allowed':False,
                    'irreversible_actions_require_deterministic_validation':True,
                }
            })
            candidates.append(c)
    run_id=now.strftime('hybrid-%Y%m%dT%H%M%SZ')
    bundle={'schema_version':1,'run_id':run_id,'collected_at':now.isoformat(),'mode':'read_only','candidates':candidates,'failures':failures}
    if output_path:
        out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(bundle,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return bundle


def _campaign_selected_live(h,token,gift,now):
    start=h.week_start(now); count=0
    for row in h.fetch_waves(token,gift['uid']):
        if row.get('status') not in {'ACCEPTED','COMPLETED'}: continue
        dt=h.parse_dt(row.get('accepted_at') or row.get('status_updated_at') or row.get('completed_at'))
        if dt and dt>=start: count+=1
    return count


def _review_description(candidate,decision,live_transcript,now):
    evidence='\n'.join(f"- {k}: {v}" for k,v in (decision.get('fact_evidence') or {}).items()) or '- See complete live transcript.'
    return (f"ACTION STATUS: Needs Daniel\n\nWHAT DANIEL NEEDS TO DECIDE\n{decision.get('manual_question')}\n\n"
            f"RECOMMENDED HANDLING\n{decision.get('recommendation') or decision.get('reason')}\n\nDECISION EVIDENCE\n{evidence}\n\n"
            f"Campaign: {candidate.get('campaign')}\nCreator: @{candidate.get('handle')}\nHashgifted conversation link: {candidate.get('conversation_url')}\n"
            f"Hashgifted row UID: {candidate.get('wave_uid')}\nLast verified: {now.isoformat()}\n\nCOMPLETE LIVE CONVERSATION\n{live_transcript}\n")


def _move_verified(h,card_id,list_name,ctx):
    moved=h.trello_move_card(card_id,list_name,ctx)
    expected=(ctx.get('lists') or {}).get(list_name) if ctx else None
    read=h.trello_req('GET',f'/cards/{card_id}')
    actual=(read.get('data') or {}).get('idList') if read.get('ok') else None
    return {'ok':bool(moved.get('ok') and expected and actual==expected),'list':list_name,'expected_list_id':expected,'actual_list_id':actual,'write_ok':bool(moved.get('ok')),'read_ok':bool(read.get('ok'))}


def _review_update_verified(h,card_id,desc):
    wrote=h.trello_req('PUT',f'/cards/{card_id}',body={'desc':desc})
    read=h.trello_req('GET',f'/cards/{card_id}')
    actual=(read.get('data') or {}).get('desc') if read.get('ok') else None
    return {'ok':bool(wrote.get('ok') and actual==desc),'write_ok':bool(wrote.get('ok')),'read_ok':bool(read.get('ok'))}


def _comment_verified(h,card_id,text):
    before=h.trello_req('GET',f'/cards/{card_id}/actions',{'filter':'commentCard','limit':'20'})
    already=any(((x.get('data') or {}).get('text') or '')==text for x in (before.get('data') or [])) if before.get('ok') else False
    if already:
        return {'ok':True,'write_ok':True,'read_ok':True,'exact_readback':True,'action':'skipped_exact_before'}
    wrote=h.trello_req('POST',f'/cards/{card_id}/actions/comments',body={'text':text})
    read=h.trello_req('GET',f'/cards/{card_id}/actions',{'filter':'commentCard','limit':'20'})
    found=any(((x.get('data') or {}).get('text') or '')==text for x in (read.get('data') or [])) if read.get('ok') else False
    return {'ok':bool(wrote.get('ok') and found),'write_ok':bool(wrote.get('ok')),'read_ok':bool(read.get('ok')),'exact_readback':found,'action':'posted'}


def _resolve_synced_card(h,ctx,sync,title,wave_uid,handle,campaign):
    card=h.find_trello_card(ctx,title,wave_uid,handle,campaign) if ctx else None
    card_info=(sync.get('card') or {})
    return {'id':(card or {}).get('id'),'url':(card or {}).get('url') or card_info.get('url'),'idList':(card or {}).get('idList')}


def apply_validated(collection,validation,dry_run=False):
    if not validation.get('ok'):
        return {'ok':False,'error':'validation_not_ok','actions':[]}
    h=load_legacy(); h.load_env(); token=h.login(); now=datetime.now(timezone.utc); gifts=campaigns_in_scope(fetch_operational_gifts(h,token))
    gifts_by_id={gift['uid']:gift for gift in gifts}
    candidates={(x['gift_id'],x['wave_uid']):x for x in collection.get('candidates',[])}
    selected_live_by_campaign={gift['name']:_campaign_selected_live(h,token,gift,now) for gift in gifts}
    audit={'warnings':[],'trello_support_errors':[],'conversation_sync':[],'manual_trello_sends':[]}
    ctx=None if dry_run else h.trello_context(audit)
    results=[]
    for decision in validation.get('valid_decisions',[]):
        key=(decision['gift_id'],decision['wave_uid']); candidate=candidates[key]
        detail=h.req('GET',f"{h.BASE}/producer/gifts/{key[0]}/waves/{key[1]}?markAsSeen=false",token)
        if not detail.get('ok'):
            results.append({'key':key,'status':'blocked','reason':'live_thread_read_failed'}); continue
        live_msgs=h.collect_messages(detail.get('data') or {})
        campaign=candidate.get('campaign'); selected_live=selected_live_by_campaign.get(campaign,0)
        selection_window_open=now.astimezone(CAMPAIGN_TIMEZONE).weekday()==0
        live_candidate=build_candidate(key[0],key[1],campaign,detail['data'].get('status'),candidate.get('handle'),live_msgs,selected_live,PER_CAMPAIGN_WEEKLY_CAP)
        pre=live_preflight(candidate,live_candidate['transcript'])
        if not pre['ok']:
            results.append({'key':key,'status':'blocked','reason':pre['reason']}); continue
        action=effective_action(decision,{'selected_this_week':selected_live,'weekly_cap':PER_CAMPAIGN_WEEKLY_CAP,'selection_window_open':selection_window_open})
        if dry_run:
            results.append({'key':key,'status':'dry_run','action':action,'reason':decision.get('reason')}); continue
        row=detail.get('data') or {}; inf,handle=h.inf_summary(row)
        sync=h.sync_thread_messages_to_trello(audit,candidate.get('campaign'),key[0],row,handle,live_msgs,'Shortlisted' if row.get('status')=='SHORTLISTED' else 'Selected / Brief Sent')
        title=h.support_card_title(handle,inf.get('name'),candidate.get('campaign'))
        resolved=_resolve_synced_card(h,ctx,sync,title,key[1],handle,candidate.get('campaign'))
        card_id=resolved.get('id'); card_url=resolved.get('url')
        if not card_id:
            results.append({'key':key,'status':'blocked','reason':'trello_card_unavailable','sync':sync}); continue
        outcome={'key':key,'card':card_url,'action':action,'status':'ok'}
        command_id=decision.get('human_command_id')
        if action=='manual_review':
            desc=_review_description(candidate,decision,live_candidate['transcript'],now)
            outcome['review_update']=_review_update_verified(h,card_id,desc)
            outcome['move']=_move_verified(h,card_id,'Needs Daniel',ctx)
        elif action=='no_action':
            outcome['status']='no_action'
        elif action=='send_message':
            block=reply_block_reason(decision.get('reply_text') or '')
            if block:
                outcome.update({'status':'blocked','reason':'reply_blocked:'+block})
            else:
                sent=h.send(token,key[0],key[1],decision['reply_text']); outcome['send']=sent
                current_list=next((name for name,lid in (ctx.get('lists') or {}).items() if lid==resolved.get('idList')),None)
                default_target='Active Q&A / Awaiting Content' if candidate.get('candidate_type')=='accepted_support' else (current_list or 'Shortlisted')
                target=decision.get('target_list') or default_target
                if target not in {'Shortlisted','Approved Reserve','Needs Daniel','Active Q&A / Awaiting Content'}: target='Shortlisted'
                if sent.get('verified_exact_readback'): outcome['move']=_move_verified(h,card_id,target,ctx)
                else: outcome.update({'status':'blocked','reason':'send_not_verified'})
        elif action=='approved_reserve':
            if decision.get('reply_text'):
                block=reply_block_reason(decision['reply_text'])
                if block: outcome.update({'status':'blocked','reason':'reply_blocked:'+block})
                else:
                    outcome['send']=h.send(token,key[0],key[1],decision['reply_text'])
                    if not outcome['send'].get('verified_exact_readback'):
                        outcome.update({'status':'blocked','reason':'reserve_message_not_verified'})
            if outcome['status']=='ok': outcome['move']=_move_verified(h,card_id,'Approved Reserve',ctx)
        elif action=='select_accept':
            gift=gifts_by_id.get(key[0]); live_now=datetime.now(timezone.utc)
            selected_live=_campaign_selected_live(h,token,gift,live_now) if gift else PER_CAMPAIGN_WEEKLY_CAP
            if live_now.astimezone(CAMPAIGN_TIMEZONE).weekday()!=0:
                outcome['action']='approved_reserve'; outcome['reason']='weekly_release_window_closed'; outcome['move']=_move_verified(h,card_id,'Approved Reserve',ctx)
            elif selected_live>=PER_CAMPAIGN_WEEKLY_CAP:
                outcome['action']='approved_reserve'; outcome['reason']='campaign_weekly_cap_full'; outcome['move']=_move_verified(h,card_id,'Approved Reserve',ctx)
            else:
                accepted=h.accept(token,key[0],key[1]); outcome['accept']=accepted
                if accepted.get('verified_status')=='ACCEPTED':
                    selected_live_by_campaign[campaign]=selected_live+1; outcome['move']=_move_verified(h,card_id,'Selected / Brief Sent',ctx)
                else: outcome.update({'status':'blocked','reason':'accept_not_verified'})
        elif action=='reject_human':
            rejected=h.reject(token,key[0],key[1]); outcome['reject']=rejected
            if rejected.get('verified_status') in {'REJECTED','DECLINED'}: outcome['move']=_move_verified(h,card_id,'Lapsed / Declined / Do Not Use',ctx)
            else: outcome.update({'status':'blocked','reason':'reject_not_verified'})
        if outcome.get('review_update') and not outcome['review_update'].get('ok'):
            outcome.update({'status':'blocked','reason':'trello_review_description_not_verified'})
        if outcome.get('move') and not outcome['move'].get('ok'):
            outcome.update({'status':'blocked','reason':'trello_move_not_verified'})
        if command_id:
            if outcome.get('status')=='ok' or outcome.get('status')=='no_action':
                marker='SENT TO CREATOR' if action=='send_message' else 'CREATOR DECISION ACTIONED'
            else:
                marker='NOT SENT TO CREATOR' if action=='send_message' else 'CREATOR DECISION BLOCKED'
            comment_text=f"{marker} — Trello instruction {command_id}. Hybrid pipeline result: {outcome.get('status')}; action: {outcome.get('action')}."
            outcome['command_comment']=_comment_verified(h,card_id,comment_text)
            if not outcome['command_comment'].get('ok'):
                outcome.update({'status':'blocked','reason':'trello_command_result_comment_not_verified'})
        results.append(outcome)
    result={'ok':not any(x.get('status')=='blocked' for x in results),'dry_run':dry_run,'run_id':collection.get('run_id'),'actions':results,'selected_live_end_by_campaign':selected_live_by_campaign}
    return result


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='command',required=True)
    c=sub.add_parser('collect'); c.add_argument('--output',required=True)
    v=sub.add_parser('validate'); v.add_argument('--collection',required=True); v.add_argument('--decisions',required=True); v.add_argument('--output')
    a=sub.add_parser('apply'); a.add_argument('--collection',required=True); a.add_argument('--validation',required=True); a.add_argument('--output'); a.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    if args.command=='collect':
        result=collect_live(args.output)
        print(json.dumps({'run_id':result['run_id'],'candidates':len(result['candidates']),'failures':result['failures'],'output':args.output},indent=2,ensure_ascii=False))
    elif args.command=='validate':
        result=validate_decision_bundle(json.loads(Path(args.collection).read_text()),json.loads(Path(args.decisions).read_text()))
        if args.output: Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
        print(json.dumps(result,indent=2,ensure_ascii=False)); raise SystemExit(0 if result['ok'] else 2)
    elif args.command=='apply':
        result=apply_validated(json.loads(Path(args.collection).read_text()),json.loads(Path(args.validation).read_text()),args.dry_run)
        if args.output: Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False,default=str)+'\n')
        print(json.dumps(result,indent=2,ensure_ascii=False,default=str)); raise SystemExit(0 if result.get('ok') else 3)


if __name__=='__main__': main()
