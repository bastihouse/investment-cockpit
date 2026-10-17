import copy
import datetime as dt
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from archive import record_snapshot
from validation import check_quote, reported_eps
from scoring import score

class EvidenceTests(unittest.TestCase):
    def test_daily_archive_is_immutable_and_versioned(self):
        with tempfile.TemporaryDirectory() as d:
            q={'ticker':'X','name':'X','researchScore':{'complete':True,'total':60,'coveragePoints':100,'parts':{}}}
            snap={'generatedAt':'2026-10-17T20:00:00+00:00','scoreModelVersion':'research-v7.2.0','quotes':[q]}
            self.assertTrue(record_snapshot(d,snap))
            snap['quotes'][0]['researchScore']['total']=90
            self.assertFalse(record_snapshot(d,snap))
            index=json.loads((Path(d)/'data/score-history.json').read_text())
            entry=index['snapshots'][0]
            self.assertEqual(entry['quotes'][0]['total'],60)
            self.assertEqual(entry['sha256'],hashlib.sha256((Path(d)/entry['path']).read_bytes()).hexdigest())
            snap['scoreModelVersion']='research-v7.3.0'
            self.assertTrue(record_snapshot(d,snap))
            self.assertEqual(len(json.loads((Path(d)/'data/score-history.json').read_text())['snapshots']),2)
    def test_vienna_date_and_no_fictional_archive(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(record_snapshot(d,{'generatedAt':None,'quotes':[]}))
            s={'generatedAt':'2026-10-17T23:15:00Z','scoreModelVersion':'research-v7.2.0','quotes':[{'ticker':'X','name':'X'}]}
            record_snapshot(d,s)
            j=json.loads((Path(d)/'data/score-history.json').read_text())
            self.assertEqual(j['snapshots'][0]['date'],'2026-10-18')
    def test_same_provider_does_not_claim_independence(self):
        q={'price':100,'peTTM':20,'marketDate':'2026-10-16','currency':'USD','fundamentals':{'providerPrice':100,'providerPriceDate':'2026-10-16','trailingEps':5,'quoteCurrency':'USD','financialCurrency':'USD'}}
        c=check_quote(q)
        self.assertEqual(c['state'],'consistent')
        self.assertFalse(c['independentEPSConfirmed'])
        q['peTTM']=40
        self.assertTrue(check_quote(q)['valuationBlocked'])
    def test_different_report_periods_do_not_pass_sec_check(self):
        q={'currency':'USD','fundamentals':{'trailingEps':5,'quoteCurrency':'USD','financialCurrency':'USD','reportDate':'2026-09-30'}}
        p={'eps':{'value':5,'periodEnd':'2026-06-30'},'url':'https://data.sec.gov/'}
        self.assertFalse(check_quote(q,p)['independentEPSConfirmed'])
    def test_sec_future_filings_excluded(self):
        rows=[{'start':'2026-01-01','end':'2026-03-31','filed':'2027-01-01','val':10}]*4
        payload={'facts':{'us-gaap':{'EarningsPerShareDiluted':{'units':{'USD/shares':rows}}}}}
        self.assertIsNone(reported_eps(payload,dt.date(2026,10,17)))
    def test_bank_uses_book_and_roe_not_operating_margin(self):
        q={'ticker':'JPM','status':'cached','price':100,'peTTM':1}
        f={'status':'fresh','priceToBook':1,'returnOnEquity':.2,'earningsGrowth':.2,'revenueGrowth':-99,'operatingMargins':-99}
        r=score(q,[],f,{})
        self.assertEqual(r['parts']['valuation'],30)
        self.assertEqual(r['parts']['growth'],25)
        self.assertEqual(r['parts']['quality'],20)
    def test_primary_reit_does_not_use_pe(self):
        inputs=json.loads((Path(__file__).resolve().parents[1]/'data/sector-inputs.json').read_text())
        f={'status':'missing','specialist':{**inputs['O'],'status':'fresh'}}
        q={'ticker':'O','status':'cached','price':56,'currency':'USD','peTTM':300}
        r=score(q,[],f,{})
        self.assertEqual(r['coveragePoints'],90)
        self.assertIn('AFFO',r['explanation']['valuation'])
        f['specialist']['status']='stale'
        self.assertEqual(score(q,[],f,{})['coveragePoints'],0)
    def test_validation_conflict_blocks_valuation(self):
        q={'ticker':'MSFT','status':'cached','peTTM':10,'validation':{'valuationBlocked':True}}
        f={'status':'fresh','revenueGrowth':.2,'operatingMargins':.2}
        r=score(q,[],f,{})
        self.assertIsNone(r['parts']['valuation'])
        self.assertNotIn('valuation',r['explanation'])

if __name__=='__main__':unittest.main()
