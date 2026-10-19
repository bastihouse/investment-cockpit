"""Report review queue: provider period changes + dated official issuer feeds.
Detection never changes curated financial inputs or claims an independent validation.
"""
import concurrent.futures as cf
import datetime as dt
import email.utils
import hashlib
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import calendar
from html.parser import HTMLParser
from pathlib import Path
from historical_sources import load_reports

FEEDS={
 'AAPL':'https://www.apple.com/newsroom/rss-feed.rss',
 'MSFT':'https://news.microsoft.com/feed/',
 'NVDA':'https://nvidianews.nvidia.com/releases.xml',
 'META':'https://investor.atmeta.com/rss/pressrelease.aspx',
 'AMZN':'https://ir.aboutamazon.com/rss/news-releases.xml',
 'GOOGL':'https://abc.xyz/investor/rss/news-releases.xml'}
SEC={'MSFT':789019,'AAPL':320193,'NVDA':1045810,'GOOGL':1652044,'META':1326801,'AMZN':1018724,'JPM':19617,'O':726728,'ARCC':1287750,'BRK.B':1067983}
CATALOGS={
 'JPM':'https://www.jpmorganchase.com/services/json/v1/investor-relations/quarterly-earnings.json',
 'ALV':'https://www.allianz.com/en/investor_relations/results-reports/results.html',
 'ENR':'https://www.siemens-energy.com/global/en/home/investor-relations/publications-ad-hoc.html'}
RESULT=re.compile(r'(?:financial results|quarter(?:ly)? results|quarter.{0,30}earnings|reports.{0,40}quarter|earnings release|full.year results)',re.I)
SCHEDULE=re.compile(r'(?:schedules?|to (?:announce|report|webcast)|conference call|announces? date|will (?:announce|report))',re.I)

class CatalogLinks(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.current=None
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.current=[dict(attrs).get('href',''),'']
    def handle_data(self,data):
        if self.current is not None:self.current[1]+=data+' '
    def handle_endtag(self,tag):
        if tag=='a' and self.current is not None:self.links.append(self.current);self.current=None

def parse_catalog(body,ticker,url,today):
    """Detect original report links without inventing a publication timestamp.
    Catalog fiscal quarter labels are not publication dates and never enter scoring.
    """
    rows=[]
    if ticker=='JPM':
        for item in json.loads(body)['items']:
            y=int(item['year']);q=int(item['quarter'][0]);doc=item.get('docs',{}).get('pressRelease',{})
            if q not in range(1,5):raise ValueError('Invalid catalog quarter')
            if doc.get('link'):rows.append((y,q,doc['link'],doc.get('title','Earnings press release')))
    else:
        parser=CatalogLinks();parser.feed(body.decode('utf-8'))
        for link,label in parser.links:
            if '.pdf' not in link.lower():continue
            if ticker=='ALV':
                m=re.search(r'results/(20\d{2})[-_](1q|2q|3q|4q|fy)',link,re.I)
                if not m or 'release' not in link.lower():continue
                y=int(m[1]);q=4 if m[2].lower()=='fy' else int(m[2][0])
            else:
                m=re.search(r'Q([1-4])\s*FY\s*(20)?(\d{2})|Q([1-4])[-_ ]*(?:FY)?[-_ ]*(20\d{2})',label+' '+link,re.I)
                if not m or 'earnings' not in (label+' '+link).lower():continue
                q=int(m[1] or m[4]);y=int('20'+m[3]) if m[3] else int(m[5])
            rows.append((y,q,link,label.strip() or f'{y} Q{q} Ergebnisbericht'))
    if not rows:raise ValueError('Official catalog structure/report links not recognized')
    out={}
    for year,q,link,title in rows:
        month=q*3;cy=year
        if ticker=='ENR':month={1:12,2:3,3:6,4:9}[q];cy=year-1 if q==1 else year
        end=dt.date(cy,month,calendar.monthrange(cy,month)[1])
        if end>=today or (today-end).days>400:continue
        link=urllib.parse.urljoin(url,link);parsed=urllib.parse.urlparse(link)
        domains={'JPM':('jpmorganchase.com',),'ALV':('allianz.com',),'ENR':('siemens-energy.com',)}[ticker]
        if parsed.scheme!='https' or not any(parsed.hostname==d or (parsed.hostname or '').endswith('.'+d) for d in domains):continue
        key=hashlib.sha256((ticker+'|'+link).encode()).hexdigest()[:20]
        out[key]={'id':key,'ticker':ticker,'title':title[:250],'publishedAt':None,'periodEnd':end.isoformat(),
                  'url':link,'sourceFeed':url,'state':'needs-review','sourceType':'issuer-catalog',
                  'meaning':'Originalbericht im offiziellen Emittentenkatalog. Periode aus Katalogbezeichnung; Veröffentlichungsdatum und Finanzzahlen noch nicht geprüft.'}
    return list(out.values())

def fetch_catalog(ticker,url,today):
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'InvestmentCockpit public research https://github.com/bastihouse/investment-cockpit'})
        with urllib.request.urlopen(request,timeout=12) as response:body=response.read(4_000_000)
        hits=parse_catalog(body,ticker,url,today)
        return {'ticker':ticker,'url':url,'status':'available','type':'Emittenten-Berichtskatalog','matches':len(hits)},hits
    except Exception as e:return {'ticker':ticker,'url':url,'status':'unavailable','type':'Emittenten-Berichtskatalog','error':str(e)[:180]},[]

