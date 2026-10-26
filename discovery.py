"""Evidence-aware gaps, comparable peer cohorts and fixed exploratory signals."""
import datetime as dt
import hashlib
import json
import math
import statistics as st
from collections import Counter,defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo
from scoring import WEIGHTS,number
from historical_sources import load_reports

def age(day,today):
    try:return (today-dt.date.fromisoformat(day[:10])).days
    except (ValueError,TypeError):return None

def percentage(value):
    value=number(value);return round(value*100,4) if value is not None else None

def fresh(q,today):
    f=q.get('fundamentals',{});a=age(q.get('marketDate'),today);b=age(f.get('reportDate'),today);c=age(f.get('fetchedAt'),today)
    return q.get('status')=='cached' and a is not None and 0<=a<=7 and f.get('status')=='fresh' and b is not None and 0<=b<=210 and c is not None and 0<=c<=7

def gaps(q,historical,check,today):
    r=q.get('researchScore') or {};parts=r.get('parts',{});blocked=q.get('validation',{}).get('blockedCategories',{})
    missing=[k for k in WEIGHTS if parts.get(k) is None];blocked_keys=[k for k in missing if k in blocked or (k=='valuation' and q.get('validation',{}).get('valuationBlocked'))]
    missing_weight=sum(WEIGHTS[k] for k in missing);blocked_weight=sum(WEIGHTS[k] for k in blocked_keys)
    verified=q.get('validation',{}).get('independentEPSConfirmed') or q.get('fundamentals',{}).get('specialist',{}).get('status')=='fresh'
    current_fresh=fresh(q,today);history_gap=not historical.get('reportCount')
    priority=1 if blocked_weight or not current_fresh or missing_weight>=30 else 2 if missing or history_gap or not verified else 3
    actions=[]
    if blocked_keys:actions.append('Gesperrte Eingaben und Aktien-/Währungsbasis prüfen')
    if not current_fresh:actions.append('Kurs- und Kennzahlenalter bzw. fehlenden Abruf klären')
    if missing:actions.append('Fehlende Kategorien anhand der aufgeführten Rohdaten ergänzen')
    if history_gap:actions.append('Erste datierte historische Primärberichte erfassen')
    elif historical.get('latestCoverage',0)<85:actions.append('Historische Abdeckung und offene Kennzahl-/Aktienbasis ergänzen')
    if not verified:actions.append('Verwendete Kennzahlen mit Emittentenbericht abgleichen')
    return {'priority':priority,'missingWeight':missing_weight,'blockedWeight':blocked_weight,'missingCategories':missing,'blockedCategories':blocked_keys,
            'currentFresh':current_fresh,'primaryScope':'EPS-Teilprüfung' if q.get('validation',{}).get('independentEPSConfirmed') else 'Kuratierte Spezialkennzahlen' if verified else 'Primärabgleich offen',
            'historyMissing':history_gap,'actions':actions,'reasons':{k:r.get('missingReasons',{}).get(k,'Geeignete Eingabe fehlt') for k in missing},
            'sourceStatus':check.get('status'),'sourceIssue':check.get('reason'),
            'meaning':'Fehlendes Modellgewicht beschreibt offene Kategorien, keine erwartete Score-Verbesserung. Primärprüfung ist eine separate Evidenzfrage.'}

def valuation(q,today):
    if not fresh(q,today) or (q.get('researchScore') or {}).get('parts',{}).get('valuation') is None:return None,None
    f=q.get('fundamentals',{});profile=q.get('sector')
    if q.get('currency')!=f.get('financialCurrency') or q.get('currency')!=f.get('quoteCurrency'):return None,None
    key='peTTM' if profile=='operating' else 'priceToBook' if profile in ('bank','insurance') else None
    value=number(q.get(key) if key=='peTTM' else f.get(key)) if key else None
    return (key,value) if value is not None and value>0 else (None,None)

