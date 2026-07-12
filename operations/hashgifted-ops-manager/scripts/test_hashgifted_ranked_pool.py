import importlib.util
import unittest
from pathlib import Path

PATH=str(Path(__file__).with_name('hashgifted_ranked_pool.py'))

def load():
    s=importlib.util.spec_from_file_location('ranked',PATH); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

class RankedPoolTests(unittest.TestCase):
    def test_approved_score_weights_and_neutral_reliability(self):
        m=load(); s=m.score_candidate('Strong','Excellent',None,10)
        self.assertEqual(s,{'brand_fit':40,'content_reusability':30,'reliability':10,'application_age':10,'total':90})

    def test_hashgifted_reliability_is_scaled_to_twenty(self):
        m=load(); s=m.score_candidate('Good','Good',85,5)
        self.assertEqual(s['reliability'],17)
        self.assertEqual(s['total'],80)

    def test_queue_has_two_locked_twelve_planned_and_three_alternates(self):
        m=load(); rows=[]
        for i in range(20):
            rows.append({'campaign':'C','wave_uid':str(i),'handle':f'h{i}','hashgifted_rank':i,'score':{'total':100-i,'brand_fit':40},'exception':False})
        a=m.queue_assignments(rows)
        states=[a[('C',str(i))]['queue_state'] for i in range(20)]
        self.assertEqual(states[:2],['locked_next_week']*2)
        self.assertEqual(states[2:12],['planned']*10)
        self.assertEqual(states[12:15],['alternate']*3)
        self.assertEqual(states[15:],['parked']*5)

    def test_exception_and_active_gift_are_not_ranked(self):
        m=load(); rows=[
          {'campaign':'C','wave_uid':'1','handle':'safe','hashgifted_rank':1,'score':{'total':80,'brand_fit':34},'exception':False},
          {'campaign':'C','wave_uid':'2','handle':'risk','hashgifted_rank':2,'score':{'total':90,'brand_fit':40},'exception':True},
          {'campaign':'C','wave_uid':'3','handle':'active','hashgifted_rank':3,'score':{'total':95,'brand_fit':40},'exception':False},
        ]
        a=m.queue_assignments(rows,{'active'})
        self.assertIn(('C','1'),a); self.assertNotIn(('C','2'),a); self.assertNotIn(('C','3'),a)

if __name__=='__main__': unittest.main()
