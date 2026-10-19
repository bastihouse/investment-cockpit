#!/usr/bin/env python3
"""Reviewed 1:1 registrant continuity, never concatenate an unrelated parent/spin-off."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_reconstruction_sources import ROOT,get
from collect_sec_history import extract
from historical_sources import load_reports

CONTINUITY={
 'XOM':(34088,2115436,'2026-07-01','https://www.sec.gov/Archives/edgar/data/2115436/000119312526291990/d71068d8k12b.htm'),
 'BLK':(1364742,2012383,'2024-10-01','https://www.sec.gov/Archives/edgar/data/1364742/000119312524229882/d887774dposasr.htm'),
}
def main():
    existing,_,_=load_reports(ROOT);keys={(r['ticker'],r['periodEnd'],r.get('periodMonths',3)) for r in existing if not r.get('entityContinuity')};reports=[];checks=[]
    for ticker,(old,new,date,url) in CONTINUITY.items():
        try:
            proof=get(url);body=get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{old:010d}.json');payload=json.loads(body)
            assert int(payload['cik'])==old
            rows=extract(payload,ticker,dt.date.today(),hashlib.sha256(body).hexdigest())
            for row in rows:
                if row['publishedAt']>=date or (ticker,row['periodEnd'],row['periodMonths']) in keys:continue
                row['entityContinuity']=dict(predecessorCIK=old,successorCIK=new,effectiveDate=date,exchangeRatio=1,sourceUrl=url,documentSha256=hashlib.sha256(proof).hexdigest(),policy='Same economic common-share interest, 1:1 registrant reorganization; original filing availability retained. Not a parent-company spin-off proxy.')
                reports.append(row)
            checks.append(dict(ticker=ticker,status='reviewed-continuity',reports=sum(r['ticker']==ticker for r in reports)));print(checks[-1],flush=True)
        except Exception as e:checks.append(dict(ticker=ticker,status='open',reason=str(e)));print(checks[-1],flush=True)
    checks += [dict(ticker='GEV',status='separate-instrument',firstTradingDate='2024-04-02',sourceUrl='https://www.gevernova.com/news/press-releases/ge-vernova-completes-spin-off-begins-trading-new-york-stock-exchange',reason='Independent spin-off; pre-listing parent prices are not GEV prices.'),dict(ticker='SNDK',status='separate-instrument',firstTradingDate='2025-02-24',sourceUrl='https://www.sec.gov/Archives/edgar/data/2023554/000119312525033433/d849281d8k.htm',reason='Independent spin-off; Western Digital prices are not Sandisk prices.')]
    (ROOT/'data/historical-predecessors.json').write_text(json.dumps(dict(schemaVersion=1,collectedAt=dt.datetime.now(dt.timezone.utc).isoformat(),reports=reports,collectionChecks=checks),ensure_ascii=False,separators=(',',':'))+'\n')
if __name__=='__main__':main()
