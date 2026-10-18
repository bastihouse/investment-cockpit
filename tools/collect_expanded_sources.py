#!/usr/bin/env python3
"""Curate additional issuer originals. Never replace missing GAAP/specialist values with proxies.
Local curation command, not automatic live-input ingestion; requires lxml + Poppler.
"""
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import urllib.parse
from lxml import html
from collect_reconstruction_sources import ROOT,get,parsedate,DATE,numbers,TODAY
def issuerdate(text):
    m=re.search(DATE,text,re.I)
    if not m:raise ValueError('Publication/report date missing')
    return dt.date(int(m[3]),['january','february','march','april','may','june','july','august','september','october','november','december'].index(m[1].lower())+1,int(m[2])).isoformat()
OUT=ROOT/'data/historical-extensions.json'

def pdftext(body):return subprocess.run(['pdftotext','-layout','-','-'],input=body,capture_output=True,check=True).stdout.decode()
def pick(text,label):
    pattern=r'^\s*(?:'+label+r')\s{2,}(.*)$'
    for line in text.splitlines():
        m=re.match(pattern,line,re.I)
        if m:
            v=numbers(re.sub(r'^\d?\s*(?:€\s*(?:mn|bn)|\$\s*(?:mn|bn))\s*','',m[1]))
            if len(v)>=2:return v
    return None

def record(ticker,url,body,pub,end,**values):
    if pub>TODAY.isoformat():return None
    assert end<pub and (dt.date.fromisoformat(pub)-dt.date.fromisoformat(end)).days<150
    return dict(ticker=ticker,publishedAt=pub,periodEnd=end,sourceUrl=url,documentSha256=hashlib.sha256(body).hexdigest(),**values)

def jpm(url,year,q):
    b=get(url);t=pdftext(b);flat=' '.join(t.split())
    m=re.search(r'conference call today,\s*('+DATE+r')',flat,re.I)
    if not m:raise ValueError('JPM publication date not found')
    pub=issuerdate(m[1]);end=dt.date(year,q*3,__import__('calendar').monthrange(year,q*3)[1]).isoformat()
    income=pick(t,'Net income');roe=pick(t,'Return on common equity')
    book=re.search(r'(?<!tangible )Book value per share (?:of|was)\s*\$([\d.]+)',flat,re.I)
    if not income or len(income)<3 or not roe or not book:raise ValueError('JPM primary metrics missing')
    return record('JPM',url,b,pub,end,kind='bank',currency='USD',periodMonths=3,netIncome=income[0],netIncomeYearAgo=income[2],bookValuePerShare=float(book[1]),returnOnEquity=roe[0]/100,qualityBasis='Reported annualized quarterly return on common equity, not ROTCE or a TTM estimate',growthBasis='quarterly-net-income-yoy',basis='Original issuer GAAP net income, common book value and reported common-equity ROE. No tangible-book substitution.')

def alv(url,year,q):
    b=get(url);t=pdftext(b);flat=' '.join(t.split());m=re.search(r'M\s*unich,\s*('+DATE+r')',flat,re.I)
    if not m:raise ValueError('Allianz publication date missing')
    pub=issuerdate(m[1]);end=dt.date(year,q*3,__import__('calendar').monthrange(year,q*3)[1]).isoformat()
    ni=pick(t,r'[-–]\s*attributable to shareholders|Net income attributable to shareholders')
    if not ni:raise ValueError('GAAP attributable net income missing; core figures deliberately excluded')
    return record('ALV',url,b,pub,end,kind='insurance',currency='EUR',periodMonths=3,netIncome=ni[0],netIncomeYearAgo=ni[1],growthBasis='quarterly-shareholder-net-income-yoy',accountingBasis='IFRS17/IFRS9' if year>=2023 else 'pre-IFRS17',basis='Reported shareholder net income only. Core EPS/core ROE excluded. Book value and comparable GAAP ROE remain missing.')

def enr(url,year,q):
    b=get(url);t=pdftext(b);flat=' '.join(t.split());m=re.search(r'Munich,?(?: Germany,)?\s*('+DATE+r')',flat,re.I)
    if not m:raise ValueError('Siemens Energy publication date missing')
    pub=issuerdate(m[1]);cy=year-1 if q==1 else year;month={1:12,2:3,3:6,4:9}[q];end=dt.date(cy,month,__import__('calendar').monthrange(cy,month)[1]).isoformat()
    statement=re.split(r'Consolidated Statements of Income',t,flags=re.I)[-1]
    if statement==t:raise ValueError('IFRS income statement missing')
    rev=pick(statement,'Revenue');op=pick(statement,r'Operating income \(loss\)');eps=pick(statement,'Diluted earnings per share')
    if q==4:
        rev=pick(t,'Revenue');op=None;eps=None
    if not rev or (not op and q!=4):raise ValueError('Revenue / IFRS operating income missing; adjusted profit not used')
    assert 0<rev[0]<25000 and rev[1]>0 and (op is None or abs(op[0])<rev[0])
    return record('ENR',url,b,pub,end,kind='operating',currency='EUR',periodMonths=3,revenue=rev[0],revenueYearAgo=rev[1],operatingIncome=op[0] if op else None,epsDiluted=eps[0] if eps else None,priceBasisVerified=False,growthBasis='quarterly-yoy',basis='Current-quarter IFRS consolidated income statement. No profit-before-special-items proxy. EPS valuation withheld without verified historical share basis.')