def peer_cohorts(rows):
    grouped=defaultdict(list)
    for row in rows:
        if not row['currentFresh'] or not row.get('industry'):continue
        key=(row['modelVersion'],row['profile'],row['industry'],row['coverage'],row['componentSet'],tuple(sorted(row['weights'].items())))
        grouped[key].append(row)
    output=[]
    for key,members in grouped.items():
        entities={}
        for row in sorted(members,key=lambda r:(r['ticker']=='GOOG',r['ticker'])):entities.setdefault(row['issuerKey'],row)
        ratios=[r['valuationValue'] for r in entities.values() if r['valuationValue'] is not None]
        kinds={r['valuationKey'] for r in entities.values() if r['valuationValue'] is not None}
        median=st.median(ratios) if len(ratios)>=5 and len(kinds)==1 else None
        identifier=hashlib.sha256(repr(key).encode()).hexdigest()[:16]
        ordered=sorted(members,key=lambda r:(-(r['total'] if r['total'] is not None else r['partialPoints']),r['ticker']))
        output.append({'id':identifier,'profile':key[1],'industry':key[2],'coverage':key[3],'componentSet':key[4],
                       'modelVersion':key[0],'size':len(members),'issuers':len(entities),'members':[r['ticker'] for r in ordered],
                       'valuationKey':next(iter(kinds)) if len(kinds)==1 else None,'valuationMedian':median,'valuationCount':len(ratios),
                       'rankable':len(entities)>=3,'medianRule':'Mindestens fünf unterschiedliche Emittenten mit gleichem Bewertungsmaß; Aktienklassen einmal gezählt.'})
    return sorted(output,key=lambda g:(-g['size'],g['industry'],g['coverage']))

def drawdown(history,quote,today):
    if 'risk' in quote.get('validation',{}).get('blockedCategories',{}):return None
    rows=sorted([p for p in history if p.get('date','')<=today.isoformat() and number(p.get('adjustedClose')) is not None and p['adjustedClose']>0],key=lambda p:p['date'])[-252:]
    if len(rows)<201 or rows[-1]['date']!=quote.get('marketDate') or quote.get('status')!='cached':return None
    if any((dt.date.fromisoformat(b['date'])-dt.date.fromisoformat(a['date'])).days>11 or not .25<b['adjustedClose']/a['adjustedClose']<4 for a,b in zip(rows,rows[1:])):return None
    return {'pct':round((rows[-1]['adjustedClose']/max(p['adjustedClose'] for p in rows)-1)*100,4),'start':rows[0]['date'],'end':rows[-1]['date'],'observations':len(rows),'basis':'Abstand zum Hoch der letzten bis zu 252 vorhandenen adjustierten Handelsschlusskurse; Kursproxy, keine historische P/E-Bewertung.'}

def observed_change(q,old,model,old_model,today,old_day):
    a=q.get('researchScore') or {};b=(old or {}).get('researchScore') or {}
    result={'scoreDelta':None,'peChangePct':None,'baselineDate':old_day,'baselineState':'Keine passende frühere Beobachtung'}
    if not old or model!=old_model or q.get('sector')!=old.get('sector') or a.get('modelVersion')!=b.get('modelVersion') or a.get('weights')!=b.get('weights'):return result
    elapsed=age(old_day,today)
    if elapsed is None or not 1<=elapsed<=45 or not fresh(q,today) or not fresh(old,dt.date.fromisoformat(old_day)):return result
    price,old_price=number(q.get('price')),number(old.get('price'))
    shares,old_shares=number(q.get('fundamentals',{}).get('sharesOutstanding')),number(old.get('fundamentals',{}).get('sharesOutstanding'))
    if (price and old_price and not .25<price/old_price<4) or (shares and old_shares and not .5<shares/old_shares<2):
        result['baselineState']='Kurs-/Aktienbasis oder Kapitalstrukturwechsel zuerst prüfen';return result
    if a.get('complete') and b.get('complete') and a.get('coveragePoints')==b.get('coveragePoints')==100:
        result['scoreDelta']=round(a['total']-b['total'],4);result['baselineState']='Gleiches Modell, Profil, Gewichte und volle Abdeckung'
    f=q.get('fundamentals',{});g=old.get('fundamentals',{});pe=number(q.get('peTTM'));prior=number(old.get('peTTM'));eps=number(f.get('trailingEps'));prior_eps=number(g.get('trailingEps'))
    if q.get('sector')=='operating' and pe and prior and pe>0 and prior>0 and eps and prior_eps and prior_eps>0 and abs(eps/prior_eps-1)<.001 and f.get('reportDate')==g.get('reportDate') and q.get('currency')==old.get('currency') and f.get('financialCurrency')==g.get('financialCurrency')==q.get('currency') and not q.get('validation',{}).get('valuationBlocked') and not old.get('validation',{}).get('valuationBlocked'):
        result['peChangePct']=round((pe/prior-1)*100,4)
    return result

