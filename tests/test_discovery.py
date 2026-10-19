import copy
import datetime as dt
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from discovery import gaps,peer_cohorts,drawdown,observed_change,signals
from historical_sources import load_reports
from scoring import WEIGHTS
from reconstruct import inputs_at

TODAY=dt.date(2026,10,19)
def quote(ticker='X'):
 return {'ticker':ticker,'sector':'operating','status':'cached','price':90,'peTTM':18,'marketDate':'2026-10-16','currency':'USD',
         'fundamentals':{'status':'fresh','fetchedAt':'2026-10-19T12:00:00+00:00','reportDate':'2026-06-30','quoteCurrency':'USD','financialCurrency':'USD','trailingEps':5},
         'validation':{'blockedCategories':{}},'researchScore':{'modelVersion':'m1','weights':WEIGHTS,'parts':{k:10 for k in WEIGHTS},'coveragePoints':100,'complete':True,'total':50}}

class DiscoveryTests(unittest.TestCase):
 def test_blocked_weight_is_not_double_counted_or_potential_gain(self):
  q=quote();q['researchScore']['parts']['valuation']=None;q['validation']['blockedCategories']={'valuation':['currency']}
  result=gaps(q,{'reportCount':0},{},TODAY)
  self.assertEqual(result['missingWeight'],30);self.assertEqual(result['blockedWeight'],30);self.assertEqual(result['priority'],1)
  self.assertNotIn('potentialGain',result);self.assertTrue(result['historyMissing'])
 def test_observed_change_requires_same_model_coverage_and_prior_date(self):
  q=quote();q['researchScore']['total']=60;old=copy.deepcopy(q);old['researchScore']['total']=50;old['fundamentals']['fetchedAt']='2026-10-18T12:00:00+00:00';old['peTTM']=20;old['price']=100
  a=observed_change(q,old,'m1','m1',TODAY,'2026-10-18');self.assertEqual(a['scoreDelta'],10);self.assertAlmostEqual(a['peChangePct'],-10)
  self.assertIsNone(observed_change(q,old,'m2','m1',TODAY,'2026-10-18')['scoreDelta'])
  self.assertIsNone(observed_change(q,old,'m1','m1',TODAY,'2026-10-19')['scoreDelta'])
  old['researchScore']['complete']=False;self.assertIsNone(observed_change(q,old,'m1','m1',TODAY,'2026-10-18')['scoreDelta'])
  old['fundamentals']['trailingEps']=4;self.assertIsNone(observed_change(q,old,'m1','m1',TODAY,'2026-10-18')['peChangePct'])
 def test_split_like_basis_change_cannot_create_improvement_signal(self):
  q=quote();old=copy.deepcopy(q);old['fundamentals']['fetchedAt']='2026-10-18T12:00:00+00:00'
  old['price']=900;old['peTTM']=180;old['researchScore']['total']=30
  result=observed_change(q,old,'m1','m1',TODAY,'2026-10-18');self.assertIsNone(result['scoreDelta']);self.assertIsNone(result['peChangePct'])
 def test_price_signal_excludes_future_prices_short_history_and_bad_basis(self):
  start=dt.date(2026,1,1);history=[{'date':(start+dt.timedelta(days=i)).isoformat(),'adjustedClose':100 if i<288 else 70} for i in range(289)]
  q=quote();history[-1]['date']=q['marketDate'];a=drawdown(history,q,TODAY);self.assertAlmostEqual(a['pct'],-30)
  self.assertEqual(a,drawdown(history+[{'date':'2027-01-01','adjustedClose':1}],q,TODAY))
  self.assertIsNone(drawdown(history[:100],q,TODAY));q['validation']['blockedCategories']={'risk':['split']};self.assertIsNone(drawdown(history,q,TODAY))
 def test_peer_cohorts_separate_profiles_coverage_and_deduplicate_share_classes(self):
  def row(ticker,issuer,profile='operating',coverage=100):
   return dict(ticker=ticker,issuerKey=issuer,currentFresh=True,industry='Semiconductors',profile=profile,coverage=coverage,componentSet='all' if coverage==100 else 'partial',modelVersion='m1',weights=WEIGHTS,valuationValue=20,valuationKey='peTTM',total=50,partialPoints=50)
  groups=peer_cohorts([row('GOOG','GOOGL'),row('GOOGL','GOOGL'),row('A','A'),row('B','B'),row('C','C'),row('BANK','BANK','bank'),row('PART','PART',coverage=85)])
  main=next(g for g in groups if g['size']==5);self.assertEqual(main['issuers'],4);self.assertIsNone(main['valuationMedian']);self.assertEqual(len(groups),3)
  groups=peer_cohorts([row(str(i),str(i)) for i in range(5)]);self.assertEqual(groups[0]['valuationMedian'],20)
 def test_scanner_requires_valid_baseline_and_does_not_invent_signals(self):
  row={'currentFresh':True,'observedChange':{'scoreDelta':None,'peChangePct':None},'parts':{'growth':20,'quality':15},'valuationValue':10,'drawdown':None}
  self.assertEqual(signals(row,{'valuationMedian':None}),[])
  found=signals(row,{'valuationMedian':20,'valuationCount':5});self.assertEqual([s['kind'] for s in found],['peer-value'])
  row['currentFresh']=False;self.assertEqual(signals(row,{'valuationMedian':20,'valuationCount':5}),[])

class SecSourceTests(unittest.TestCase):
 def test_sec_periods_preserve_filing_cutoffs_and_q4_arithmetic(self):
  root=Path(__file__).resolve().parents[1];rows,hashes,_=load_reports(root);rows=[r for r in rows if r.get('sourceType')=='SEC Companyfacts / filed XBRL']
  self.assertTrue(rows);self.assertEqual(len(rows),len({(r['ticker'],r['periodEnd'],r['periodMonths']) for r in rows}))
  self.assertTrue(any(p.startswith('historical-sec/') for p in hashes))
  for r in rows:
   self.assertLess(r['periodEnd'],r['publishedAt']);self.assertTrue(all(x['filed']<=r['publishedAt'] for x in r['sourceInputs']));self.assertFalse(r['priceBasisVerified']);self.assertIsNone(r['epsDiluted'])
   if r.get('derivation'):
    a,b,c,d=r['sourceInputs'][:4];key='netIncome' if 'netIncome' in r else 'revenue'
    self.assertAlmostEqual(r[key],(a['val']-b['val'])/1e6);self.assertAlmostEqual(r[key+'YearAgo'],(c['val']-d['val'])/1e6)
    self.assertEqual(a['tag'],b['tag']);self.assertEqual(a['tag'],c['tag']);self.assertEqual(c['tag'],d['tag'])
  sample=next(r for r in rows if r['ticker']=='AVGO' and r['periodEnd']=='2021-01-31')
  self.assertEqual((sample['revenue'],sample['revenueYearAgo'],sample['operatingIncome']),(6655,5858,1837))
  self.assertEqual(inputs_at([sample],'AVGO',sample['publishedAt'])[0]['status'],'missing')
  holding=[r for r in rows if r['ticker']=='BRK.B'];facts,eps,_=inputs_at(holding,'BRK.B','2026-06-30');self.assertIsNone(eps);self.assertIsNone(facts.get('bookValuePerShare'))

if __name__=='__main__':unittest.main()
