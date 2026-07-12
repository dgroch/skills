#!/usr/bin/env python3
import argparse
import importlib.util
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROFILE_HYBRID_PATH='/opt/data/profiles/creative/scripts/hashgifted_hybrid_pipeline.py'
SIBLING_HYBRID_PATH=Path(__file__).with_name('hashgifted_hybrid_pipeline.py')
HYBRID_PATH=str(SIBLING_HYBRID_PATH if SIBLING_HYBRID_PATH.exists() else Path(PROFILE_HYBRID_PATH))
SHORTLIST_PATH='/opt/data/tmp/hashgifted_reflexed_new_applicant_shortlist_sweep.py'
CAMPAIGNS={'Reflexed Roses - Red','Reflexed Roses - White','Reflexed Roses - Pastel Pink'}
PENDING={'SUBMITTED','NEGOTIATION','SHORTLISTED'}
BRAND_POINTS={'Strong':40,'Good':34,'Maybe':24,'Weak':10,'Unsafe':0}
CONTENT_POINTS={'Excellent':30,'Good':24,'Mixed':15,'Weak':6,'Unknown':12}
HORIZON_PLANNED=12
HORIZON_ALTERNATES=3
OUTREACH_THRESHOLD=70
BRAND_THRESHOLD=28
MANAGED_START='<!-- RANKED_POOL_POLICY_START -->'
MANAGED_END='<!-- RANKED_POOL_POLICY_END -->'


def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def score_candidate(brand_fit,content_quality,reliability_total=None,age_score=5):
    brand=BRAND_POINTS.get(brand_fit,20)
    content=CONTENT_POINTS.get(content_quality,12)
    reliability=10 if reliability_total is None else round(max(0,min(100,float(reliability_total)))*0.2,1)
    age=round(max(0,min(10,float(age_score))),1)
    return {'brand_fit':brand,'content_reusability':content,'reliability':reliability,'application_age':age,'total':round(brand+content+reliability+age,1)}


def queue_assignments(candidates,active_handles=None):
    active_handles=set(active_handles or [])
    grouped=defaultdict(list)
    for c in candidates:
        if c.get('exception') or c.get('handle') in active_handles:
            continue
        grouped[c['campaign']].append(c)
    assigned={}
    for campaign,rows in grouped.items():
        rows.sort(key=lambda x:(-x['score']['total'],-x['score']['brand_fit'],x.get('hashgifted_rank',10**9),x.get('handle','')))
        for i,c in enumerate(rows,1):
            state='locked_next_week' if i<=2 else ('planned' if i<=HORIZON_PLANNED else ('alternate' if i<=HORIZON_PLANNED+HORIZON_ALTERNATES else 'parked'))
            assigned[(c['campaign'],c['wave_uid'])]={'position':i,'queue_state':state}
    return assigned


def _prop_text(mod,p):
    try: return mod.prop_text(p)
    except Exception: return None


def notion_cache(short):
    cache={}
    for row in short.query_ds(short.CREATORS_DS,{'page_size':100}):
        p=row.get('properties',{})
        rec={
          'page_id':row.get('id'), 'handle':short.norm_handle(_prop_text(short,p.get('Handle',{}))),
          'brand_fit':_prop_text(short,p.get('Brand Fit',{})) or 'Unknown',
          'content_quality':_prop_text(short,p.get('Content Quality',{})) or 'Unknown',
          'brand_safety':_prop_text(short,p.get('Brand Safety',{})) or 'Unknown',
          'metro_eligible':_prop_text(short,p.get('Metro Eligible',{})) or 'Unconfirmed',
          'location':_prop_text(short,p.get('Location',{})) or '',
          'visual_evidence':_prop_text(short,p.get('Visual Evidence',{})) or '',
        }
        if rec['handle']: cache[rec['handle']]=rec
    return cache


def campaign_from_card(card):
    text=(card.get('name') or '')+'\n'+(card.get('desc') or '')
    return next((x for x in CAMPAIGNS if x in text),None)


def wave_from_card(card):
    m=re.search(r'(?im)^Hashgifted row UID:\s*([0-9a-f-]{36})\s*$',card.get('desc') or '')
    return m.group(1) if m else None


