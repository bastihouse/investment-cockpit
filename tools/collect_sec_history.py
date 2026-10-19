#!/usr/bin/env python3
"""Dated SEC XBRL curation, retaining accession, concepts and arithmetic sources.
Current provider facts and SEC calendar frames are never used to backfill history.
"""
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import re
import time
from collections import defaultdict
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scoring import SPECIAL
from collect_reconstruction_sources import ROOT,get

REVENUES=['RevenueFromContractWithCustomerExcludingAssessedTax','RevenueFromContractWithCustomerIncludingAssessedTax','Revenues','SalesRevenueNet','SalesRevenueGoodsNet']
INCOME=['NetIncomeLossAvailableToCommonStockholdersBasic','NetIncomeLoss']

def extract(payload,ticker,today,document_hash):
    cik=int(payload['cik']);facts=payload.get('facts',{}).get('us-gaap',{})
    profile=SPECIAL.get(ticker,'operating');financial=profile in ('bank','insurance','holding')
    main=INCOME if financial else REVENUES
    by_filing=defaultdict(list)
    for tag in main+(['OperatingIncomeLoss'] if not financial else []):
        for r in facts.get(tag,{}).get('units',{}).get('USD',[]):
            try:
                start,end,filed=[dt.date.fromisoformat(r[k]) for k in ('start','end','filed')]
                if r.get('form') not in ('10-Q','10-K') or filed>today or end>today or end>=filed or end<dt.date(2020,1,1):continue
                if not 65<=(end-start).days<=380 or not isinstance(r.get('val'),(float,int)):continue
                if not re.fullmatch(r'\d{10}-\d{2}-\d{6}',r.get('accn','')):continue
                by_filing[(r['accn'],r['filed'])].append(dict(r,tag=tag))
            except (ValueError,KeyError):continue
    all_rows=[r for rows in by_filing.values() for r in rows]
    def url(accn):return f'https://www.sec.gov/Archives/edgar/data/{cik}/{accn.replace("-","")}/{accn}-index.html'
    def unique(rows):
        if not rows:return None
        # A conflicting tagged value is an unresolved data issue, never averaged.
        if len({r['val'] for r in rows})!=1:return None
        return rows[0]
    def paired(rows,current):
        end=dt.date.fromisoformat(current['end']);duration=(end-dt.date.fromisoformat(current['start'])).days
        prior=[r for r in rows if r['tag']==current['tag'] and 350<=(end-dt.date.fromisoformat(r['end'])).days<=378 and abs((dt.date.fromisoformat(r['end'])-dt.date.fromisoformat(r['start'])).days-duration)<=14]
        return unique(prior)
    def metric(rows,tag,start,end):return unique([r for r in rows if r['tag']==tag and r['start']==start and r['end']==end])
    def asof(tag,end,low,high,filed):
        candidates=[r for r in all_rows if r['tag']==tag and r['end']==end and r['filed']<=filed and low<=(dt.date.fromisoformat(r['end'])-dt.date.fromisoformat(r['start'])).days<=high]
        if not candidates:return None
        latest=max(r['filed'] for r in candidates)
        return unique([r for r in candidates if r['filed']==latest])
    output=[]
    def emit(cur,prior,op,months,accn,filed,inputs=None,start=None):
        if cur['end']<'2020-01-01':return
        if not prior or prior['val']<=0:return
        if not financial and cur['val']<=0:return
        sources=inputs or [cur,prior]+([op] if op else [])
        record=dict(ticker=ticker,periodEnd=cur['end'],periodStart=start or cur['start'],publishedAt=filed,
                    periodMonths=months,kind=profile if financial else 'operating',currency='USD',
                    sourceUrl=url(accn),documentSha256=document_hash,sourceType='SEC Companyfacts / filed XBRL',
                    accession=accn,availabilityBasis='SEC filing date; use strictly after actual trading cutoff',
                    sourceInputs=[{k:r[k] for k in ('tag','start','end','val','accn','filed')} for r in sources],
                    priceBasisVerified=False,epsDiluted=None,
                    basis='Reported US-GAAP USD values in millions. EPS valuation withheld without verified historical share basis. SEC filing date is conservative availability, not an earnings-release date.',
                    growthBasis=('quarterly-' if months==3 else 'annual-')+('shareholder-net-income-yoy' if financial else 'yoy'))
        if financial:record.update(netIncome=cur['val']/1e6,netIncomeYearAgo=prior['val']/1e6)
        else:record.update(revenue=cur['val']/1e6,revenueYearAgo=prior['val']/1e6,operatingIncome=op['val']/1e6 if op else None)
        if inputs:record['derivation']='Q4 = reported fiscal year minus first nine months; all operands filed by publishedAt. No EPS subtraction.'
        output.append(record)
    for (accn,filed),rows in sorted(by_filing.items(),key=lambda kv:kv[0][1]):
        mains=[r for r in rows if r['tag'] in main]
        if not mains:continue
        latest=max(r['end'] for r in mains)
        for months,low,high in [(3,65,110),(12,330,380)]:
            possible=[r for r in mains if r['end']==latest and low<=(dt.date.fromisoformat(r['end'])-dt.date.fromisoformat(r['start'])).days<=high]
            if not possible:continue
            tag=min({r['tag'] for r in possible},key=main.index)
            current=unique([r for r in possible if r['tag']==tag]);prior=paired(rows,current) if current else None
            if not current or not prior:continue
            op=metric(rows,'OperatingIncomeLoss',current['start'],current['end']) if not financial else None
            emit(current,prior,op,months,accn,filed)
            if months!=12:continue
            # Locate the actual fiscal nine-month end, rather than assuming calendar September.
            nine=[r for r in all_rows if r['tag']==tag and r['start']==current['start'] and r['filed']<=filed and 240<=(dt.date.fromisoformat(r['end'])-dt.date.fromisoformat(r['start'])).days<=300]
            if not nine:continue
            end9=max(r['end'] for r in nine);n=asof(tag,end9,240,300,filed)
            prev9=[r for r in all_rows if r['tag']==tag and r['start']==prior['start'] and r['filed']<=filed and 240<=(dt.date.fromisoformat(r['end'])-dt.date.fromisoformat(r['start'])).days<=300]
            if not n or not prev9:continue
            pn=asof(tag,max(r['end'] for r in prev9),240,300,filed)
            start=(dt.date.fromisoformat(end9)+dt.timedelta(days=1)).isoformat()
            if not pn or not 65<=(dt.date.fromisoformat(latest)-dt.date.fromisoformat(start)).days<=110:continue
            a=dict(current,val=current['val']-n['val']);b=dict(prior,val=prior['val']-pn['val']);qo=None;inputs=[current,n,prior,pn]
            if op:
                on=asof('OperatingIncomeLoss',end9,240,300,filed)
                if on and on['start']==current['start']:qo=dict(op,val=op['val']-on['val']);inputs.extend([op,on])
            emit(a,b,qo,3,accn,filed,inputs,start)
    # First public filing for each exact duration; later restatements are retained
    # only in their own source inputs, never moved back to an earlier date.
    first={}
    for row in sorted(output,key=lambda r:(r['publishedAt'],bool(r.get('derivation')))):
        first.setdefault((row['periodEnd'],row['periodMonths']),row)
    return sorted(first.values(),key=lambda r:(r['periodEnd'],r['periodMonths']))