def parse_feed(body,ticker,url,today):
    root=ET.fromstring(body);out=[]
    if root.tag not in ('rss','{http://www.w3.org/2005/Atom}feed'):
        raise ValueError('Expected RSS/Atom feed, received a different document')
    for item in [*root.findall('.//item'),*root.findall('.//{http://www.w3.org/2005/Atom}entry')]:
        value=lambda k:next((c.text or '' for c in item if c.tag.split('}')[-1]==k),'').strip()
        title=value('title')
        if not RESULT.search(title) or SCHEDULE.search(title):continue
        link=value('link')
        if not link:
            link=next((c.get('href','') for c in item if c.tag.split('}')[-1]=='link'),'')
        stamp=value('pubDate') or value('published') or value('updated')
        try:
            try:day=dt.datetime.fromisoformat(stamp.replace('Z','+00:00')).date()
            except ValueError:day=email.utils.parsedate_to_datetime(stamp).date()
        except (ValueError,TypeError,AttributeError):continue
        # Only links on the issuer feed's domain (Apple newsroom etc.); no arbitrary redirects.
        host=urllib.parse.urlparse(link).hostname or '';feedhost=urllib.parse.urlparse(url).hostname or ''
        if not (host==feedhost or host.endswith('.'+feedhost.removeprefix('www.'))):continue
        if day>today or (today-day).days>400:continue
        out.append({'id':hashlib.sha256((ticker+'|'+link).encode()).hexdigest()[:20],'ticker':ticker,
                    'title':title[:250],'publishedAt':day.isoformat(),'url':link,'sourceFeed':url,
                    'state':'needs-review','meaning':'Datierter Treffer im offiziellen Feed; Finanzzahlen und Berichtsperiode noch nicht geprüft.'})
    return out

def fetch_feed(ticker,url,today):
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'InvestmentCockpit public research https://github.com/bastihouse/investment-cockpit','Accept':'application/rss+xml,application/xml,text/xml'})
        with urllib.request.urlopen(request,timeout=12) as r:body=r.read(2_000_000)
        candidates=parse_feed(body,ticker,url,today)
        return {'ticker':ticker,'url':url,'status':'available','matches':len(candidates)},candidates
    except Exception as e:return {'ticker':ticker,'url':url,'status':'unavailable','error':str(e)[:180]},[]

def fetch_sec(ticker,cik,today):
    url=f'https://data.sec.gov/submissions/CIK{cik:010d}.json'
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'InvestmentCockpit public research https://github.com/bastihouse/investment-cockpit','Accept':'application/json'})
        with urllib.request.urlopen(request,timeout=12) as response:payload=json.load(response)
        if int(payload['cik'])!=cik:raise ValueError('Issuer CIK mismatch')
        recent=payload['filings']['recent'];out=[]
        for i,form in enumerate(recent['form']):
            if form not in ('10-Q','10-K') and not (form=='8-K' and '2.02' in recent.get('items',['']*len(recent['form']))[i]):continue
            day=dt.date.fromisoformat(recent['filingDate'][i])
            if day>today or (today-day).days>400:continue
            accession=recent['accessionNumber'][i].replace('-','');document=recent['primaryDocument'][i]
            link=f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}'
            period=recent.get('reportDate',['']*len(recent['form']))[i] or None
            # 8-K reportDate is the event date, not the fiscal period end; never equate them.
            if form=='8-K':period=None
            out.append({'id':hashlib.sha256((ticker+'|'+link).encode()).hexdigest()[:20],'ticker':ticker,
                        'title':f'{form} · '+('Finanzbericht '+period if period else 'Ergebnisveröffentlichung (Item 2.02)'),
                        'publishedAt':day.isoformat(),'periodEnd':period,'url':link,'sourceFeed':url,
                        'state':'needs-review','meaning':'Offizielle SEC-Einreichung; Kennzahlen noch nicht aus der Meldung geprüft.'})
        return {'ticker':ticker,'url':url,'status':'available','type':'SEC submissions','matches':len(out)},out
    except Exception as e:return {'ticker':ticker,'url':url,'status':'unavailable','type':'SEC submissions','error':str(e)[:180]},[]

