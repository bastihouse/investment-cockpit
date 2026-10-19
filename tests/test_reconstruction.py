import datetime as dt
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from reconstruct import month_ends,inputs_at,reconstruct_point

def report(end,published,eps=2):
 return dict(ticker='MSFT',currency='USD',periodEnd=end,publishedAt=published,revenue=100,revenueYearAgo=80,operatingIncome=30,epsDiluted=eps,sourceUrl='https://example.test/report',documentSha256='abc',priceBasis='No stock split after 2020')
class ReconstructionTests(unittest.TestCase):
 def test_new_original_gap_sources_and_annual_insurance_basis(self):
  import json
  rows=json.loads((pathlib.Path(__file__).resolve().parents[1]/'data/historical-extensions.json').read_text())['reports']
  for year,rev,prior,op in [(2022,36729,28665,10127),(2024,41677,42240,10624)]:
   row=next(r for r in rows if r['ticker']=='MC' and r['periodEnd']==f'{year}-06-30')
   self.assertEqual((row['revenue'],row['revenueYearAgo'],row['operatingIncome']),(rev,prior,op))
   self.assertFalse(row['priceBasisVerified']);self.assertEqual(row['periodMonths'],6)
  row=next(r for r in rows if r['ticker']=='G' and r['periodEnd']=='2025-12-31')
  self.assertEqual((row['netIncome'],row['netIncomeYearAgo']),(4172,3724))
  self.assertEqual(inputs_at([row],'G',row['publishedAt'])[0]['status'],'missing')
  f,eps,_=inputs_at([row],'G','2026-03-31')
  self.assertEqual(f['growthPeriodMonths'],12);self.assertEqual(f['growthBasis'],'annual-shareholder-net-income-yoy')
  self.assertAlmostEqual(f['earningsGrowth'],4172/3724-1);self.assertIsNone(eps);self.assertIsNone(f['returnOnEquity'])
 def test_month_ends_exclude_incomplete_month(self):
  values=month_ends(dt.date(2026,10,17));self.assertEqual(len(values),60);self.assertEqual(values[0],'2021-10-31');self.assertEqual(values[-1],'2026-09-30')
  self.assertEqual(month_ends(dt.date(2024,3,1),1),['2024-02-29'])
 def test_release_on_cutoff_not_usable_or_future_leak(self):
  r=report('2023-06-30','2023-07-25')
  self.assertEqual(inputs_at([r],'MSFT','2023-07-25')[0]['status'],'missing')
  self.assertAlmostEqual(inputs_at([r],'MSFT','2023-07-26')[0]['revenueGrowth'],.25)
 def test_no_gap_filled_in_four_quarter_window(self):
  rows=[report('2022-06-30','2022-07-25'),report('2022-12-31','2023-01-25'),report('2023-03-31','2023-04-25'),report('2023-06-30','2023-07-25')]
  f,e,u=inputs_at(rows,'MSFT','2023-07-31');self.assertIsNone(e);self.assertNotIn('operatingMargins',f)
 def test_future_revision_and_stale_reports_do_not_change_past(self):
  a=report('2023-06-30','2023-07-25');b={**a,'publishedAt':'2024-01-01','revenue':200}
  self.assertEqual(inputs_at([a,b],'MSFT','2023-08-31'),inputs_at([a],'MSFT','2023-08-31'))
  self.assertEqual(inputs_at([a],'MSFT','2024-02-29')[0]['status'],'missing')
 def test_weekend_report_after_last_close_excluded(self):
  r=report('2023-06-30','2023-09-30')
  p=reconstruct_point(dict(ticker='MSFT',name='Microsoft',currency='USD'),[dict(date='2023-09-29',close=100,adjustedClose=100)],[r],'2023-09-30')
  self.assertEqual(p['sources'],[]);self.assertIsNone(p['total']);self.assertIsNone(p['parts']['revisions'])
 def test_trailing_window_excludes_future_prices(self):
  start=dt.date(2022,1,1);h=[dict(date=(start+dt.timedelta(days=i)).isoformat(),close=100+i*.01,adjustedClose=100+i*.01) for i in range(300)]
  s=dict(ticker='MSFT',name='Microsoft',currency='USD')
  a=reconstruct_point(s,h,[],'2022-09-30');b=reconstruct_point(s,h+[dict(date='2023-01-01',close=900,adjustedClose=900)],[],'2022-09-30')
  self.assertEqual(a,b);self.assertEqual(a['coveragePoints'],10)

 def test_four_quarters_support_85_percent_without_consensus(self):
  rows=[report('2022-09-30','2022-10-25'),report('2022-12-31','2023-01-25'),report('2023-03-31','2023-04-25'),report('2023-06-30','2023-07-25')]
  start=dt.date(2022,1,1);h=[dict(date=(start+dt.timedelta(days=i)).isoformat(),close=160,adjustedClose=160) for i in range(577)]
  p=reconstruct_point(dict(ticker='MSFT',name='Microsoft',currency='USD'),h,rows,'2023-07-31')
  self.assertEqual(p['coveragePoints'],85);self.assertIsNone(p['total']);self.assertEqual(p['inputs']['peApprox'],20);self.assertEqual(len(p['sources']),4)
 def test_split_adjustment_preserves_raw_eps(self):
  rows=[report('2022-09-30','2022-10-25'),report('2022-12-31','2023-01-25'),report('2023-03-31','2023-04-25'),report('2023-06-30','2023-07-25')]
  for r in rows:r.update(ticker='NVDA',priceBasis='',priceBasisVerified=True,epsToPriceBasisFactor=10)
  self.assertAlmostEqual(inputs_at(rows,'NVDA','2023-07-31')[1],.8)
  self.assertTrue(all(r['epsDiluted']==2 for r in rows))
  rows[0]['priceBasisVerified']=False
  self.assertIsNone(inputs_at(rows,'NVDA','2023-07-31')[1])

 def test_original_release_sample_values_and_latest_coverage(self):
  import json
  rows=json.loads((pathlib.Path(__file__).resolve().parents[1]/'data/historical-reports.json').read_text())['reports']
  samples={('NVDA','2024-04-28'):(26044,16909,5.98),('META','2023-03-31'):(28645,7227,2.20),('AMZN','2023-09-30'):(143083,11188,.94),('GOOGL','2024-03-31'):(80539,25472,1.89)}
  for key,expected in samples.items():
   row=next(r for r in rows if (r['ticker'],r['periodEnd'])==key)
   self.assertEqual((row['revenue'],row['operatingIncome'],row['epsDiluted']),expected)
  for ticker in ['MSFT','AAPL','NVDA','META','AMZN','GOOGL']:
   facts,eps,used=inputs_at(rows,ticker,'2026-09-30')
   self.assertEqual(facts['status'],'fresh');self.assertGreater(eps,0);self.assertEqual(len(used),4)

 def test_source_bundle_has_unique_quarters_and_consistent_values(self):
  import json
  rows=json.loads((pathlib.Path(__file__).resolve().parents[1]/'data/historical-reports.json').read_text())['reports']
  self.assertEqual(len({(r['ticker'],r['periodEnd']) for r in rows}),len(rows))
  for r in rows:
   self.assertGreater(r['revenue'],r['operatingIncome']);self.assertGreater(r['revenueYearAgo'],0)
   self.assertLess(r['periodEnd'],r['publishedAt']);self.assertEqual(len(r['documentSha256']),64)
