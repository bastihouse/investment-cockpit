#!/usr/bin/env python3
"""Curate issuer releases for historical reconstruction; no current vendor facts used."""
import concurrent.futures as cf
import datetime as dt
import hashlib
import io
import json
import pathlib
import re
import subprocess
import urllib.request
import urllib.parse
from lxml import html
ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=ROOT.parent/'tmp/reconstruction-sources'
CACHE.mkdir(parents=True,exist_ok=True)
TODAY=dt.date.today()
MONTHS={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
DATE=r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(20\d{2})'
def parsedate(s):
 m=re.search(DATE,s)
 if not m: raise ValueError('Publication/report date missing')
 return dt.date(int(m[3]),MONTHS[m[1]],int(m[2])).isoformat()
def get(url):
 p=CACHE/hashlib.sha256(url.encode()).hexdigest()
 if p.exists():return p.read_bytes()
 req=urllib.request.Request(url,headers={'User-Agent':'InvestmentCockpit public research; github.com/bastihouse/investment-cockpit'})
 with urllib.request.urlopen(req,timeout=25) as r:b=r.read()
 p.write_bytes(b);return b
def numbers(s):return [float(x.replace(',','').replace('$','').replace(' ','').replace('(','-').replace(')','')) for x in re.findall(r'\(?\$?\s*-?\d[\d,]*\.\d+\)?|\(?\$?\s*-?\d[\d,]*\)?',s)]
def msft(year,q):
 url=f'https://www.microsoft.com/en-us/Investor/earnings/FY-{year}-Q{q}/press-release-webcast'
 b=get(url);tree=html.fromstring(b);txt=' '.join(tree.itertext());txt=' '.join(txt.split())
 intro=re.search(r'REDMOND,?\s+Wash.*?quarter ended.*?as compared',txt,re.I)
 if not intro:raise ValueError('Microsoft release header missing')
 pub=parsedate(intro[0]); end=parsedate(intro[0].split('quarter ended')[-1])
 if pub>TODAY.isoformat():return None
 for t in tree.xpath('//table'):
  rows=[[' '.join(' '.join(c.itertext()).split()) for c in tr.xpath('./td|./th') if ' '.join(c.itertext()).strip()] for tr in t.xpath('.//tr')]
  if not any(r and r[0].lower()=='total revenue' for r in rows):continue
  rev=next(r for r in rows if r and r[0].lower()=='total revenue')
  op=next(r for r in rows if r and r[0].lower()=='operating income')
  eps=next(r for r in rows if r and r[0].lower()=='diluted')
  clean=lambda s:float(re.sub(r'[^0-9.\-]','',s))
  return dict(ticker='MSFT',publishedAt=pub,periodEnd=end,revenue=clean(rev[1]),revenueYearAgo=clean(rev[2]),operatingIncome=clean(op[1]),epsDiluted=clean(eps[1]),currency='USD',units='USD millions, EPS USD/share',sourceUrl=url,documentSha256=hashlib.sha256(b).hexdigest(),basis='Original release, current quarter GAAP column',priceBasis='No stock split after 2020')
 raise ValueError('Microsoft GAAP statement missing')
APPLE=[(2020,4,10),(2021,1,1),(2021,2,4),(2021,3,7),(2021,4,10),(2022,1,1),(2022,2,4),(2022,3,7),(2022,4,10),(2023,1,2),(2023,2,5),(2023,3,8),(2023,4,11),(2024,1,2),(2024,2,5),(2024,3,8),(2024,4,10),(2025,1,1),(2025,2,5),(2025,3,7),(2025,4,10),(2026,1,1),(2026,2,4),(2026,3,7)]
def apple(year,q,month):
 ordinal={1:'first',2:'second',3:'third',4:'fourth'}[q]
 url=f'https://www.apple.com/newsroom/{year}/{month:02d}/apple-reports-{ordinal}-quarter-results/'
 b=get(url);tree=html.fromstring(b);txt=' '.join(' '.join(tree.itertext()).split())
 pub=parsedate(txt[txt.find('PRESS RELEASE'):])
 if pub>TODAY.isoformat():return None
 end=parsedate(re.search(r'quarter ended.*?(?:\.|The Company)',txt,re.I)[0])
 links=[a.get('href') for a in tree.xpath('//a') if '.pdf' in (a.get('href') or '') and 'financial' in (a.get('href') or '').lower()]
 if len(links)!=1:raise ValueError('Apple financial PDF not unique')
 pdfurl=urllib.parse.urljoin(url,links[0]);pb=get(pdfurl)
 text=subprocess.run(['pdftotext','-f','1','-l','1','-layout','-','-'],input=pb,capture_output=True,check=True).stdout.decode()
 lines=text.splitlines()
 def pick(label):
  pattern=r'^\s*'+r'\s*'.join(re.escape(c) for c in label.replace(' ',''))+r'\s*'
  idx=next(i for i,x in enumerate(lines) if re.match(pattern,x,re.I))
  value=re.sub(r'^\s*\(1\)\s*','',re.sub(pattern,'',lines[idx],flags=re.I))
  if len(numbers(value))<2:value+=' '+next(x for x in lines[idx+1:] if x.strip())
  return value
 rev=numbers(pick('Total net sales'));op=numbers(pick('Operating income'));eps=numbers(pick('Diluted'))
 return dict(ticker='AAPL',publishedAt=pub,periodEnd=end,revenue=rev[0],revenueYearAgo=rev[1],operatingIncome=op[0],epsDiluted=eps[0],currency='USD',units='USD millions, EPS USD/share',sourceUrl=url,statementUrl=pdfurl,documentSha256=hashlib.sha256(pb).hexdigest(),basis='Original release, current quarter GAAP column',priceBasis='No stock split after 2020')
def main():
 jobs=[('MSFT',msft,(y,q)) for y in range(2021,2027) for q in range(1,5)]+[('AAPL',apple,args) for args in APPLE]
 results=[];fail=[]
 with cf.ThreadPoolExecutor(max_workers=4) as pool:
  futures={pool.submit(fn,*args):(ticker,args) for ticker,fn,args in jobs}
  for f in cf.as_completed(futures):
   ticker,args=futures[f]
   try:
    r=f.result()
    if r:
     assert 0<r['operatingIncome']<r['revenue']<1e7 and 0.3<r['revenue']/r['revenueYearAgo']<3 and abs(r['epsDiluted'])<100
     assert 0<(dt.date.fromisoformat(r['publishedAt'])-dt.date.fromisoformat(r['periodEnd'])).days<120
     results.append(r);print(ticker,args,r['publishedAt'],r['periodEnd'],r['revenue'],r['operatingIncome'],r['epsDiluted'],flush=True)
   except Exception as e:fail.append(dict(ticker=ticker,period=str(args),error=repr(e)));print('FAILED',ticker,args,str(e),flush=True)
 result=dict(schemaVersion=1,collectedAt=dt.datetime.now(dt.timezone.utc).isoformat(),policy='Original issuer releases; current-quarter GAAP figures only. Published date used conservatively from next trading day. EPS sum is a TTM approximation.',reports=sorted(results,key=lambda r:(r['ticker'],r['periodEnd'])),collectionErrors=fail)
 (ROOT/'data/historical-reports.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
 print('REPORTS',len(results),'FAILURES',len(fail))
if __name__=='__main__':main()
