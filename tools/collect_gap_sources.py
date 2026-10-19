#!/usr/bin/env python3
"""Reviewed gap collection: original issuer releases, never adjusted-profit proxies."""
import datetime as dt
import json
import re
from collect_expanded_sources import ROOT, OUT, get, html, mc, record

def generali_annual(url,year):
    body=get(url);tree=html.fromstring(body)
    for node in tree.xpath('//script|//style'):node.drop_tree()
    text=' '.join(tree.text_content().split())
    date=re.search(r'(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (20\d{2}) - \d{2}:\d{2} price sensitive',text)
    if not date:raise ValueError('Original Generali release date missing')
    pub=dt.datetime.strptime(' '.join(date.groups()),'%d %B %Y').date().isoformat()
    # Exact unadjusted group net-result sentence, with an explicit prior-year value.
    m=re.search(r'The net result (?:amounted to|grew by [\d.]+% to) €\s*([\d,]+) million \(€\s*([\d,]+) million FY'+str(year-1)+r'\)',text)
    if not m:raise ValueError('Explicit IFRS group net result and prior year not found; adjusted result excluded')
    if f'31 December {year}' not in text:raise ValueError('Fiscal year mismatch')
    return record('G',url,body,pub,f'{year}-12-31',kind='insurance',currency='EUR',periodMonths=12,
                  netIncome=float(m[1].replace(',','')),netIncomeYearAgo=float(m[2].replace(',','')),
                  growthBasis='annual-shareholder-net-income-yoy',accountingBasis='IFRS17/IFRS9',
                  basis='Original issuer annual group net result, not adjusted net result or operating result. No quarterly relabelling; book value per share and comparable IFRS ROE remain missing.')

def main():
    current=json.loads(OUT.read_text());existing={(r['ticker'],r['periodEnd'],r.get('periodMonths',3)):r for r in current['reports']}
    jobs=[('MC',mc,(f'https://www.lvmh.com/en/financial-calendar/{y}-first-half-results',y,6)) for y in (2022,2024)]
    jobs += [('G',generali_annual,(f'https://www.generali.com/media/press-releases/all/{y+1}/Consolidated-Results-as-of-31-December-{y}',y)) for y in (2024,2025)]
    errors=[];completed=set()
    for ticker,fn,args in jobs:
        try:
            row=fn(*args)
            if not row:raise ValueError('Future release excluded')
            existing[(row['ticker'],row['periodEnd'],row['periodMonths'])]=row
            completed.add((ticker,args[0]));print(ticker,row['periodEnd'],row['publishedAt'])
        except Exception as error:errors.append({'ticker':ticker,'args':list(args),'error':str(error)})
    current['collectionErrors']=[e for e in current.get('collectionErrors',[]) if (e['ticker'],e['args'][0]) not in completed]+errors
    current['reports']=sorted(existing.values(),key=lambda r:(r['ticker'],r['periodEnd'],r.get('periodMonths',3)))
    current['collectedAt']=dt.datetime.now(dt.timezone.utc).isoformat()
    OUT.write_text(json.dumps(current,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    print('REPORTS',len(existing),'ERRORS',len(current['collectionErrors']))

if __name__=='__main__':main()