def review_rows(snapshot,reports,specialists,previous,candidates):
    prior={r['ticker']:r for r in previous.get('stocks',[])};out=[]
    for q in snapshot.get('quotes',[]):
        ticker=q['ticker'];rs=[r for r in reports if r['ticker']==ticker]
        sp=specialists.get(ticker);known=[r['periodEnd'] for r in rs]+([sp['periodEnd']] if sp else [])
        covered=max(known) if known else None;pubs=[r['publishedAt'] for r in rs]+([sp['publishedAt']] if sp else [])
        last_pub=max(pubs) if pubs else None;reported=q.get('fundamentals',{}).get('reportDate');old=prior.get(ticker,{}).get('providerPeriodEnd')
        advanced=bool(old and reported and reported>old)
        pending=bool(reported and (not covered or reported>covered))
        hits=[c for c in candidates if c['ticker']==ticker and ((c.get('periodEnd') and (not covered or c['periodEnd']>covered)) or (not c.get('periodEnd') and c.get('publishedAt') and (not last_pub or c['publishedAt']>last_pub)))]
        state='new-period' if advanced else 'review-required' if hits or (pending and covered) else 'initial-source-needed' if not covered else 'covered-reference'
        out.append({'ticker':ticker,'name':q['name'],'providerPeriodEnd':reported,'previousProviderPeriodEnd':old,
                    'curatedPeriodEnd':covered,'curatedPublishedAt':last_pub,'state':state,'providerAdvanced':advanced,
                    'curationBehind':pending,'candidateIds':[c['id'] for c in hits],'officialFeed':FEEDS.get(ticker),
                    'note':'Anbieter-Berichtsende ist kein Veröffentlichungsdatum. covered-reference bestätigt nur eine hinterlegte Referenz, nicht das Fehlen neuerer Berichte.'})
    return out

def build(root,today=None,fetch=True):
    root=Path(root);today=today or dt.date.today();path=root/'data/report-monitor.json'
    previous=json.loads(path.read_text()) if path.exists() else {}
    snapshot=json.loads((root/'data/snapshot.json').read_text());reports,_,_=load_reports(root)
    special=json.loads((root/'data/sector-inputs.json').read_text());checks=[];candidates=[]
    if fetch:
        with cf.ThreadPoolExecutor(max_workers=3) as pool:
            for status,hits in pool.map(lambda j:fetch_feed(j[0],j[1],today),FEEDS.items()):checks.append(status);candidates.extend(hits)
        with cf.ThreadPoolExecutor(max_workers=3) as pool:
            for status,hits in pool.map(lambda j:fetch_sec(j[0],j[1],today),SEC.items()):checks.append(status);candidates.extend(hits)
        with cf.ThreadPoolExecutor(max_workers=3) as pool:
            for status,hits in pool.map(lambda j:fetch_catalog(j[0],j[1],today),CATALOGS.items()):checks.append(status);candidates.extend(hits)
    merged={c['id']:c for c in previous.get('candidates',[]) if (c.get('publishedAt') or c.get('periodEnd') or '')>=(today-dt.timedelta(days=400)).isoformat()}
    for c in candidates:
        old=merged.get(c['id'],{})
        c['firstDetectedAt']=old.get('firstDetectedAt',dt.datetime.now(dt.timezone.utc).isoformat())
        if not c.get('publishedAt') and old.get('publishedAt'):c['publishedAt']=old['publishedAt']
        merged[c['id']]=c
    rows=review_rows(snapshot,reports,special,previous,list(merged.values()))
    result={'schemaVersion':1,'checkedAt':dt.datetime.now(dt.timezone.utc).isoformat(),
            'policy':'Review queue only. Provider period advances are not independently verified earnings. Official feed hits never update curated raw financial inputs automatically.',
            'coverage':'Vergleich der Anbieter-Berichtsperioden für alle Aktien; offizielle Feed-/SEC-Prüfungen und zusätzliche Emittentenkataloge nur für ausdrücklich aufgeführte Unternehmen. Katalogperioden sind keine Veröffentlichungsdaten. Quellen können unvollständig sein; nicht erreichbare Quellen bleiben unbekannt.',
            'feedChecks':checks,'stocks':rows,'candidates':sorted(merged.values(),key=lambda c:(c.get('publishedAt') or c.get('periodEnd') or '',c['ticker']),reverse=True),
            'summary':{'stocks':len(rows),'newProviderPeriods':sum(r['providerAdvanced'] for r in rows),
                       'reviewRequired':sum(r['state'] in ('new-period','review-required') for r in rows),
                       'initialSourcesNeeded':sum(r['state']=='initial-source-needed' for r in rows),
                       'availableFeeds':sum(c['status']=='available' for c in checks),'attemptedFeeds':len(checks),
                       'availableIssuers':len({c['ticker'] for c in checks if c['status']=='available'}),
                       'attemptedIssuers':len({c['ticker'] for c in checks})}}
    path.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
    print('Berichtsmonitor:',result['summary']);return result
if __name__=='__main__':build(Path(__file__).resolve().parent)
