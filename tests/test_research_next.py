import datetime as dt
import json
import pathlib
import sys
import unittest
import tempfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from validation import check_quote,issuer_reference
from scoring import score
from reconstruct import inputs_at,reconstruct_point
from evaluation import add_months,outcome,rank_ic,summarize,sample,build as evaluate
from monitor_reports import parse_feed,review_rows

class QualityTests(unittest.TestCase):
 def quote(self):return {'ticker':'BRK.B','yahoo':'BRK-B','currency':'USD','price':532,'status':'cached','marketDate':'2026-10-16','fundamentals':{'status':'fresh','quoteCurrency':'USD','financialCurrency':'USD','bookValue':522000,'priceToBook':.001019}}
 def test_berkshire_class_mismatch_never_silently_scaled(self):
  q=self.quote();v=check_quote(q);self.assertTrue(v['valuationBlocked']);q['validation']=v
  self.assertIsNone(score(q,[],q['fundamentals'],{})['parts']['valuation']);self.assertEqual(q['fundamentals']['bookValue'],522000)
 def test_book_ratio_mismatch_and_currency_block(self):
  q=self.quote();q['ticker']='JPM';q['fundamentals'].update(bookValue=100,priceToBook=1)
  self.assertTrue(check_quote(q)['valuationBlocked']);q['fundamentals']['priceToBook']=5.32;self.assertFalse(check_quote(q)['valuationBlocked'])
  q['fundamentals']['financialCurrency']='EUR';self.assertTrue(check_quote(q)['valuationBlocked'])
 def test_split_jump_blocks_only_risk(self):
  q={'ticker':'MSFT','status':'cached','currency':'USD','price':100,'peTTM':20,'fundamentals':{'quoteCurrency':'USD','financialCurrency':'USD','trailingEps':5}}
  q['validation']=check_quote(q,history=[{'date':'2026-01-01','adjustedClose':100},{'date':'2026-01-02','adjustedClose':10}])
  self.assertIn('risk',q['validation']['blockedCategories']);self.assertFalse(q['validation']['valuationBlocked'])
 def test_original_reports_confirm_only_matching_eps_period(self):
  q={'ticker':'AAPL','currency':'USD','price':100,'peTTM':20,'fundamentals':{'trailingEps':5,'quoteCurrency':'USD','financialCurrency':'USD','reportDate':'2026-06-30'}}
  ref={'eps':{'value':5,'periodEnd':'2026-06-30'},'currency':'USD','url':'https://issuer.test/report','reports':[]}
  self.assertTrue(check_quote(q,issuer=ref)['independentEPSConfirmed']);q['fundamentals']['reportDate']='2026-09-30';self.assertFalse(check_quote(q,issuer=ref)['independentEPSConfirmed'])

class PeriodTests(unittest.TestCase):
 def test_half_year_ttm_uses_only_available_annual_and_half(self):
  def row(end,pub,months,rev,op,prior):return dict(ticker='MC',kind='operating',currency='EUR',periodEnd=end,publishedAt=pub,periodMonths=months,revenue=rev,revenueYearAgo=prior,operatingIncome=op,growthBasis='half-year-yoy' if months==6 else 'annual-yoy')
  rows=[row('2022-06-30','2022-07-25',6,80,20,70),row('2022-12-31','2023-01-25',12,200,50,180),row('2023-06-30','2023-07-25',6,100,30,80)]
  f,e,u=inputs_at(rows,'MC','2023-07-31');self.assertAlmostEqual(f['operatingMargins'],60/220);self.assertEqual(f['growthBasis'],'half-year-yoy');self.assertIsNone(e);self.assertEqual(len(u),3)
  rows[1]['publishedAt']='2024-01-01';f,_,_=inputs_at(rows,'MC','2023-07-31');self.assertNotIn('operatingMargins',f)
 def test_specialist_profiles_do_not_use_operating_proxies(self):
  row=dict(ticker='ARCC',sourceUrl='https://issuer.test/report',kind='bdc',currency='USD',periodEnd='2026-06-30',publishedAt='2026-07-29',specialist={'navPerShare':20,'niiQuarterPerShare':.5,'dividendQuarterPerShare':.48,'debtToEquity':1})
  f,e,u=inputs_at([row],'ARCC','2026-07-31');self.assertIsNone(e);self.assertNotIn('operatingMargins',f);self.assertEqual(f['specialist']['raw']['navPerShare'],20)

 def test_specialist_reconstruction_keeps_quote_currency(self):
  row=dict(ticker='ARCC',sourceUrl='https://issuer.test/report',documentSha256='abc',kind='bdc',currency='USD',periodEnd='2026-06-30',publishedAt='2026-07-29',specialist={'navPerShare':20,'niiQuarterPerShare':.5,'dividendQuarterPerShare':.48,'debtToEquity':1})
  point=reconstruct_point({'ticker':'ARCC','name':'Ares','currency':'USD'},[{'date':'2026-07-30','close':20,'adjustedClose':20}],[row],'2026-07-31')
  self.assertIsNotNone(point['parts']['valuation']);self.assertIsNotNone(point['parts']['quality'])