def signals(row,peer):
    hits=[];change=row['observedChange']
    if row['currentFresh'] and change['scoreDelta'] is not None and change['scoreDelta']>=5:hits.append({'kind':'score-rise','label':'Score mindestens +5 Punkte','value':change['scoreDelta'],'basis':'Gegenüber '+change['baselineDate']+' bei unverändertem Modell/Profil und 100% Abdeckung'})
    if row['currentFresh'] and change['peChangePct'] is not None and change['peChangePct']<=-10:hits.append({'kind':'pe-fall','label':'TTM-P/E mindestens 10% niedriger','value':change['peChangePct'],'basis':'Gegenüber '+change['baselineDate']+'; gleiche Berichtsperiode und nahezu unverändertes EPS'})
    median=(peer or {}).get('valuationMedian');value=row.get('valuationValue');parts=row['parts']
    if median and value and row['currentFresh'] and value<=median*.8 and parts.get('growth') is not None and parts.get('quality') is not None and parts['growth']>=5 and parts['quality']>=10:
        hits.append({'kind':'peer-value','label':'Bewertung mindestens 20% unter Peer-Median','value':round((value/median-1)*100,3),'basis':str(peer['valuationCount'])+' Emittenten · gleiches Profil, Branche und Modellabdeckung; Wachstum ≥5/25 und Qualität ≥10/20 Punkte'})
    d=row.get('drawdown')
    if row['currentFresh'] and d and d['pct']<=-20:hits.append({'kind':'pullback','label':'Mindestens 20% unter Kurshoch','value':d['pct'],'basis':d['basis']})
    return hits

