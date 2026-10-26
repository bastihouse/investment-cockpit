import datetime as dt,json,unittest
from pathlib import Path
from tools.collect_stoxx_universe import select
from update_data import normalize_prices
from scoring import SPECIAL,score
ROOT=Path(__file__).resolve().parents[1]
class EuropeTests(unittest.TestCase):
 def test_dated_selection_exact_listings_and_overlap(self):
  meta=json.loads((ROOT/'data/stoxx600-selection.json').read_text());u=json.loads((ROOT/'data/universe.json').read_text());selected=[r for r in u if r.get('stoxx600Top100')]
  self.assertEqual(len(selected),100);self.assertEqual(len({r['yahoo'] for r in u}),len(u));self.assertEqual(len(u),meta['totalCount'])
  self.assertEqual(sorted(r['stoxx600Top100']['rank'] for r in selected),list(range(1,101)))
  self.assertIn('SAN.MC',{r['ticker'] for r in selected});self.assertIn('SAN.PA',{r['ticker'] for r in selected})
  self.assertTrue({'UL','ULVR.L','SHEL','SHELL.AS'}.issubset({r['ticker'] for r in u}))
  self.assertEqual(next(r['currency'] for r in u if r['ticker']=='HSBA.L'),'GBP')
  day=dt.date.fromisoformat(meta['asOf']);self.assertEqual(len(select((ROOT/'data/stoxx600-holdings.csv').read_bytes(),day)[1]),100)
  with self.assertRaises(ValueError):select((ROOT/'data/stoxx600-holdings.csv').read_bytes(),day+dt.timedelta(days=11))
 def test_pence_are_normalized_without_mutating_input(self):
  rows=[{'date':'2026-10-23','close':1234,'adjustedClose':1200}];out,c=normalize_prices(rows,'GBp')
  self.assertEqual((c,out[0]['close'],out[0]['adjustedClose']),('GBP',12.34,12));self.assertEqual(rows[0]['close'],1234)
  self.assertEqual(normalize_prices(rows,'GBP'),(rows,'GBP'))
 def test_european_financials_never_get_operating_model(self):
  for ticker in ['HSBA.L','SAN.MC','UBSG.SW','ZURN.SW','CS.PA','INVE-B.ST']:
   r=score({'ticker':ticker,'status':'cached','peTTM':5},[],{'status':'fresh','revenueGrowth':1,'operatingMargins':1},{})
   self.assertNotEqual(r['profile'],'operating');self.assertIsNone(r['parts']['quality'])
if __name__=='__main__':unittest.main()

class PrimaryStatementTests(unittest.TestCase):
 def check(self,months=3,end='2026-06-30',currency='EUR',growth=.12,margin=.2):
  from validation import check_quote
  q={'ticker':'SAP.DE','sector':'operating','currency':'EUR','fundamentals':{'status':'fresh','reportDate':'2026-06-30','financialCurrency':'EUR','revenueGrowth':growth,'operatingMargins':margin}}
  source={'facts':{'status':'fresh','reportDate':end,'growthPeriodMonths':months,'revenueGrowth':.12,'operatingMargins':.2},'currency':currency,'url':'https://www.sec.gov/example','reports':[]}
  return check_quote(q,issuer=source)
 def test_only_matching_definition_period_currency_confirmed(self):
  self.assertEqual(self.check()['independentFundamentalChecks'],2)
  self.assertEqual(self.check(months=6)['independentFundamentalChecks'],1)
  self.assertEqual(self.check(end='2025-12-31')['independentFundamentalChecks'],0)
  self.assertEqual(self.check(currency='USD')['independentFundamentalChecks'],0)
  r=self.check(growth=.5);self.assertEqual(r['independentFundamentalChecks'],1);self.assertFalse(r['independentEPSConfirmed']);self.assertNotIn('growth',r['blockedCategories'])

class FiledEuropeHistoryTests(unittest.TestCase):
 def test_first_publication_and_matching_operands(self):
  import sys
  sys.path.insert(0,str(ROOT/'tools'))
  from collect_europe_history import extract
  rows=[{'start':'2024-01-01','end':'2024-12-31','filed':'2025-03-01','accn':'0000000001-25-000001','form':'20-F','val':120},
        {'start':'2023-01-01','end':'2023-12-31','filed':'2025-03-01','accn':'0000000001-25-000001','form':'20-F','val':100},
        {'start':'2024-01-01','end':'2024-12-31','filed':'2026-03-01','accn':'0000000001-26-000001','form':'20-F','val':999}]
  p={'cik':1,'facts':{'ifrs-full':{'Revenue':{'units':{'EUR':rows}},'ProfitLossFromOperatingActivities':{'units':{'EUR':[{**rows[0],'val':20}]}}}}}
  out=extract(p,'SAP.DE','EUR',dt.date(2026,10,26),'hash');self.assertEqual(len(out),1)
  self.assertEqual(out[0]['publishedAt'],'2025-03-01');self.assertEqual(out[0]['revenue'],.00012)
  self.assertEqual(out[0]['operatingIncome'],.00002);self.assertIsNone(out[0]['epsDiluted']);self.assertFalse(out[0]['priceBasisVerified'])
  self.assertEqual(extract(p,'SAP.DE','USD',dt.date(2026,10,26),'hash'),[])
  rows.append({**rows[0],'val':121});self.assertEqual(extract(p,'SAP.DE','EUR',dt.date(2026,10,26),'hash'),[])
