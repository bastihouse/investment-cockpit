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
from pathlib import Path

FEEDS={
 'AAPL':'https://www.apple.com/newsroom/rss-feed.rss',
 'MSFT':'https://news.microsoft.com/feed/',
 'NVDA':'https://nvidianews.nvidia.com/releases.xml',
 'META':'https://investor.atmeta.com/rss/news-releases.xml',
 'AMZN':'https://ir.aboutamazon.com/rss/news-releases.xml',
 'GOOGL':'https://abc.xyz/investor/rss/news-releases.xml'}
SEC={'MSFT':789019,'AAPL':320193,'NVDA':1045810,'GOOGL':1652044,'META':1326801,'AMZN':1018724,'JPM':19617,'O':726728,'ARCC':1287750,'BRK.B':1067983}
RESULT=re.compile(r'(?:financial results|quarter(?:ly)? results|quarter.{0,30}earnings|reports.{0,40}quarter|earnings release|full.year results)',re.I)
SCHEDULE=re.compile(r'(?:schedules?|to (?:announce|report|webcast)|conference call|announces? date|will (?:announce|report))',re.I)

def parse_feed(body,ticker,url,today):
    root=ET.fromstring(body);out=[]
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
        hits=[c for c in candidates if c['ticker']==ticker and ((c.get('periodEnd') and (not covered or c['periodEnd']>covered)) or (not c.get('periodEnd') and (not last_pub or c['publishedAt']>last_pub)))]
        state='new-period' if advanced else 'review-required' if hits or (pending and covered) else 'initial-source-needed' if not covered else 'covered-reference'
        out.append({'ticker':ticker,'name':q['name'],'providerPeriodEnd':reported,'previousProviderPeriodEnd':old,
                    'curatedPeriodEnd':covered,'curatedPublishedAt':last_pub,'state':state,'providerAdvanced':advanced,
                    'curationBehind':pending,'candidateIds':[c['id'] for c in hits],'officialFeed':FEEDS.get(ticker),
                    'note':'Anbieter-Berichtsende ist kein Veröffentlichungsdatum. covered-reference bestätigt nur eine hinterlegte Referenz, nicht das Fehlen neuerer Berichte.'})
    return out

def build(root,today=None,fetch=True):
    root=Path(root);today=today or dt.date.today();path=root/'data/report-monitor.json'
    previous=json.loads(path.read_text()) if path.exists() else {}
    snapshot=json.loads((root/'data/snapshot.json').read_text());bundle=json.loads((root/'data/historical-reports.json').read_text())
    extension=root/'data/historical-extensions.json'
    if extension.exists():bundle['reports']+=json.loads(extension.read_text())['reports']
    special=json.loads((root/'data/sector-inputs.json').read_text());checks=[];candidates=[]
    if fetch:
        with cf.ThreadPoolExecutor(max_workers=3) as pool:
            for status,hits in pool.map(lambda j:fetch_feed(j[0],j[1],today),FEEDS.items()):checks.append(status);candidates.extend(hits)
        with cf.ThreadPoolExecutor(max_workers=3) as pool:
            for status,hits in pool.map(lambda j:fetch_sec(j[0],j[1],today),SEC.items()):checks.append(status);candidates.extend(hits)
    merged={c['id']:c for c in previous.get('candidates',[]) if c.get('publishedAt','')>=(today-dt.timedelta(days=400)).isoformat()}
    for c in candidates:
        c['firstDetectedAt']=merged.get(c['id'],{}).get('firstDetectedAt',dt.datetime.now(dt.timezone.utc).isoformat());merged[c['id']]=c
    rows=review_rows(snapshot,bundle['reports'],special,previous,list(merged.values()))
    result={'schemaVersion':1,'checkedAt':dt.datetime.now(dt.timezone.utc).isoformat(),
            'policy':'Review queue only. Provider period advances are not independently verified earnings. Official feed hits never update curated raw financial inputs automatically.',
            'coverage':'Vergleich der Anbieter-Berichtsperioden für alle Aktien; datierte offizielle Feed-/SEC-Prüfungen nur für ausdrücklich aufgeführte Emittenten. RSS-Feeds können unvollständig sein; nicht erreichbare Quellen bleiben unbekannt.',
            'feedChecks':checks,'stocks':rows,'candidates':sorted(merged.values(),key=lambda c:(c['publishedAt'],c['ticker']),reverse=True),
            'summary':{'stocks':len(rows),'newProviderPeriods':sum(r['providerAdvanced'] for r in rows),
                       'reviewRequired':sum(r['state'] in ('new-period','review-required') for r in rows),
                       'initialSourcesNeeded':sum(r['state']=='initial-source-needed' for r in rows),
                       'availableFeeds':sum(c['status']=='available' for c in checks),'attemptedFeeds':len(checks)}}
    path.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
    print('Berichtsmonitor:',result['summary']);return result
if __name__=='__main__':build(Path(__file__).resolve().parent)