def build(root,today=None):
    root=Path(root);snapshot=json.loads((root/'data/snapshot.json').read_text());today=today or dt.datetime.fromisoformat(snapshot['generatedAt']).astimezone(ZoneInfo('Europe/Vienna')).date()
    reconstruction=json.loads((root/'data/reconstruction.json').read_text());hist={s['ticker']:s for s in reconstruction['stocks']}
    reports,hashes,checks=load_reports(root);checkmap={r['ticker']:r for r in checks};by_ticker=defaultdict(list)
    for r in reports:by_ticker[r['ticker']].append(r)
    model=snapshot['scoreModelVersion'];baseline=None;old_model=None;old_day=None;old={}
    index_path=root/'data/score-history.json'
    if index_path.exists():
        entries=json.loads(index_path.read_text()).get('snapshots',[])
        entries=sorted([s for s in entries if s['modelVersion']==model and s['date']<today.isoformat()],key=lambda s:s['date'],reverse=True)
        for entry in entries:
            path=(root/entry['path']).resolve()
            if not path.is_relative_to((root/'data/snapshots').resolve()) or not path.exists():continue
            body=path.read_bytes()
            if hashlib.sha256(body).hexdigest()!=entry['sha256']:continue
            baseline=json.loads(body);old={q['ticker']:q for q in baseline['quotes']};old_model=baseline.get('scoreModelVersion');old_day=entry['date'];break
    rows=[]
    for q in snapshot['quotes']:
        ticker=q['ticker'];r=q.get('researchScore') or {};f=q.get('fundamentals',{});rs=by_ticker[ticker];points=hist.get(ticker,{}).get('points',[]);last=points[-1] if points else {}
        historical={'reportCount':len(rs),'firstPeriod':min((x['periodEnd'] for x in rs),default=None),'latestPeriod':max((x['periodEnd'] for x in rs),default=None),
                    'epsAuditedPeriods':sum(bool(x.get('epsBasisAudit')) for x in rs),
                    'monthsWithFundamentals':sum(any(p['parts'].get(k) is not None for k in ('valuation','growth','quality')) for p in points),
                    'latestCoverage':last.get('coveragePoints',0),'latestMonth':last.get('date'),
                    'latestParts':last.get('parts',{}),'originalUrl':max(rs,key=lambda x:x['publishedAt'])['sourceUrl'] if rs else None}
        historical['reports']=[{k:x.get(k) for k in ('periodEnd','publishedAt','periodMonths','currency','revenue','revenueYearAgo','operatingIncome','netIncome','netIncomeYearAgo','sourceUrl','documentSha256','sourceType','derivation','accession','basis','epsBasisAudit','epsTtmBasis','entityContinuity','releasePage')} for x in sorted(rs,key=lambda x:(x['periodEnd'],x.get('periodMonths',3)))]
        for report,original in zip(historical['reports'],sorted(rs,key=lambda x:(x['periodEnd'],x.get('periodMonths',3)))):
            report['periodMonths']=original.get('periodMonths',3)
            report['operandAccessions']=sorted({r['accn'] for r in original.get('sourceInputs',[])})
        issue=gaps(q,historical,checkmap.get(ticker,{}),today);vkey,vvalue=valuation(q,today);hp=root/'data/history'/(ticker+'.json')
        history=json.loads(hp.read_text()).get('data',[]) if hp.exists() else []
        alias='GOOGL' if ticker in ('GOOG','GOOGL') else ticker
        row={'ticker':ticker,'name':q['name'],'profile':q['sector'],'industry':f.get('industry'),'economicSector':f.get('sector'),
             'issuerKey':alias,'currency':q['currency'],'price':q.get('price'),'priceDate':q.get('marketDate'),'reportDate':f.get('reportDate'),
             'exchange':q.get('fundamentals',{}).get('exchange'),'originalUniverse':q.get('originalUniverse',True),'sp500Top100':q.get('sp500Top100'),
             'modelVersion':r.get('modelVersion',model),'weights':r.get('weights',WEIGHTS),'parts':r.get('parts',{}),
             'componentSet':'|'.join(k for k in WEIGHTS if r.get('parts',{}).get(k) is not None),'coverage':r.get('coveragePoints',0),
             'total':r.get('total'),'partialPoints':r.get('partialPoints',0),'currentFresh':issue['currentFresh'],
             'valuationKey':vkey,'valuationValue':vvalue,'growthPct':percentage(f.get('revenueGrowth' if q['sector']=='operating' else 'earningsGrowth')) if q['sector'] in ('operating','bank','insurance') else None,
             'qualityPct':percentage(f.get('operatingMargins' if q['sector']=='operating' else 'returnOnEquity')) if q['sector'] in ('operating','bank','insurance') else None,
             'historical':historical,'gaps':issue,'drawdown':drawdown(history,q,today),
             'observedChange':observed_change(q,old.get(ticker),model,old_model,today,old_day),
             'sourceUrl':f.get('specialist',{}).get('url') or f.get('sourceUrl'),'validationState':q.get('validation',{}).get('state')}
        rows.append(row)
    peers=peer_cohorts(rows);membership={ticker:g for g in peers for ticker in g['members']}
    for row in rows:
        cohort=membership.get(row['ticker']);row['peerGroup']=cohort['id'] if cohort else None;row['signals']=signals(row,cohort)
    result={'schemaVersion':1,'generatedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'snapshotAt':snapshot['generatedAt'],'asOf':today.isoformat(),'modelVersion':model,
            'sourceHashes':hashes,'snapshotSha256':hashlib.sha256((root/'data/snapshot.json').read_bytes()).hexdigest(),
            'baselineDate':old_day,'baselineMeaning':'Latest earlier, integrity-checked daily snapshot of the same model; missing stocks have no fabricated baseline.',
            'rows':rows,'peerGroups':peers,'summary':{'stocks':len(rows),'historicalStocks':sum(r['historical']['reportCount']>0 for r in rows),
                'periodRecords':len(reports),'primaryReports':len({r['sourceUrl'] for r in reports}),'priority1':sum(r['gaps']['priority']==1 for r in rows),'signals':dict(Counter(s['kind'] for r in rows for s in r['signals'])),
                'signalStocks':sum(bool(r['signals']) for r in rows),'baselineMissing':sum(r['observedChange']['scoreDelta'] is None for r in rows)},
            'policy':['Offenes Modellgewicht ist keine erwartete Punkteverbesserung. Primärprüfung und Datenabdeckung werden getrennt ausgewiesen.',
                      'Peer-Gruppen erfordern gleiches Modell, Profil, Branche, Kategorien und Abdeckung; Branchenbezeichnungen stammen vom Kennzahlenanbieter.',
                      'Signale verwenden feste, nicht optimierte Schwellen und kennzeichnen Recherchebedarf. Sie sind keine validierte Renditeprognose.',
                      'Neue historische SEC-Daten verwenden Einreichungsdaten und belegte USD-Konzepte. EPS-/Splitbasis und Analystenrevisionen bleiben gegebenenfalls offen.']}
    (root/'data/research-discovery.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    print('Research-Workbench:',result['summary']);return result

if __name__=='__main__':build(Path(__file__).resolve().parent)
