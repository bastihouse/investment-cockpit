#!/usr/bin/env python3
"""Fixed, dated top 100 from physical iShares STOXX Europe 600 holdings."""
import csv,datetime as dt,hashlib,io,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://www.ishares.com/de/privatanleger/de/produkte/251931/ishares-stoxx-europe-600-ucits-etf-de/latest-holdings.csv'
PAGE='https://www.ishares.com/de/privatanleger/de/produkte/251931/ishares-stoxx-europe-600-ucits-etf-de-fu_2'
EXCHANGES={'Euronext Amsterdam':'.AS','SIX Swiss Exchange':'.SW','London Stock Exchange':'.L','Xetra':'.DE','Nyse Euronext - Euronext Paris':'.PA','Bolsa De Madrid':'.MC','Borsa Italiana':'.MI','Nyse Euronext - Euronext Brussels':'.BR','Omx Nordic Exchange Copenhagen A/S':'.CO','Nasdaq Omx Nordic':'.ST','Nasdaq Omx Helsinki Ltd.':'.HE'}
OVERRIDES={'NDA FI':'NDA-FI','NOVO B':'NOVO-B','INVE B':'INVE-B','VOLV B':'VOLV-B','ATCO A':'ATCO-A','ASSA B':'ASSA-B','BP.':'BP','RR.':'RR','NG.':'NG','BA.':'BA'}
MONTHS={'Jan':1,'Feb':2,'Mär':3,'Apr':4,'Mai':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Okt':10,'Nov':11,'Dez':12}
def select(body,today):
 s=body.decode('utf-8-sig');m=re.search(r'Fondsposition per,"(\d+)\.([A-Za-zä]+)\.(\d{4})"',s)
 if not m:raise ValueError('Dated issuer holdings required')
 asof=dt.date(int(m[3]),MONTHS[m[2]],int(m[1]))
 if not 0<=(today-asof).days<=10:raise ValueError('Holdings are stale or future dated')
 rows=list(csv.DictReader(io.StringIO(s[s.index('Emittententicker,'):])));stocks=[]
 for r in rows:
  if r.get('Anlageklasse')!='Aktien':continue
  weight=float(r['Gewichtung (%)'].replace('.','').replace(',','.'))
  if weight<=0:continue
  stocks.append(dict(r,weight=weight))
 if not 580<=len(stocks)<=620 or not 98<=sum(x['weight'] for x in stocks)<=101:raise ValueError('Unexpected equity holdings breadth/weight')
 # Deterministic ties: issuer file order (rounded weights); no invented extra precision.
 selected=sorted(stocks,key=lambda r:-r['weight'])[:100]
 for r in selected:
  suffix=EXCHANGES[r['Börse']];symbol=OVERRIDES.get(r['Emittententicker'],r['Emittententicker'])+suffix
  r['yahoo']=symbol;r['currency']='GBP' if suffix=='.L' and r['Marktwährung']=='GBP' else r['Marktwährung']
 if len({r['yahoo'] for r in selected})!=100:raise ValueError('Duplicate instruments')
 return asof,selected

def build(body,today=None):
 asof,selected=select(body,today or dt.date.today());path=ROOT/'data/universe.json';old=json.loads(path.read_text());by_symbol={r['yahoo']:r for r in old}
 for r in old:r.pop('stoxx600Top100',None)
 holdings=[]
 for rank,r in enumerate(selected,1):
  symbol=r['yahoo'];stock=by_symbol.get(symbol)
  if stock is None:
   stock=dict(ticker=symbol,yahoo=symbol,name=r['Name'],currency=r['currency'],originalUniverse=False);old.append(stock);by_symbol[symbol]=stock
  stock['stoxx600Top100']=dict(rank=rank,weightProxyPct=r['weight'],asOf=asof.isoformat())
  stock['listingExchange']=r['Börse'];stock['country']=r['Standort']
  holdings.append(dict(ticker=stock['ticker'],yahoo=symbol,name=r['Name'],exchange=r['Börse'],issuerTicker=r['Emittententicker'],currency=stock['currency'],rank=rank,weightProxyPct=r['weight']))
 meta=dict(schemaVersion=1,asOf=asof.isoformat(),selectedAt=dt.datetime.now(dt.timezone.utc).isoformat(),sourceUrl=URL,sourcePage=PAGE,sourceSha256=hashlib.sha256(body).hexdigest(),sourceFile='stoxx600-holdings.csv',top100Count=100,totalCount=len(old),holdings=holdings,weightBasis='Physical iShares STOXX Europe 600 ETF holdings, an approximation of index weights; not independently verified original STOXX weights. Rounded equal weights retain issuer file order.',rotation='Fixed selection; no automatic rotation. Current membership introduces selection/survivorship bias.',instrumentPolicy='Exact listing symbols deduplicated. Ordinary shares and existing US ADRs remain separate instruments. UK GBp quotations are explicitly divided by 100 to GBP by the data collector.')
 path.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n');(ROOT/'data/stoxx600-selection.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');(ROOT/'data/stoxx600-holdings.csv').write_bytes(body)
 # Existing S&P selection retains its membership, but total universe count is shared.
 p=ROOT/'data/sp500-selection.json';sp=json.loads(p.read_text());sp['totalCount']=len(old);p.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+'\n')
 print('Universe',len(old),'STOXX selection',len(holdings),'as of',asof)
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--input');args=ap.parse_args()
 body=Path(args.input).read_bytes() if args.input else urllib.request.urlopen(URL,timeout=45).read();build(body)
