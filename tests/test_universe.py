import json
from pathlib import Path
import unittest
from scoring import SPECIAL,score

ROOT=Path(__file__).resolve().parents[1]

class UniverseTests(unittest.TestCase):
 def test_dated_top100_merge_preserves_existing_and_share_classes(self):
  rows=json.loads((ROOT/'data/universe.json').read_text());meta=json.loads((ROOT/'data/sp500-selection.json').read_text())
  self.assertEqual(len(rows),len({r['ticker'] for r in rows}));self.assertEqual(len(rows),meta['totalCount'])
  self.assertEqual(sum(r['originalUniverse'] for r in rows),32)
  selected=sorted([r for r in rows if r.get('sp500Top100')],key=lambda r:r['sp500Top100']['rank'])
  self.assertEqual(len(selected),100);self.assertEqual([r['sp500Top100']['rank'] for r in selected],list(range(1,101)))
  self.assertEqual([r['ticker'] for r in selected],[r['ticker'] for r in meta['holdings']])
  weights=[r['sp500Top100']['weightProxyPct'] for r in selected];self.assertEqual(weights,sorted(weights,reverse=True))
  self.assertTrue(all(r['sp500Top100']['asOf']==meta['asOf'] for r in selected))
  for ticker in ('GOOG','GOOGL','BRK.B'):self.assertIn(ticker,{r['ticker'] for r in selected})
  self.assertEqual(next(r for r in rows if r['ticker']=='BRK.B')['yahoo'],'BRK-B')
  self.assertEqual(next(r for r in rows if r['ticker']=='G')['yahoo'],'G.MI')
 def test_new_specialists_do_not_receive_operating_model_points(self):
  for ticker in ['BAC','WFC','C','GS','MS','AXP','COF','SCHW','PGR','CB','WELL','PLD']:
   with self.subTest(ticker=ticker):
    result=score({'ticker':ticker,'status':'cached','peTTM':5},[],{'status':'fresh','revenueGrowth':1,'operatingMargins':1},{})
    self.assertIsNone(result['parts']['valuation']);self.assertIsNone(result['parts']['growth']);self.assertIsNone(result['parts']['quality'])
    self.assertNotEqual(result['profile'],'operating')

if __name__=='__main__':unittest.main()
