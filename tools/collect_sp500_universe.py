#!/usr/bin/env python3
"""One-off, dated universe selection from the issuer's daily SPY holdings.
Requires openpyxl locally. No scheduled constituent rotation or invented index weights.
"""
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
URL='https://www.ssga.com/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx'

def select(rows,today):
    if rows[1][1]!='SPY':raise ValueError('Wrong fund')
    asof=dt.datetime.strptime(rows[2][1],'As of %d-%b-%Y').date()
    if not 0<=(today-asof).days<=7:raise ValueError('Holdings date outside current window')
    header=list(rows[4]);fields={k:header.index(k) for k in ['Name','Ticker','Identifier','Weight','Local Currency']}
    stocks=[]
    for row in rows[5:]:
        name,ticker,identifier,weight,currency=[row[fields[k]] for k in fields]
        if not isinstance(ticker,str) or not re.fullmatch(r'[A-Z]{1,5}(?:[.\-][A-Z])?',ticker):continue
        if not isinstance(identifier,str) or not re.fullmatch(r'[A-Z0-9]{9}',identifier):continue
        if not isinstance(weight,(float,int)) or weight<=0 or currency!='USD':continue
        ticker=ticker.replace('-','.')
        stocks.append(dict(ticker=ticker,name=name,yahoo=ticker.replace('.','-'),currency=currency,weightPct=weight,identifier=identifier))
    if not 490<=len(stocks)<=510 or len({s['ticker'] for s in stocks})!=len(stocks):raise ValueError('Unexpected holdings breadth or duplicate symbols')
    if not 98<sum(s['weightPct'] for s in stocks)<101:raise ValueError('Unexpected equity weight')
    return asof,sorted(stocks,key=lambda s:(-s['weightPct'],s['ticker']))[:100]

def main():
    with urllib.request.urlopen(URL,timeout=30) as r:body=r.read()
    rows=list(openpyxl.load_workbook(io.BytesIO(body),read_only=True,data_only=True).active.values)
    asof,selected=select(rows,dt.date.today())
    path=ROOT/'data/universe.json';old=json.loads(path.read_text())
    by_ticker={s['ticker']:s for s in old}
    original=[s['ticker'] for s in old if s.get('originalUniverse',True)]
    for stock in old:
        stock['originalUniverse']=stock['ticker'] in original
        stock.pop('sp500Top100',None)
    for rank,s in enumerate(selected,1):
        stock=by_ticker.setdefault(s['ticker'],{k:s[k] for k in ('ticker','name','yahoo','currency')})
        stock.setdefault('originalUniverse',False)
        stock['sp500Top100']={'rank':rank,'weightProxyPct':s['weightPct'],'asOf':asof.isoformat()}
    result=list(by_ticker.values())
    metadata={'schemaVersion':1,'asOf':asof.isoformat(),'selectedAt':dt.datetime.now(dt.timezone.utc).isoformat(),
              'sourceUrl':URL,'sourceSha256':hashlib.sha256(body).hexdigest(),'selection':'100 largest equity positions by daily SPY holding weight; separate index share classes remain separate.',
              'weightBasis':'SPY holdings proxy for S&P 500 float-adjusted index weight; not independently confirmed original S&P index weights.',
              'rotation':'Fixed selection; no automatic rotation. Historical performance of this current selection is subject to survivorship/selection bias.',
              'originalCount':len(original),'totalCount':len(result),'top100Count':100,'newCount':len(result)-len(old),'holdings':selected}
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'data/sp500-selection.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    print('Universe',len(result),'new',metadata['newCount'],'asOf',asof,'last',selected[-1]['ticker'])

if __name__=='__main__':main()