def managed_description(card,candidate,assignment,target,now):
    old=card.get('desc') or ''
    old=re.sub(re.escape(MANAGED_START)+r'.*?'+re.escape(MANAGED_END)+r'\n*','',old,flags=re.S)
    if target!='Needs Daniel' and 'WHAT DANIEL NEEDS TO DECIDE' in old:
        source_at=old.find('Source: Hashgifted / Fig & Bloom UGC')
        old=old[source_at:] if source_at>=0 else old
    status_line={
      'Parked Applicant Pool':'Parked Applicant Pool — retained and ranked outside the six-week operational horizon',
      'Triage / Brand Fit':'Ranked near-term applicant — fit/eligibility review',
      'Shortlisted':'Shortlisted — in six-week operational horizon',
      'Approved Reserve':'Approved Reserve — qualified within operational horizon',
      'Needs Daniel':'Needs Daniel — genuine policy/brand-safety exception',
    }.get(target,target)
    old=re.sub(r'(?im)^ACTION STATUS:\s*.*$',f'ACTION STATUS: {status_line}',old,count=1)
    s=candidate['score']; q=assignment.get('queue_state') if assignment else 'exception'
    pos=assignment.get('position') if assignment else None
    gate='eligible' if candidate.get('location_eligible') else 'ranked but ineligible until location confirmation'
    block=(f"{MANAGED_START}\nACTION STATUS: {status_line}\nRANKED APPLICANT POOL POLICY\nQueue state: {q}\nCampaign position: {pos if pos is not None else 'exception'}\n"
           f"Score: {s['total']}/100 (brand fit {s['brand_fit']}/40; content quality/reusability {s['content_reusability']}/30; reliability {s['reliability']}/20; application age {s['application_age']}/10)\n"
           f"Eligibility: {gate}\nBrand fit source: {candidate.get('brand_fit')}\nContent quality source: {candidate.get('content_quality')}\n"
           f"Operational target: {target}\nLast ranked: {now}\n{MANAGED_END}\n\n")
    return block+old


def build_live_plan():
    hybrid=load_module(HYBRID_PATH,'hybrid_rank'); h=hybrid.load_legacy(); h.load_env(); token=h.login()
    short=load_module(SHORTLIST_PATH,'shortlist_rank'); short.load_env(); cache=notion_cache(short)
    audit={'warnings':[],'trello_support_errors':[]}; ctx=h.trello_context(audit); inv={v:k for k,v in ctx.get('lists',{}).items()}
    gift_resp=h.req('GET',f'{h.BASE}/producer/brands/{h.BRAND_ID}/gifts',token)
    gifts=[g for g in (gift_resp.get('data') or []) if g.get('name') in CAMPAIGNS]
    rows=[]; active_handles=set()
    for g in gifts:
        for row in h.fetch_waves(token,g['uid']):
            handle=h.inf_summary(row)[1]
            if row.get('status')=='ACCEPTED' and handle: active_handles.add(handle)
            if row.get('status') not in PENDING: continue
            inf=row.get('influencer') or {}; n=cache.get(handle,{})
            reliability=(inf.get('reliability_score') or {}).get('total_score') if isinstance(inf.get('reliability_score'),dict) else None
            sc=score_candidate(n.get('brand_fit','Unknown'),n.get('content_quality','Unknown'),reliability,5)
            bs=n.get('brand_safety','Unknown')
            rows.append({'campaign':g['name'],'campaign_status':g.get('status'),'gift_id':g['uid'],'wave_uid':row.get('uid'),'status':row.get('status'),'handle':handle,'hashgifted_rank':row.get('rank') if isinstance(row.get('rank'),(int,float)) else 10**9,'brand_fit':n.get('brand_fit','Unknown'),'content_quality':n.get('content_quality','Unknown'),'brand_safety':bs,'location':n.get('location',''),'metro_eligible':n.get('metro_eligible','Unconfirmed'),'location_eligible':n.get('metro_eligible') in {'Confirmed','Likely'},'outreach_eligible':sc['total']>=OUTREACH_THRESHOLD and sc['brand_fit']>=BRAND_THRESHOLD,'score':sc,'exception':bs in {'Concern','Unsafe'},'notion_page_id':n.get('page_id')})
    assignments=queue_assignments(rows,active_handles)
    by_wave={(r['campaign'],r['wave_uid']):r for r in rows}
    actions=[]; unmatched=[]
    for card in ctx.get('cards',[]):
        campaign=campaign_from_card(card); wave=wave_from_card(card)
        if not campaign or not wave: continue
        c=by_wave.get((campaign,wave))
        if not c: continue
        assignment=assignments.get((campaign,wave))
        current=inv.get(card.get('idList'),'Unknown')
        if c['exception']:
            target='Needs Daniel'; queue_state='exception'
        elif not assignment or assignment['queue_state']=='parked':
            target='Parked Applicant Pool'; queue_state='parked'
        elif current=='Approved Reserve':
            target='Approved Reserve'; queue_state=assignment['queue_state']
        elif c['status']=='SHORTLISTED':
            target='Shortlisted'; queue_state=assignment['queue_state']
        else:
            target='Triage / Brand Fit'; queue_state=assignment['queue_state']
        actions.append({'card_id':card.get('id'),'card_url':card.get('url'),'title':card.get('name'),'campaign':campaign,'wave_uid':wave,'handle':c['handle'],'current_list':current,'target_list':target,'queue_state':queue_state,'position':assignment.get('position') if assignment else None,'score':c['score'],'outreach_eligible':c['outreach_eligible'],'location_eligible':c['location_eligible'],'description':managed_description(card,c,assignment,target,datetime.now(timezone.utc).isoformat())})
    return {'created_at':datetime.now(timezone.utc).isoformat(),'policy_version':'ranked-pool-v1','campaigns':[{'name':g.get('name'),'status':g.get('status')} for g in gifts],'candidate_count':len(rows),'active_handles':sorted(active_handles),'actions':actions,'unmatched':unmatched,'trello_errors':audit.get('trello_support_errors')}


