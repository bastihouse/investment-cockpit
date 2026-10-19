#!/usr/bin/env python3
"""Curate EPS only for reviewed instruments; do not infer a clean split history.
Offline source curation. No automatic release of unreviewed instruments in CI.
"""
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
ROOT=Path(__file__).resolve().parents[1]

REVIEWED={
 'AMD':('https://ir.amd.com/stock-data/stock-split-history',[]),
 'COST':('https://investor.costco.com/stock-info/dividend-history/default.aspx',[]),
 'QCOM':('https://investor.qualcomm.com/stock-info/dividend-split-history/default.aspx',[]),
 'AVGO':('https://investors.broadcom.com/static-files/e90fe911-25c9-47eb-afbe-8e763b71eb64', [('2024-07-15',10)]),
 'WMT':('https://stock.walmart.com/stock-data/stock-split-history',[('2024-02-26',3)]),
}

def unique(rows):
    return rows[0] if rows and len({r['val'] for r in rows})==1 else None

def observations(payload,events,today):
    facts=payload['facts']['us-gaap'];out=[]
    eps=facts.get('EarningsPerShareDiluted',{}).get('units',{}).get('USD/shares',[])
    shares=facts.get('WeightedAverageNumberOfDilutedSharesOutstanding',{}).get('units',{}).get('shares',[])
    income=[]
    for tag in ['NetIncomeLossAvailableToCommonStockholdersDiluted','NetIncomeLossAvailableToCommonStockholdersBasic','NetIncomeLoss','ProfitLoss']:
        income += [dict(r,tag=tag) for r in facts.get(tag,{}).get('units',{}).get('USD',[])]
    for r in eps:
        try:
            start,end,filed=[dt.date.fromisoformat(r[k]) for k in ('start','end','filed')]
            days=(end-start).days
            if r.get('form') not in ('10-Q','10-K') or filed>today or end>=filed or end<dt.date(2019,1,1) or not 65<=days<=380:continue
            # Current period only: comparative restatements are never backdated.
            if (filed-end).days>100:continue
            if len({x['val'] for x in eps if all(x.get(k)==r[k] for k in ('accn','start','end'))})!=1:continue
            if any(abs((filed-dt.date.fromisoformat(date)).days)<=7 for date,_ in events):continue
            s=unique([x for x in shares if all(x.get(k)==r[k] for k in ('accn','start','end'))])
            if not s or s['val']<=0:continue
            candidates=[x for x in income if all(x.get(k)==r[k] for k in ('accn','start','end'))]
            n=next((x for x in candidates if abs(x['val']/s['val']-r['val'])<=max(.015,abs(r['val'])*.02)),None)
            if not n:continue
            factor=math.prod(ratio for date,ratio in events if date>r['filed'])
            out.append(dict(start=r['start'],end=r['end'],filed=r['filed'],accn=r['accn'],
                            eps=r['val'],factor=factor,normalized=r['val']/factor,
                            shareCount=s['val'],netIncome=n['val'],netIncomeTag=n['tag'],days=days))
        except (KeyError,ValueError,TypeError):continue
    # First same-period filing, conflicting facts are withheld.
    first={}
    for r in sorted(out,key=lambda x:x['filed']):first.setdefault((r['start'],r['end']),r)
    return list(first.values())

def ttm_at(obs,end,filed):
    available=[r for r in obs if r['filed']<=filed]
    current=[r for r in available if r['end']==end]
    annual=next((r for r in current if 330<=r['days']<=380),None)
    if annual:return annual['normalized'],[dict(annual,coefficient=1)],'reported annual diluted EPS'
    # Sum of four reported quarters, never FY-minus-nine-months Q4 EPS.
    quarters=sorted([r for r in available if 65<=r['days']<=110 and r['end']<=end],key=lambda r:r['end'])[-4:]
    if len(quarters)==4 and quarters[-1]['end']==end and all(70<=(dt.date.fromisoformat(b['end'])-dt.date.fromisoformat(a['end'])).days<=110 for a,b in zip(quarters,quarters[1:])):
        return sum(r['normalized'] for r in quarters),[dict(r,coefficient=1) for r in quarters],'sum of four reported quarter diluted EPS'
    # TTM approximation from reported YTD + prior FY - prior YTD.
    for cur in sorted(current,key=lambda r:r['days'],reverse=True):
        for year in available:
            if not 330<=year['days']<=380:continue
            if not 0<=(dt.date.fromisoformat(cur['start'])-dt.date.fromisoformat(year['end'])).days<=7:continue
            prior=next((r for r in available if r['start']==year['start'] and abs(r['days']-cur['days'])<=14 and 350<=(dt.date.fromisoformat(cur['end'])-dt.date.fromisoformat(r['end'])).days<=378),None)
            if prior:
                operands=[dict(cur,coefficient=1),dict(year,coefficient=1),dict(prior,coefficient=-1)]
                return sum(r['normalized']*r['coefficient'] for r in operands),operands,'reported YTD + prior FY - prior YTD diluted EPS approximation; not a fabricated Q4'
    return None,[],None

def main():
    from collect_reconstruction_sources import get
    from historical_sources import load_reports
    reports,_,_=load_reports(ROOT,apply_audit=False)
    mapping=json.loads(get('https://www.sec.gov/files/company_tickers.json'))
    ciks={r['ticker']:int(r['cik_str']) for r in mapping.values()};today=dt.date.today();overlays=[];checks=[]
    for ticker,(source,events) in REVIEWED.items():
        try:
            body=get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{ciks[ticker]:010d}.json');payload=json.loads(body)
            proof=get(source);obs=observations(payload,events,today);count=0
            for row in [r for r in reports if r['ticker']==ticker and r.get('sourceType')=='SEC Companyfacts / filed XBRL']:
                value,operands,basis=ttm_at(obs,row['periodEnd'],row['publishedAt'])
                if value is None:continue
                for r in operands:r['url']=f'https://www.sec.gov/Archives/edgar/data/{ciks[ticker]}/{r["accn"].replace("-","")}/{r["accn"]}-index.html'
                overlays.append(dict(ticker=ticker,periodEnd=row['periodEnd'],periodMonths=row['periodMonths'],publishedAt=row['publishedAt'],
                  documentSha256=row['documentSha256'],epsTtmApprox=value,epsTtmInputs=operands,epsTtmBasis=basis,
                  epsBasisAudit={'status':'reviewed','checkedThrough':today.isoformat(),'instrument':ticker,'currency':'USD','sourceUrl':source,
                                 'documentSha256':hashlib.sha256(proof).hexdigest(),'factsSha256':hashlib.sha256(body).hexdigest(),
                                 'splitEvents':[dict(tradingDate=d,ratio=v,url=source) for d,v in events]}));count+=1
            checks.append(dict(ticker=ticker,status='reviewed',periods=count,sourceUrl=source));print(ticker,count,flush=True)
        except Exception as e:checks.append(dict(ticker=ticker,status='open',reason=str(e)));print(ticker,str(e),flush=True)
    out=dict(schemaVersion=1,collectedAt=dt.datetime.now(dt.timezone.utc).isoformat(),policy='Reviewed exact common-share instruments only. SEC diluted EPS reconciled to income / diluted shares in the same accession and period. Later comparative facts never become earlier inputs. TTM is an approximation; no full score without revisions.',epsOverlays=overlays,collectionChecks=checks)
    (ROOT/'data/historical-eps-audit.json').write_text(json.dumps(out,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')

if __name__=='__main__':main()
