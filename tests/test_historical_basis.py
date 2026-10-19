import copy
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from audit_historical_eps import observations,ttm_at
from historical_sources import load_reports
from reconstruct import inputs_at,reconstruct_point

class HistoricalBasisTests(unittest.TestCase):
 def test_ttm_ytd_uses_only_available_operands_and_never_quarter_relabels(self):
  def r(start,end,filed,days,value):return dict(start=start,end=end,filed=filed,days=days,normalized=value)
  rows=[r('2022-01-01','2022-12-31','2023-02-01',364,4),r('2022-01-01','2022-06-30','2022-07-20',180,1.5),r('2023-01-01','2023-06-30','2023-07-20',180,2)]
  value,used,label=ttm_at(rows,'2023-06-30','2023-07-20')
  self.assertEqual(value,4.5);self.assertEqual([r['coefficient'] for r in used],[1,1,-1]);self.assertIn('not a fabricated Q4',label)
  self.assertIsNone(ttm_at(rows,'2023-06-30','2023-07-19')[0])
 def test_conflicting_eps_and_income_share_mismatch_are_withheld(self):
  r=dict(start='2023-01-01',end='2023-03-31',filed='2023-04-20',accn='a',form='10-Q',val=2)
  facts={'EarningsPerShareDiluted':{'units':{'USD/shares':[r]}},'WeightedAverageNumberOfDilutedSharesOutstanding':{'units':{'shares':[dict(r,val=100)]}},'NetIncomeLoss':{'units':{'USD':[dict(r,val=200)]}}}
  p={'facts':{'us-gaap':facts}};self.assertEqual(observations(p,[('2024-01-01',10)],dt.date(2026,10,19))[0]['normalized'],.2)
  facts['NetIncomeLoss']['units']['USD'][0]['val']=100;self.assertEqual(observations(p,[],dt.date(2026,10,19)),[])
  facts['NetIncomeLoss']['units']['USD'][0]['val']=200;facts['EarningsPerShareDiluted']['units']['USD/shares'].append(dict(r,val=3));self.assertEqual(observations(p,[],dt.date(2026,10,19)),[])
 def test_real_overlay_cutoff_split_and_raw_source_are_preserved(self):
  reports,hashes,_=load_reports(ROOT);raw,_,_=load_reports(ROOT,apply_audit=False)
  r=next(r for r in reports if r['ticker']=='AVGO' and r['periodEnd']=='2021-01-31')
  original=next(x for x in raw if x['ticker']=='AVGO' and x['periodEnd']=='2021-01-31')
  self.assertIsNone(original['epsDiluted']);self.assertIsNone(r['epsDiluted']);self.assertTrue(r['epsBasisAudit'])
  self.assertIn('historical-eps-audit.json',hashes);self.assertIsNone(inputs_at([r],'AVGO',r['publishedAt'])[1])
  cutoff=(dt.date.fromisoformat(r['publishedAt'])+dt.timedelta(days=1)).isoformat()
  self.assertIsNotNone(inputs_at([r],'AVGO',cutoff)[1]);late=copy.deepcopy(r);late['epsTtmInputs'][0]['filed']='2030-01-01';self.assertIsNone(inputs_at([late],'AVGO',cutoff)[1])
  stock=dict(ticker='AVGO',name='Broadcom',currency='USD');h=[dict(date=cutoff,close=100,adjustedClose=100)]
  good=reconstruct_point(stock,h,[r],cutoff,[{'tradingDate':'2024-07-15','ratio':10}]);bad=reconstruct_point(stock,h,[r],cutoff,[])
  self.assertIsNotNone(good['parts']['valuation']);self.assertIsNone(bad['parts']['valuation']);self.assertIsNone(good['total'])
 def test_overlay_cannot_attach_to_a_different_source_hash(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();r=dict(ticker='X',periodEnd='2023-03-31',periodMonths=3,publishedAt='2023-04-20',documentSha256='one')
   (root/'data/historical-reports.json').write_text(json.dumps({'reports':[r]}))
   (root/'data/historical-eps-audit.json').write_text(json.dumps({'epsOverlays':[dict(r,documentSha256='two',epsTtmApprox=100)]}))
   self.assertNotIn('epsTtmApprox',load_reports(root)[0][0])
 def test_four_international_instruments_and_predecessor_boundaries(self):
  rows,_,checks=load_reports(ROOT)
  for ticker in ['005930','ACOMO','UL','SHEL']:self.assertTrue(any(r['ticker']==ticker for r in rows))
  samsung=next(r for r in rows if r['ticker']=='005930' and r['periodEnd']=='2024-12-31');self.assertEqual((samsung['revenue'],samsung['revenueYearAgo'],samsung['operatingIncome']),(300870903,258935494,32725961));self.assertEqual(samsung['currency'],'KRW')
  acomo=next(r for r in rows if r['ticker']=='ACOMO' and r['periodEnd']=='2024-12-31');self.assertAlmostEqual(acomo['revenue'],1362.823);self.assertAlmostEqual(acomo['operatingIncome'],79.737)
  ul=next(r for r in rows if r['ticker']=='UL');self.assertEqual(ul['currency'],'EUR');self.assertIsNone(ul['epsDiluted'])
  for r in rows:
   if r.get('entityContinuity'):self.assertLess(r['publishedAt'],r['entityContinuity']['effectiveDate']);self.assertEqual(r['entityContinuity']['exchangeRatio'],1)
  self.assertTrue(any(r.get('entityContinuity') and r['ticker']=='XOM' for r in rows));self.assertFalse(any(r.get('entityContinuity') and r['ticker'] in ['GEV','SNDK'] for r in rows))

if __name__=='__main__':unittest.main()
