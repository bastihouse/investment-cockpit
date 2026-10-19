#!/usr/bin/env python3
"""Exact IFRS currencies and dated issuer statements; no ADR EPS conversion guesses."""
import datetime as dt
import hashlib
import json
import re
import sys
import urllib.parse
from pathlib import Path
from lxml import html
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_reconstruction_sources import ROOT,get,numbers
from collect_expanded_sources import pdftext,pick
TODAY=dt.date.today()

def base(ticker,body,url,pub,end,months,currency,**values):
    assert end<pub<=TODAY.isoformat()
    return dict(ticker=ticker,kind='operating',periodEnd=end,periodMonths=months,publishedAt=pub,
      currency=currency,units='Millions of '+currency,sourceUrl=url,documentSha256=hashlib.sha256(body).hexdigest(),
      priceBasisVerified=False,epsDiluted=None,growthBasis={3:'quarterly-yoy',6:'half-year-yoy',12:'annual-yoy'}[months],**values)

def ifrs(ticker,cik,currency):
    body=get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json');p=json.loads(body)
    assert int(p['cik'])==cik
    facts=p['facts']['ifrs-full'];revs=facts['Revenue']['units'][currency];ops=facts.get('ProfitLossFromOperatingActivities',{}).get('units',{}).get(currency,[])
    output=[]
    for r in revs:
        try:
            start,end,filed=[dt.date.fromisoformat(r[k]) for k in ('start','end','filed')];days=(end-start).days
            months=next((m for m,lo,hi in [(3,65,110),(6,150,200),(12,330,380)] if lo<=days<=hi),None)
            if not months or r.get('form') not in ('20-F','6-K') or filed>TODAY or end>=filed or end<dt.date(2020,1,1) or (filed-end).days>150:continue
            # Comparative facts must be in this same filing and have equal duration.
            previous=[x for x in revs if x['accn']==r['accn'] and x.get('start') and 350<=(end-dt.date.fromisoformat(x['end'])).days<=378 and abs((dt.date.fromisoformat(x['end'])-dt.date.fromisoformat(x['start'])).days-days)<=14]
            if not previous or len({x['val'] for x in previous})!=1 or previous[0]['val']<=0:continue
            op=[x for x in ops if all(x.get(k)==r[k] for k in ('accn','start','end'))]
            op=op[0] if op and len({x['val'] for x in op})==1 else None
            url=f'https://www.sec.gov/Archives/edgar/data/{cik}/{r["accn"].replace("-","")}/{r["accn"]}-index.html'
            output.append(base(ticker,body,url,r['filed'],r['end'],months,currency,periodStart=r['start'],
              revenue=r['val']/1e6,revenueYearAgo=previous[0]['val']/1e6,operatingIncome=op['val']/1e6 if op else None,
              accession=r['accn'],sourceType='SEC IFRS filed XBRL',sourceInputs=[dict(x,tag=tag) for x,tag in [(r,'Revenue'),(previous[0],'Revenue')]+([(op,'ProfitLossFromOperatingActivities')] if op else [])],
              basis='Original IFRS filing; raw reporting currency, no FX conversion. EPS blocked: ADR/instrument and currency basis require a separate review. No adjusted-profit substitute.'))
        except (KeyError,ValueError):continue
    first={}
    for row in sorted(output,key=lambda x:x['publishedAt']):first.setdefault((row['periodEnd'],row['periodMonths']),row)
    return list(first.values())

SAMSUNG={2020:'82715',2021:'82856',2022:'83989',2023:'84125',2024:'84315',2025:'84565'}
def samsung(year,code):
    page=f'https://www.samsung.com/global/ir/reports-disclosures/public-disclosure-view.{code}/';pb=get(page);tree=html.fromstring(pb);text=' '.join(tree.text_content().split())
    match=re.search(r'(Jan|Feb|Mar|Apr)\s+(\d{1,2})\.\s+(20\d{2})',text)
    if not match:raise ValueError('Dated publication notice missing')
    pub=dt.datetime.strptime(' '.join(match.groups()),'%b %d %Y').date().isoformat()
    urls=list(dict.fromkeys(urllib.parse.urljoin(page,a.get('href')).replace('http:','https:') for a in tree.xpath('//a[@href]') if 'pdf' in a.text_content().lower()))
    if len(urls)!=1:raise ValueError('Unique financial statement link missing')
    body=get(urls[0]);text=pdftext(body);chunk=next((x[:6500] for x in re.split(r'Consolidated Statements of Profit or Loss',text,flags=re.I)[1:] if re.search(r'^\s*Revenue\s',x,re.M)),None)
    if not chunk:raise ValueError('Consolidated income statement missing')
    # KRW columns are first; note references are separated from values explicitly.
    def metric(label):
        line=next(x for x in chunk.splitlines() if re.match(r'^\s*'+label+r'\s',x,re.I))
        cells=re.split(r'\s{2,}',line.strip());vals=[float(x.replace(',','').replace('(','-').replace(')','')) for x in cells[1:] if re.fullmatch(r'\(?[\d,]+\)?',x)]
        if len(vals)==5:vals=vals[1:]
        if len(vals)<2:raise ValueError('Missing KRW columns')
        return vals
    rev=metric('Revenue');op=metric('Operating profit')
    if rev[0]<1e8 or rev[1]<1e8 or abs(op[0])>rev[0]:raise ValueError('Invalid millions-KRW units')
    return base('005930',body,urls[0],pub,f'{year}-12-31',12,'KRW',revenue=rev[0],revenueYearAgo=rev[1],operatingIncome=op[0],
      releasePage=page,availabilitySourceSha256=hashlib.sha256(pb).hexdigest(),sourceType='Samsung audited consolidated K-IFRS',
      basis='First two KRW-million columns of the original annual consolidated income statement, not convenience USD translations. Dated issuer disclosure notice determines availability. Annual periods remain annual; EPS common/preferred-share basis not substituted.')

