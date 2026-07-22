import importlib.util
import json
import unittest
from pathlib import Path

MODULE=Path(__file__).with_name('hashgifted_hybrid_pipeline.py')


def load_module():
    spec=importlib.util.spec_from_file_location('hybrid',MODULE)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class HybridDecisionTests(unittest.TestCase):
    def test_operational_gift_discovery_does_not_depend_on_tmp_helper_method(self):
        h=load_module()
        class FakeLegacy:
            BASE='https://example.test/service'
            BRAND_ID='brand'
            def req(self,method,url,token):
                status=url.rsplit('=',1)[-1]
                rows={'ACTIVE':[{'uid':'active','name':'Reflexed Roses - Red','status':'ACTIVE'}],
                      'CLOSED':[{'uid':'closed','name':'Reflexed Roses - White','status':'CLOSED'}]}
                return {'ok':True,'status':200,'data':rows[status]}
        gifts=h.fetch_operational_gifts(FakeLegacy(),'token')
        self.assertEqual([g['uid'] for g in gifts],['active','closed'])

    def test_campaign_scope_includes_intake_closed_but_operational_campaigns(self):
        h=load_module()
        gifts=[
            {'name':'Reflexed Roses - Red','status':'ACTIVE'},
            {'name':'Reflexed Roses - White','status':'CLOSED'},
            {'name':'Reflexed Roses - Pastel Pink','status':'CLOSED'},
            {'name':'Completed Legacy','status':'CLOSED'},
            {'name':'Reflexed Roses - Red','status':'COMPLETED'},
        ]
        scoped=h.campaigns_in_scope(gifts)
        self.assertEqual([(x['name'],x['status']) for x in scoped],[
            ('Reflexed Roses - Red','ACTIVE'),
            ('Reflexed Roses - White','CLOSED'),
            ('Reflexed Roses - Pastel Pink','CLOSED'),
        ])

    def test_validator_rejects_evidence_quote_not_in_transcript(self):
        h=load_module()
        collection={'run_id':'r1','candidates':[{
            'gift_id':'g1','wave_uid':'w1','status':'SHORTLISTED',
            'transcript':'Creator: I am Melbourne based and happy to create a Reel.',
            'thread_sha256':'abc','selected_this_week':3,'weekly_cap':3
        }]}
        decisions={'run_id':'r1','decisions':[{
            'gift_id':'g1','wave_uid':'w1','classification':'fully_qualified',
            'confidence':'high','reason':'all gates confirmed','action':'approved_reserve',
            'facts':{'delivery_eligible':True,'reel_confirmed':True,'brief_confirmed':True},
            'fact_evidence':{
                'delivery_eligible':'I am Sydney based',
                'reel_confirmed':'happy to create a Reel',
                'brief_confirmed':'happy to create a Reel'
            },'reply_text':None
        }]}
        result=h.validate_decision_bundle(collection,decisions)
        self.assertFalse(result['ok'])
        self.assertIn('evidence_quote_not_in_transcript:delivery_eligible',result['errors'][0]['errors'])

    def test_validator_blocks_sensitive_creator_reply(self):
        h=load_module()
        transcript='Creator: Can I send my address?'
        collection={'run_id':'r2','candidates':[{
            'gift_id':'g2','wave_uid':'w2','status':'SHORTLISTED',
            'transcript':transcript,'thread_sha256':h.sha256_text(transcript),
            'selected_this_week':0,'weekly_cap':3
        }]}
        decisions={'run_id':'r2','decisions':[{
            'gift_id':'g2','wave_uid':'w2','classification':'answerable_question',
            'confidence':'high','reason':'ask for detailed delivery information',
            'action':'send_message','facts':{},
            'fact_evidence':{'question':'Can I send my address?'},
            'reply_text':'Please send your full street address and unit number.'
        }]}
        result=h.validate_decision_bundle(collection,decisions)
        self.assertFalse(result['ok'])
        self.assertIn('reply_blocked:asks_for_detailed_address',result['errors'][0]['errors'])

    def test_candidate_builder_preserves_ordered_thread_without_keyword_classification(self):
        h=load_module()
        messages=[
            {'created_at':'2026-07-09T14:01:47Z','is_brand':True,'raw_text':'Please confirm an IG Reel and that the brief feels natural.'},
            {'created_at':'2026-07-09T22:17:11Z','is_creator':True,'raw_text':'Yes of course!'},
            {'created_at':'2026-07-09T22:17:55Z','is_creator':True,'raw_text':'I will style the roses in a vase.'},
        ]
        candidate=h.build_candidate('gift','wave','Campaign','SHORTLISTED','@creator',messages,2,3)
        self.assertLess(candidate['transcript'].index('Yes of course!'),candidate['transcript'].index('style the roses'))
        self.assertNotIn('classification',candidate)
        self.assertEqual(candidate['thread_sha256'],h.sha256_text(candidate['transcript']))

    def test_live_preflight_blocks_changed_thread(self):
        h=load_module()
        result=h.live_preflight({'thread_sha256':h.sha256_text('old thread')},'new creator message')
        self.assertFalse(result['ok'])
        self.assertEqual(result['reason'],'thread_changed_since_llm_review')

    def test_manual_review_requires_specific_question(self):
        h=load_module()
        collection={'run_id':'r3','candidates':[{'gift_id':'g3','wave_uid':'w3','transcript':'Creator: Maybe.','thread_sha256':h.sha256_text('Creator: Maybe.')} ]}
        decisions={'run_id':'r3','decisions':[{'gift_id':'g3','wave_uid':'w3','classification':'ambiguous','confidence':'medium','reason':'mixed signal','action':'manual_review','facts':{},'fact_evidence':{},'manual_question':''}]}
        result=h.validate_decision_bundle(collection,decisions)
        self.assertFalse(result['ok'])
        self.assertIn('manual_question_required',result['errors'][0]['errors'])

    def test_select_is_downgraded_to_reserve_when_campaign_cap_is_full(self):
        h=load_module()
        decision={'action':'select_accept'}
        candidate={'selected_this_week':2,'weekly_cap':2,'selection_window_open':True}
        self.assertEqual(h.effective_action(decision,candidate),'approved_reserve')

    def test_select_is_downgraded_outside_weekly_release_window(self):
        h=load_module()
        decision={'action':'select_accept'}
        candidate={'selected_this_week':0,'weekly_cap':2,'selection_window_open':False}
        self.assertEqual(h.effective_action(decision,candidate),'approved_reserve')

    def test_pending_human_approval_cannot_be_silently_ignored(self):
        h=load_module()
        transcript='[t] Creator: Yes, I can do a Reel in Melbourne.'
        collection={'run_id':'r4','candidates':[{'gift_id':'g4','wave_uid':'w4','candidate_type':'shortlisted_qualification','transcript':transcript,'thread_sha256':h.sha256_text(transcript),'pending_human_commands':[{'comment_id':'cmd1','type':'approve'}]}]}
        decisions={'run_id':'r4','decisions':[{'gift_id':'g4','wave_uid':'w4','classification':'qualified','confidence':'high','reason':'qualified','action':'no_action','facts':{},'fact_evidence':{},'human_command_id':'cmd1'}]}
        result=h.validate_decision_bundle(collection,decisions)
        self.assertFalse(result['ok'])
        self.assertIn('approve_command_not_reflected_in_action',result['errors'][0]['errors'])

    def test_sync_card_resolution_uses_cached_trello_card_id(self):
        h=load_module()
        class Fake:
            def find_trello_card(self,ctx,title,uid,handle,campaign):
                return {'id':'card123','url':'https://trello.com/c/test'}
        resolved=h._resolve_synced_card(Fake(),{'cards':[]},{'card':{'url':'https://fallback'}},'title','wave','creator','campaign')
        self.assertEqual(resolved,{'id':'card123','url':'https://trello.com/c/test','idList':None})

    def test_human_approved_alternative_deliverable_satisfies_output_gate(self):
        h=load_module()
        transcript='Creator: Sydney. Carousel plus Stories?\nFig & Bloom: Yes, carousel plus Stories works for this campaign.'
        collection={'run_id':'r5','candidates':[{'gift_id':'g5','wave_uid':'w5','candidate_type':'shortlisted_qualification','transcript':transcript,'thread_sha256':h.sha256_text(transcript),'pending_human_commands':[]}]}
        decisions={'run_id':'r5','decisions':[{'gift_id':'g5','wave_uid':'w5','classification':'qualified_reserve','confidence':'high','reason':'Daniel approved the format exception','action':'approved_reserve','facts':{'delivery_eligible':True,'reel_confirmed':False,'brief_confirmed':True,'deliverable_exception_approved':True},'fact_evidence':{'delivery_eligible':'Sydney','brief_confirmed':'Carousel plus Stories?','deliverable_exception_approved':'Yes, carousel plus Stories works for this campaign.'},'reply_text':'You are approved in our queue. No gifting date is confirmed yet; we will message when a weekly slot opens.'}]}
        result=h.validate_decision_bundle(collection,decisions)
        self.assertTrue(result['ok'],result['errors'])

    def test_confirmed_photo_deliverable_satisfies_output_gate(self):
        h=load_module()
        transcript='Creator: I am in Melbourne, the brief feels natural, and I am happy to provide around five aesthetic high-resolution photographs.'
        collection={'run_id':'r-photo','candidates':[{'gift_id':'g-photo','wave_uid':'w-photo','candidate_type':'shortlisted_qualification','transcript':transcript,'thread_sha256':h.sha256_text(transcript),'pending_human_commands':[]}]}
        decisions={'run_id':'r-photo','decisions':[{'gift_id':'g-photo','wave_uid':'w-photo','classification':'qualified_reserve','confidence':'high','reason':'The creator confirmed delivery, the brief and the new photo deliverable.','action':'approved_reserve','facts':{'delivery_eligible':True,'deliverable_confirmed':True,'brief_confirmed':True},'fact_evidence':{'delivery_eligible':'I am in Melbourne','deliverable_confirmed':'happy to provide around five aesthetic high-resolution photographs','brief_confirmed':'the brief feels natural'},'reply_text':'You are approved in our queue. We will message you when a gifting slot opens.'}]}
        result=h.validate_decision_bundle(collection,decisions)
        self.assertTrue(result['ok'],result['errors'])

    def test_new_reserve_requires_transparent_queue_notification(self):
        h=load_module()
        transcript='Creator: I am in Sydney, accept the brief, and will create a Reel.'
        collection={'run_id':'r6','candidates':[{'gift_id':'g6','wave_uid':'w6','candidate_type':'shortlisted_qualification','transcript':transcript,'thread_sha256':h.sha256_text(transcript),'pending_human_commands':[]}]}
        decision={'gift_id':'g6','wave_uid':'w6','classification':'qualified_reserve','confidence':'high','reason':'qualified while cadence is closed','action':'approved_reserve','facts':{'delivery_eligible':True,'reel_confirmed':True,'brief_confirmed':True},'fact_evidence':{'delivery_eligible':'I am in Sydney','reel_confirmed':'will create a Reel','brief_confirmed':'accept the brief'},'reply_text':None}
        result=h.validate_decision_bundle(collection,{'run_id':'r6','decisions':[decision]})
        self.assertFalse(result['ok'])
        self.assertIn('reserve_notification_required',result['errors'][0]['errors'])

    def test_existing_reserve_notification_is_not_repeated(self):
        h=load_module()
        transcript='Creator: Sydney, brief accepted, Reel confirmed.\nFig & Bloom: You are approved in our queue; we will message when a weekly slot opens.'
        collection={'run_id':'r7','candidates':[{'gift_id':'g7','wave_uid':'w7','candidate_type':'shortlisted_qualification','transcript':transcript,'thread_sha256':h.sha256_text(transcript),'pending_human_commands':[]}]}
        decision={'gift_id':'g7','wave_uid':'w7','classification':'qualified_reserve','confidence':'high','reason':'remain in reserve','action':'approved_reserve','facts':{'delivery_eligible':True,'reel_confirmed':True,'brief_confirmed':True},'fact_evidence':{'delivery_eligible':'Sydney','reel_confirmed':'Reel confirmed','brief_confirmed':'brief accepted'},'reply_text':None}
        result=h.validate_decision_bundle(collection,{'run_id':'r7','decisions':[decision]})
        self.assertTrue(result['ok'],result['errors'])


if __name__=='__main__': unittest.main()