class EvaluationTests(unittest.TestCase):
 def history(self):
  start=dt.date(2022,1,1)
  return [{'date':(start+dt.timedelta(days=i)).isoformat(),'close':999,'adjustedClose':100+i*.1} for i in range(1000)]
 def test_calendar_and_next_close_entry(self):
  self.assertEqual(add_months('2024-08-31',6),'2025-02-28')
  r,error=outcome(self.history(),'2022-01-31',6,'2023-01-01');self.assertIsNone(error);self.assertEqual(r['entryDate'],'2022-02-01');self.assertGreaterEqual(r['exitDate'],'2022-08-01')
 def test_unmatured_or_future_prices_never_create_outcome(self):
  h=self.history();self.assertEqual(outcome(h,'2022-01-31',12,'2022-12-31')[1],'not-mature')
  a=outcome(h,'2022-01-31',6,'2022-09-01');b=outcome(h+[{'date':'2024-01-01','adjustedClose':1}],'2022-01-31',6,'2022-09-01');self.assertEqual(a,b)
 def test_no_unadjusted_close_substitution_and_no_fake_ic(self):
  self.assertEqual(outcome([{'date':'2022-02-01','close':100}],'2022-01-31',6,'2023-01-01')[1],'entry-pending')
  self.assertIsNone(rank_ic([{'score':1,'returnPct':1}]*4))
  self.assertAlmostEqual(rank_ic([{'score':i,'returnPct':i} for i in range(4)]),1)
 def test_profile_and_coverage_cohorts_not_pooled_for_ic(self):
  point={'ticker':'X','date':'2022-01-31','profile':'bdc','coveragePoints':85,'partialPoints':50,'parts':{'valuation':20,'growth':10,'quality':15,'risk':5},'inputs':{'growthBasis':'nav-since-comparison-date','reportEnd':'2021-09-30','specialist':{'navPreviousDate':'2020-12-31'}}}
  row,_=sample(point,self.history(),6,'2023-01-01','retrospective','test-v1');self.assertEqual(row['growthBasis'],'nav-since-comparison-date-9m')
  rs=[{'ticker':str(i),'signalDate':'2022-01-31','score':i*20,'returnPct':i,'coverage':85 if i<2 else 55,'components':'g|q|r','profile':'operating','growthBasis':'quarterly','maxDrawdownPct':-10,'volatilityPct':20} for i in range(4)]
  self.assertEqual(summarize(rs)['rankICCohorts'],0)

 def test_time_partition_purges_boundary_and_observed_stays_unmatured(self):
  with tempfile.TemporaryDirectory() as temp:
   root=pathlib.Path(temp);(root/'data/history').mkdir(parents=True)
   start=dt.date(2021,1,1);history=[{'date':(start+dt.timedelta(days=i)).isoformat(),'adjustedClose':100+i*.01} for i in range(2200)]
   (root/'data/history/X.json').write_text(json.dumps({'data':history}));(root/'data/universe.json').write_text(json.dumps([{'ticker':'X'}]))
   base={'ticker':'X','profile':'operating','coveragePoints':55,'partialPoints':40,'parts':{'growth':20,'quality':15,'risk':5},'inputs':{'growthBasis':'quarterly-yoy'}}
   points=[dict(base,date=d) for d in ['2022-01-31','2023-07-31','2024-01-31']]
   (root/'data/reconstruction.json').write_text(json.dumps({'modelVersion':'test-v1','reportBundleSha256':'abc','stocks':[{'ticker':'X','points':points}]}))
   (root/'data/score-history.json').write_text(json.dumps({'snapshots':[{'date':'2026-10-18','observedAt':'2026-10-18T12:00:00Z','modelVersion':'live-v1','quotes':[base]}]}))
   result=evaluate(root,dt.date(2026,10,18));rows=result['retrospective']['samples']
   self.assertTrue(result['retrospective']['excluded']['purged-development-boundary']>0)
   self.assertTrue(all(r['exitDate']<'2024-01-01' for r in rows if r['partition']=='development'))
   self.assertTrue(all(r['signalDate']>='2024-01-01' for r in rows if r['partition']=='test'))
   self.assertTrue(all(s['modelVersion']=='test-v1' for s in result['retrospective']['summary']))
   self.assertEqual(result['observed']['matureCount'],0)

class MonitorTests(unittest.TestCase):
 def test_future_scheduled_and_external_items_excluded(self):
  feed=b'''<rss><channel><item><title>Reports First Quarter Results</title><link>https://issuer.test/result</link><pubDate>Wed, 29 Apr 2026 10:00:00 GMT</pubDate></item><item><title>Schedules Earnings Release</title><link>https://issuer.test/schedule</link><pubDate>Wed, 29 Apr 2026 10:00:00 GMT</pubDate></item><item><title>Financial Results</title><link>https://evil.test/result</link><pubDate>Wed, 29 Apr 2026 10:00:00 GMT</pubDate></item><item><title>Financial Results</title><link>https://issuer.test/future</link><pubDate>Wed, 29 Apr 2027 10:00:00 GMT</pubDate></item></channel></rss>'''
  hits=parse_feed(feed,'X','https://issuer.test/feed',dt.date(2026,10,18));self.assertEqual(len(hits),1);self.assertEqual(hits[0]['state'],'needs-review')
 def test_provider_advance_is_not_primary_confirmation(self):
  snap={'quotes':[{'ticker':'X','name':'X','fundamentals':{'reportDate':'2026-09-30'}}]};prev={'stocks':[{'ticker':'X','providerPeriodEnd':'2026-06-30'}]}
  row=review_rows(snap,[],{},prev,[])[0];self.assertEqual(row['state'],'new-period');self.assertTrue(row['curationBehind']);self.assertNotIn('primaryConfirmed',row)
if __name__=='__main__':unittest.main()