def acomo():
    page='https://acomo.nl/investors/investors-publications';tree=html.fromstring(get(page));targets=[]
    # Periodic-report links only: avoid duplicate press-release copies and presentations.
    for a in tree.xpath('//a[@href]'):
        parent=a.getparent();context=' '.join(parent.getparent().text_content().split()) if parent is not None and parent.getparent() is not None else ''
        url=a.get('href')
        if '.pdf' not in url.lower() or not any(v in context for v in ['FY report','FY Report','HY report','HY Report']):continue
        year=re.search(r'(?:FY|HY) [Rr]eport (20\d{2})',context)
        if year and 2020<=int(year[1])<=2025:targets.append((url,int(year[1]),6 if 'HY ' in context else 12))
    # Latest half-year is in the dated press-release block.
    for a in tree.xpath('//a[@href]'):
        url=a.get('href')
        if '260728-Press-release-Acomo-Half-year-Figures-H1-2026_EN_FINAL.pdf' in url:targets.append((url,2026,6))
    out=[]
    for url,year,months in dict.fromkeys(targets):
        url=urllib.parse.quote(url,safe=':/%?=&')
        body=get(url);text=pdftext(body);flat=' '.join(text.split())
        date=re.search(r'ROTTERDAM\s*\(NL\),?\s*(\d{1,2})\s+([A-Z]+)\s+(20\d{2})',flat,re.I)
        if not date:raise ValueError('Acomo release date missing '+url)
        pub=dt.datetime.strptime(' '.join(date.groups()).title(),'%d %B %Y').date().isoformat()
        chunks=re.split(r'(?:Condensed )?consolidated (?:income statement|statement of income)',text,flags=re.I)
        chunk=next((s[:6000] for s in chunks[1:] if pick(s[:6000],'Sales') and pick(s[:6000],r'Operating income(?: \(EBIT\))?')),None)
        if not chunk:raise ValueError('Acomo IFRS statement missing '+url)
        rev=pick(chunk,'Sales');op=pick(chunk,r'Operating income(?: \(EBIT\))?');end=f'{year}-'+('06-30' if months==6 else '12-31')
        out.append(base('ACOMO',body,url,pub,end,months,'EUR',revenue=rev[0]/1000,revenueYearAgo=rev[1]/1000,operatingIncome=op[0]/1000,
          sourceType='Acomo original consolidated IFRS statement',releasePage=page,basis='Original consolidated statement in EUR thousands converted to millions. Reported operating income; adjusted EBITDA / adjusted EPS excluded. EPS share basis remains open.'))
        print('ACOMO',end,flush=True)
    return out

def main():
    reports=[];checks=[]
    jobs=[('UL',lambda:ifrs('UL',217410,'EUR')),('SHEL',lambda:ifrs('SHEL',1306965,'USD')),('ACOMO',acomo)]
    jobs += [('005930',lambda y=y,c=c:[samsung(y,c)]) for y,c in SAMSUNG.items()]
    for ticker,fn in jobs:
        try:
            rows=fn();reports.extend(rows);checks.append(dict(ticker=ticker,status='available',reports=len(rows)));print(ticker,len(rows),flush=True)
        except Exception as e:checks.append(dict(ticker=ticker,status='open',reason=str(e)));print(ticker,str(e),flush=True)
    result=dict(schemaVersion=1,collectedAt=dt.datetime.now(dt.timezone.utc).isoformat(),reports=sorted(reports,key=lambda r:(r['ticker'],r['periodEnd'],r['periodMonths'])),collectionChecks=checks)
    (ROOT/'data/historical-international.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')

if __name__=='__main__':main()
