import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scoring import score

class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.quote={'ticker':'MSFT','status':'cached','peTTM':10}
        self.history=[{'date':str(i),'close':100+i*.01,'adjustedClose':100+i*.01} for i in range(253)]
        self.facts={'status':'fresh','revenueGrowth':.25,'operatingMargins':.30}
        self.revision={'status':'fresh','current':11,'30daysAgo':10,'numberOfAnalysts':3}
    def test_full_evidence_can_reach_100(self):
        s=score(self.quote,self.history,self.facts,self.revision)
        self.assertEqual(s['coveragePoints'],100)
        self.assertEqual(s['total'],100)
    def test_missing_is_not_renormalized(self):
        s=score(self.quote,self.history,self.facts,{})
        self.assertEqual(s['coveragePoints'],85)
        self.assertEqual(s['partialPoints'],85)
        self.assertIsNone(s['total'])
        self.assertFalse(s['complete'])
    def test_special_profiles_do_not_use_operating_model(self):
        q={**self.quote,'ticker':'JPM'}
        s=score(q,self.history,self.facts,self.revision)
        self.assertEqual(s['coveragePoints'],10)
        self.assertIsNone(s['parts']['valuation'])
    def test_stale_inputs_cannot_get_fundamental_points(self):
        s=score(self.quote,self.history,{**self.facts,'status':'stale'},self.revision)
        self.assertEqual(s['coveragePoints'],10)
        s=score({**self.quote,'status':'stale'},self.history,self.facts,self.revision)
        self.assertEqual(s['coveragePoints'],0)
    def test_losses_and_invalid_analyst_base_stay_open(self):
        s=score({**self.quote,'peTTM':-8},self.history,self.facts,{**self.revision,'30daysAgo':-1})
        self.assertIsNone(s['parts']['valuation'])
        self.assertIsNone(s['parts']['revisions'])
    def test_adjusted_series_prevents_split_spike(self):
        history=[{**p,'close':p['close']*(10 if i<150 else 1)} for i,p in enumerate(self.history)]
        self.assertEqual(score(self.quote,history,self.facts,{})['parts']['risk'],10)
    def test_missing_adjusted_history_does_not_score_risk(self):
        h=[{'close':100} for _ in range(253)]
        self.assertIsNone(score(self.quote,h,self.facts,{})['parts']['risk'])

if __name__=='__main__': unittest.main()