def mc(page,year,months):
    tree=html.fromstring(get(page));text=' '.join(tree.text_content().split());m=re.search(r'Published on (\d{2})\.(\d{2})\.(\d{4})',text)
    if not m:raise ValueError('LVMH original publication date missing')
    pub=f'{m[3]}-{m[1]}-{m[2]}'
    candidates=[a.get('href') for a in tree.xpath('//a[@href]') if '.pdf' in a.get('href').lower() and any(k in (a.text_content()+' '+a.get('href')).lower() for k in ['financial document','financial-doc','financialdocuments','financial report','financial-report'])]
    if not candidates:raise ValueError('LVMH original financial document missing')
    url=urllib.parse.urljoin(page,candidates[-1]);b=get(url);t=pdftext(b)
    chunks=re.split(r'CONSOLIDATED INCOME STATEMENT',t,flags=re.I)
    if len(chunks)<2:raise ValueError('IFRS consolidated statement missing')
    statement=next((c for c in chunks[1:] if pick(c[:6000],'Revenue') and pick(c[:6000],'Operating profit')),chunks[-1]);rev=pick(statement,'Revenue');op=pick(statement,'Operating profit');eps=pick(statement,r'Diluted Group share of net earnings per share \(EUR\)|Diluted earnings per share \(EUR\)')
    if not rev or not op:raise ValueError('IFRS revenue / operating profit missing')
    # A notes-column reference can precede the financial years (e.g. Revenue note 24).
    if len(rev)>=4 and rev[0]<100:rev=rev[1:]
    if eps and len(eps)>=4 and eps[0].is_integer() and eps[0]<100:eps=eps[1:]
    end=f'{year}-{6 if months==6 else 12:02d}-{30 if months==6 else 31}'
    assert rev[0]>1000 and rev[1]>1000 and 0<op[0]<rev[0]
    return record('MC',url,b,pub,end,kind='operating',currency='EUR',periodMonths=months,revenue=rev[0],revenueYearAgo=rev[2] if months==6 else rev[1],operatingIncome=op[0],epsDiluted=eps[0] if eps else None,priceBasisVerified=False,growthBasis='half-year-yoy' if months==6 else 'annual-yoy',releasePage=page,basis='Original IFRS consolidated financial document; operating profit includes non-recurring operating items. No recurring-profit substitute. EPS valuation withheld without verified historical share basis.')

def rows_of(table):return [[' '.join(c.text_content().split()) for c in tr.xpath('./td|./th') if c.text_content().strip()] for tr in table.xpath('.//tr')]
def sector(ticker,url,pub):
    b=get(url);tree=html.fromstring(b);txt=' '.join(tree.text_content().split());m=re.search(r'(?:quarter|months) ended\s+('+DATE+r')',txt,re.I)
    if not m:raise ValueError('Quarter end missing')
    end=issuerdate(m[1]);raw={}
    def find(label):
        for table in tree.xpath('//table'):
            for row in rows_of(table):
                if row and re.fullmatch(label,row[0],re.I):return numbers(' '.join(row[1:])),table
        return [],None
    if ticker=='ARCC':
        nav,table=find('Net asset value per share|Net assets per share');nii,_=find(r'Net investment income\(1\)|Net investment income');div,_=find('Dividends declared and payable');debt,_=find('Debt/equity ratio')
        if len(nav)<2 or len(nii)<2 or not div or not debt:raise ValueError('BDC primary NAV/NII/dividend/debt missing')
        dates=[issuerdate(m[0]) for m in re.finditer(DATE,' '.join(table.text_content().split()))]
        prev=next((x for x in dates if x<end),None)
        raw=dict(navPerShare=nav[0],navPreviousPerShare=nav[1],navPreviousDate=prev,niiQuarterPerShare=nii[1],dividendQuarterPerShare=div[0],debtToEquity=debt[0])
        assert 0<nav[0]<100 and -3<nii[1]<3 and 0<div[0]<3 and 0<=debt[0]<10
        if not prev:raw.pop('navPreviousPerShare');raw.pop('navPreviousDate')
        basis='Original NAV and GAAP net investment income; Core EPS and GAAP EPS are not NII substitutes.'
    else:
        affo,_=find('AFFO per share');div,_=find('Cash dividends paid per common share')
        if len(affo)<2 or not div:raise ValueError('REIT quarter AFFO/dividend per share missing')
        raw=dict(affoQuarterPerShareValue=affo[0],affoQuarterPerShareYearAgo=affo[1],cashDividendsQuarterPerShare=div[0])
        assert 0<affo[0]<3 and 0<affo[1]<3 and 0<div[0]<2
        basis='Original reported quarter AFFO per common share and cash dividends per common share; per-share distribution coverage explicitly differs from the live total-dollar measure.'
    return record(ticker,url,b,pub,end,kind='bdc' if ticker=='ARCC' else 'reit',currency='USD',periodMonths=3,specialist=raw,growthBasis='nav-since-comparison-date' if ticker=='ARCC' else 'quarterly-affo-yoy',basis=basis)