def write_json(path,data):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')


def ensure_parked_list(h,ctx):
    if ctx.get('lists',{}).get('Parked Applicant Pool'):
        return {'ok':True,'id':ctx['lists']['Parked Applicant Pool'],'action':'existing'}
    board=h.trello_req('GET',f'/boards/{getattr(h,"TRELLO_BOARD","zDpcpS3V")}',{'fields':'id,name'})
    board_id=(board.get('data') or {}).get('id') if board.get('ok') else None
    if not board_id:
        return {'ok':False,'action':'board_lookup_failed','write_ok':False,'read_ok':False}
    made=h.trello_req('POST','/lists',{'name':'Parked Applicant Pool','idBoard':board_id,'pos':'bottom'})
    fresh=h.trello_context({},force=True) if 'force' in getattr(h.trello_context,'__code__',type('x',(),{'co_varnames':()})).co_varnames else None
    lid=(made.get('data') or {}).get('id') if made.get('ok') else None
    if lid: ctx.setdefault('lists',{})['Parked Applicant Pool']=lid
    rb=h.trello_req('GET',f'/lists/{lid}') if lid else {'ok':False}
    return {'ok':bool(lid and rb.get('ok') and (rb.get('data') or {}).get('name')=='Parked Applicant Pool'),'id':lid,'action':'created','write_ok':made.get('ok'),'read_ok':rb.get('ok')}


def apply_plan(plan,output):
    hybrid=load_module(HYBRID_PATH,'hybrid_apply_rank'); h=hybrid.load_legacy(); h.load_env(); audit={'warnings':[],'trello_support_errors':[]}; ctx=h.trello_context(audit)
    list_result=ensure_parked_list(h,ctx)
    results=[]
    if not list_result.get('ok'):
        out={'ok':False,'reason':'parked_list_unavailable','list_result':list_result,'results':[]}; write_json(output,out); return out
    for a in plan.get('actions',[]):
        desc=hybrid._review_update_verified(h,a['card_id'],a['description'])
        move=hybrid._move_verified(h,a['card_id'],a['target_list'],ctx)
        results.append({'card_id':a['card_id'],'url':a['card_url'],'campaign':a['campaign'],'handle':a['handle'],'from':a['current_list'],'to':a['target_list'],'queue_state':a['queue_state'],'position':a['position'],'score':a['score']['total'],'description_ok':desc.get('ok'),'move_ok':move.get('ok')})
    out={'ok':all(x['description_ok'] and x['move_ok'] for x in results),'list_result':list_result,'results':results,'trello_errors':audit.get('trello_support_errors')}
    write_json(output,out); return out


def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('plan'); p.add_argument('--output',required=True)
    a=sub.add_parser('apply'); a.add_argument('--plan',required=True); a.add_argument('--output',required=True)
    args=ap.parse_args()
    if args.cmd=='plan':
        data=build_live_plan(); write_json(args.output,data); print(json.dumps({'ok':not data['trello_errors'],'candidate_count':data['candidate_count'],'actions':len(data['actions']),'output':args.output}))
    else:
        plan=json.loads(Path(args.plan).read_text()); out=apply_plan(plan,args.output); print(json.dumps({'ok':out['ok'],'count':len(out['results']),'output':args.output})); raise SystemExit(0 if out['ok'] else 3)

if __name__=='__main__': main()