def main():
    universe=json.loads((ROOT/'data/universe.json').read_text())
    existing=json.loads((ROOT/'data/historical-reports.json').read_text())['reports']+json.loads((ROOT/'data/historical-extensions.json').read_text())['reports']
    covered={r['ticker'] for r in existing}
    mapping=json.loads(get('https://www.sec.gov/files/company_tickers.json'))
    ciks={r['ticker'].replace('-','.'):int(r['cik_str']) for r in mapping.values()}
    today=dt.date.today();targets=[s for s in universe if s['ticker'] not in covered];checks=[];reports=[]
    def collect(stock):
        ticker=stock['ticker'];symbol=stock['yahoo'].replace('-','.')
        cik=ciks.get(symbol)
        if not cik:return {'ticker':ticker,'status':'unavailable','reason':'No matching SEC symbol for the exact traded instrument'},[]
        url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'
        try:
            body=get(url);payload=json.loads(body)
            if int(payload['cik'])!=cik:raise ValueError('CIK mismatch')
            rows=extract(payload,ticker,today,hashlib.sha256(body).hexdigest())
            return {'ticker':ticker,'status':'available' if rows else 'unsupported','cik':cik,'url':url,'reports':len(rows),'reason':None if rows else 'No unambiguous comparable US-GAAP USD periods'},rows
        except Exception as e:return {'ticker':ticker,'status':'unavailable','cik':cik,'url':url,'reason':str(e)[:180]},[]
        finally:time.sleep(.3)
    with cf.ThreadPoolExecutor(max_workers=2) as pool:
        for check,rows in pool.map(collect,targets):
            checks.append(check);reports.extend(rows);print(check['ticker'],check['status'],len(rows),flush=True)
    output=dict(schemaVersion=1,collectedAt=dt.datetime.now(dt.timezone.utc).isoformat(),policy='SEC filing dates, original accession and USD concepts; no current estimates, calendar frame backfill or historical EPS valuation without verified share basis.',reports=sorted(reports,key=lambda r:(r['ticker'],r['periodEnd'],r['periodMonths'])),collectionChecks=checks)
    (ROOT/'data/historical-sec.json').write_text(json.dumps(output,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    print('REPORTS',len(reports),'TICKERS',len({r['ticker'] for r in reports}),flush=True)

def package_existing():
    source=json.loads((ROOT/'data/historical-sec.json').read_text());directory=ROOT/'data/historical-sec';directory.mkdir(exist_ok=True)
    chunks=[];current=[];size=0
    for record in source['reports']:
        length=len(json.dumps(record,ensure_ascii=False,separators=(',',':')).encode())
        if current and size+length>380_000:chunks.append(current);current=[];size=0
        current.append(record);size+=length
    if current:chunks.append(current)
    for i,rows in enumerate(chunks,1):
        bundle={k:v for k,v in source.items() if k not in ('reports','collectionChecks')}
        bundle['reports']=rows;bundle['collectionChecks']=source['collectionChecks'] if i==1 else []
        path=directory/f'part-{i:02d}.json';path.write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':'))+'\n')
        print(path.name,len(rows),path.stat().st_size)

if __name__=='__main__':
    if '--package-existing' in sys.argv:package_existing()
    else:main();package_existing()