def main():
    jobs=[]
    catalog=json.loads(get('https://www.jpmorganchase.com/services/json/v1/investor-relations/quarterly-earnings.json'))
    for item in catalog['items']:
        y=int(item['year']);q=int(item['quarter'][0]);link=item.get('docs',{}).get('pressRelease',{}).get('link')
        if y>=2020 and link:jobs.append(('JPM',jpm,('https://www.jpmorganchase.com'+link,y,q)))
    tree=html.fromstring(get('https://www.allianz.com/en/investor_relations/results-reports/results.html'))
    for url in dict.fromkeys(a.get('href') for a in tree.xpath('//a[@href]') if '.pdf' in a.get('href') and 'release' in a.get('href')):
        m=re.search(r'results/(20\d{2})[-_](1q|2q|3q|4q|fy)',url,re.I)
        if m and int(m[1])>=2020:jobs.append(('ALV',alv,('https://www.allianz.com'+url,int(m[1]),4 if m[2].lower()=='fy' else int(m[2][0]))))
    tree=html.fromstring(get('https://www.siemens-energy.com/global/en/home/investor-relations/publications-ad-hoc.html'))
    for a in tree.xpath('//a[@href]'):
        u=a.get('href');label=a.text_content()+' '+u
        if '.pdf' not in u.lower() or 'earnings' not in label.lower():continue
        m=re.search(r'Q([1-4])\s*FY\s*(20)?(\d{2})|Q([1-4])[-_ ]*(?:FY)?[-_ ]*(20\d{2})',label,re.I)
        if m:
            q=int(m[1] or m[4]);year=int('20'+m[3]) if m[3] else int(m[5]);jobs.append(('ENR',enr,(u,year,q)))
    for y in range(2020,2027):
        for months,label in [(6,'first-half'),(12,'full-year')]:
            if y==2026 and months==12:continue
            jobs.append(('MC',mc,(f'https://www.lvmh.com/en/financial-calendar/{y}-{label}-results',y,months)))
    # SEC originals discovered through public 8-K exhibit links, publication no earlier than filing date.
    linkfile=ROOT/'tools/sec-report-links.json'
    if linkfile.exists():
        for entry in json.loads(linkfile.read_text()):
            links=entry.get('links',[])
            if links:jobs.append((entry['ticker'],sector,(entry['ticker'],urllib.parse.urljoin(entry['filingUrl'],links[0][1]),entry['publishedAt'])))
    current=json.loads(OUT.read_text()) if OUT.exists() else {'schemaVersion':1,'reports':[]};existing={(r['ticker'],r['periodEnd'],r.get('periodMonths',3)):r for r in current['reports']};errors=[]
    def run(j):
        ticker,fn,args=j
        try:return j,fn(*args),None
        except Exception as e:return j,None,str(e)
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for (ticker,fn,args),r,error in pool.map(run,jobs):
            if r:existing[(r['ticker'],r['periodEnd'],r.get('periodMonths',3))]=r;print(ticker,r['periodEnd'],r['publishedAt'],r['kind'],flush=True)
            elif error:errors.append({'ticker':ticker,'args':list(args),'error':error});print('FAILED',ticker,str(args)[:60],error,flush=True)
    current.update(collectedAt=dt.datetime.now(dt.timezone.utc).isoformat(),policy='Original issuer financial statements and dated original exhibits. Missing specialist/GAAP/share-basis inputs remain missing. Annual and half-year figures never relabelled as quarters.',reports=sorted(existing.values(),key=lambda r:(r['ticker'],r['periodEnd'],r.get('periodMonths',3))),collectionErrors=errors)
    OUT.write_text(json.dumps(current,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    print('REPORTS',len(existing),'ERRORS',len(errors),flush=True)
if __name__=='__main__':main()
