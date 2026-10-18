"""Fixed-rule retrospective diagnostics and separate forward observed validation.
No fitting/optimization, no trade at the signal close, no completed outcome before maturity.
"""
import calendar
import datetime as dt
import hashlib
import json
import math
import statistics as st
from collections import Counter,defaultdict
from pathlib import Path

SPLIT='2024-01-01'
VERSION='diagnostics-v1'
def add_months(day,months):
    d=dt.date.fromisoformat(day);n=d.year*12+d.month-1+months;y,m=divmod(n,12)
    return dt.date(y,m+1,min(d.day,calendar.monthrange(y,m+1)[1])).isoformat()

def ranks(xs):
    result=[0.]*len(xs);ordered=sorted(range(len(xs)),key=lambda i:xs[i]);i=0
    while i<len(xs):
        j=i+1
        while j<len(xs) and xs[ordered[j]]==xs[ordered[i]]:j+=1
        for k in ordered[i:j]:result[k]=(i+j-1)/2+1
        i=j
    return result

def rank_ic(rows):
    if len(rows)<4:return None
    a,b=ranks([r['score'] for r in rows]),ranks([r['returnPct'] for r in rows])
    if len(set(a))<2 or len(set(b))<2:return None
    return round(st.correlation(a,b),6)

def outcome(history,signal_date,horizon,asof):
    # Decision exists only after month end / observed publication: enter the NEXT close.
    prices=sorted([p for p in history if p.get('date') and p['date']<=asof and isinstance(p.get('adjustedClose'),(int,float)) and p['adjustedClose']>0],key=lambda p:p['date'])
    entry=next((p for p in prices if p['date']>signal_date),None)
    if not entry:return None,'entry-pending'
    if (dt.date.fromisoformat(entry['date'])-dt.date.fromisoformat(signal_date)).days>7:return None,'entry-gap'
    target=add_months(entry['date'],horizon)
    if target>asof:return None,'not-mature'
    end=next((p for p in prices if p['date']>=target),None)
    if not end:return None,'not-mature'
    if (dt.date.fromisoformat(end['date'])-dt.date.fromisoformat(target)).days>7:return None,'exit-gap'
    window=[p for p in prices if entry['date']<=p['date']<=end['date']]
    continuous=all((dt.date.fromisoformat(b['date'])-dt.date.fromisoformat(a['date'])).days<=10 for a,b in zip(window,window[1:]))
    risk_ok=len(window)>=horizon*16 and continuous
    peak=window[0]['adjustedClose'];dd=0
    for p in window:
        peak=max(peak,p['adjustedClose']);dd=min(dd,p['adjustedClose']/peak-1)
    returns=[math.log(b['adjustedClose']/a['adjustedClose']) for a,b in zip(window,window[1:])]
    return {'entryDate':entry['date'],'exitDate':end['date'],'targetDate':target,
            'returnPct':round((end['adjustedClose']/entry['adjustedClose']-1)*100,5),
            'maxDrawdownPct':round(dd*100,5) if risk_ok else None,
            'volatilityPct':round(st.stdev(returns)*math.sqrt(252)*100,5) if risk_ok and len(returns)>1 else None,
            'returnBasis':'Yahoo adjusted closes, retrieved today; dividend/split-adjusted proxy in trading currency, no FX or costs.'},None

def component_key(p):return '|'.join(k for k in ('valuation','growth','quality','revisions','risk') if (p.get('parts') or {}).get(k) is not None)
def sample(point,history,horizon,asof,kind,model):
    # Never pool partial scores with different component availability or profiles.
    if point.get('coveragePoints',0)<55 or point.get('parts',{}).get('growth') is None:return None,'insufficient-components'
    value=point.get('partialPoints')
    if not isinstance(value,(int,float)):return None,'no-score'
    result,reason=outcome(history,point['date'],horizon,asof)
    if result is None:return None,reason
    basis=point.get('inputs',{}).get('growthBasis') or ('observed-live-profile' if kind=='observed' else 'quarterly-yoy')
    return {'ticker':point['ticker'],'signalDate':point['date'],'score':value,'coverage':point['coveragePoints'],
            'components':component_key(point),'profile':point.get('profile'),'growthBasis':basis,
            'modelVersion':model,'kind':kind,'horizonMonths':horizon,**result},None

def summarize(rows):
    groups=defaultdict(list)
    for r in rows:groups[(r['signalDate'],r['profile'],r['coverage'],r['components'],r['growthBasis'])].append(r)
    ics=[v for rs in groups.values() if (v:=rank_ic(rs)) is not None]
    values=lambda key:[r[key] for r in rows if r.get(key) is not None]
    median=lambda xs:round(st.median(xs),5) if xs else None
    buckets=[]
    for lo,hi,label in [(0,40,'0–<40'),(40,60,'40–<60'),(60,101,'60+')]:
        rs=[r for r in rows if lo<=r['score']<hi]
        buckets.append({'label':label,'count':len(rs),'issuers':len(set(r['ticker'] for r in rs)),
                        'medianReturnPct':median([r['returnPct'] for r in rs]),
                        'medianMaxDrawdownPct':median([r['maxDrawdownPct'] for r in rs if r['maxDrawdownPct'] is not None])})
    return {'count':len(rows),'issuers':len(set(r['ticker'] for r in rows)),'cohorts':len(groups),
            'rankICCohorts':len(ics),'meanRankIC':round(st.mean(ics),5) if ics else None,
            'medianReturnPct':median(values('returnPct')),'medianMaxDrawdownPct':median(values('maxDrawdownPct')),
            'medianVolatilityPct':median(values('volatilityPct')),'buckets':buckets,
            'interpretation':'Deskriptiv; kleine Stichprobe, keine Signifikanz- oder Prognosebehauptung.'}

def build(root,today=None):
    root=Path(root);asof=(today or dt.date.today()).isoformat();data=json.loads((root/'data/reconstruction.json').read_text())
    universe=json.loads((root/'data/universe.json').read_text());histories={}
    for s in universe:
        p=root/'data/history'/(s['ticker']+'.json');histories[s['ticker']]=json.loads(p.read_text()).get('data',[]) if p.exists() else []
    rows=[];exclusions=Counter();summaries=[]
    # January / July or January only: fixed, non-overlapping anchors per ticker and horizon.
    for horizon in (6,12):
        for s in data['stocks']:
            last_exit=None
            for p in sorted(s['points'],key=lambda p:p['date']):
                month=int(p['date'][5:7])
                if month not in ((1,7) if horizon==6 else (1,)):continue
                r,reason=sample(p,histories[s['ticker']],horizon,asof,'retrospective',data['modelVersion'])
                if r is None:exclusions[reason]+=1;continue
                if last_exit and r['entryDate']<last_exit:exclusions['overlap-excluded']+=1;continue
                if r['signalDate']<SPLIT:
                    if r['exitDate']>=SPLIT:exclusions['purged-development-boundary']+=1;continue
                    r['partition']='development'
                else:r['partition']='test'
                last_exit=r['exitDate'];rows.append(r)
        # Individual profile / exact coverage / source period remain separate even in summaries.
        grouped=defaultdict(list)
        for r in rows:
            if r['horizonMonths']==horizon:grouped[(r['partition'],r['profile'],r['coverage'],r['components'],r['growthBasis'])].append(r)
        for (part,profile,coverage,components,basis),rs in sorted(grouped.items()):
            summaries.append({'modelVersion':data['modelVersion'],'horizonMonths':horizon,'partition':part,'profile':profile,'coverage':coverage,
                              'components':components,'growthBasis':basis,**summarize(rs)})
    # The observed branch cannot borrow reconstructed historical scores or backdate entry prices.
    observed=[];observed_pending=Counter();archive_path=root/'data/score-history.json'
    archive=json.loads(archive_path.read_text()) if archive_path.exists() else {'snapshots':[]}
    for horizon in (6,12):
        seen=set();last_exit={}
        for snapshot in archive.get('snapshots',[]):
            for q in snapshot.get('quotes',[]):
                # Monthly first observation per ticker + model; never mix model versions.
                k=(q['ticker'],snapshot['modelVersion'],snapshot['date'][:7])
                if k in seen:continue
                seen.add(k)
                signal=max(snapshot['date'],str(snapshot.get('observedAt') or snapshot['date'])[:10])
                p={**q,'date':signal}
                r,reason=sample(p,histories.get(q['ticker'],[]),horizon,asof,'observed',snapshot['modelVersion'])
                if r is None:observed_pending[reason]+=1
                else:
                    key=(q['ticker'],snapshot['modelVersion'])
                    if r['entryDate']<last_exit.get(key,''):observed_pending['overlap-excluded']+=1;continue
                    last_exit[key]=r['exitDate'];observed.append(r)
    observed_groups=defaultdict(list)
    for row in observed:observed_groups[(row['modelVersion'],row['horizonMonths'],row['profile'],row['coverage'],row['components'],row['growthBasis'])].append(row)
    observed_summary=[{'modelVersion':model,'horizonMonths':horizon,'partition':'observed','profile':profile,'coverage':coverage,'components':components,'growthBasis':basis,**summarize(rs)} for (model,horizon,profile,coverage,components,basis),rs in observed_groups.items()]
    result={'schemaVersion':1,'version':VERSION,'calculatedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'asOf':asof,
            'reconstructionModel':data['modelVersion'],'sourceBundleSha256':data['reportBundleSha256'],
            'splitDate':SPLIT,'development':'Signale vor 2024; Ergebnisfenster endet strikt vor 2024. Grenzüberschreitende Fenster ausgeschlossen.',
            'test':'Signale ab 2024; Regeln und Gewichte unverändert. Retrospektive Zeitteilung, kein historisch versiegelter Holdout.',
            'policy':['Keine Optimierung oder Anpassung von Gewichten anhand dieser Auswertung.',
                      'Einstieg erst zum nächsten verfügbaren Schlusskurs nach Signalmonat bzw. beobachteter Veröffentlichung; Ausstieg frühestens nach 6/12 Kalendermonaten.',
                      'Nur gereifte Ergebnisse. Feste Januar-/Juli-Anker bzw. Januar-Anker; überlappende Fenster je Aktie und Horizont ausgeschlossen.',
                      'Vergleiche nur innerhalb gleicher Modellversion, Branchenprofile, Komponentenabdeckung und Wachstumsperiode. Teilpunkte unverändert /100, kein Hochrechnen.',
                      'Rangkorrelation nur bei mindestens vier Aktien im selben Stichtags-/Profil-/Abdeckungssegment. Mittelwert über solche Kohorten, keine gepoolte Scheingenauigkeit.'],
            'limitations':['Heutiges Universum: Auswahl-/Survivorship-Bias; ausgeschiedene Unternehmen fehlen.',
                           'Heute abgerufene adjustierte Kursreihen und Emittentenmeldungen können nachträglich korrigiert sein; keine zertifizierte Point-in-time-Datenbank.',
                           'Die Regeln wurden heute entwickelt. Die rückblickende Zeitteilung ist keine unangetastete Out-of-sample-Prognoseprüfung.',
                           'Kleine Stichproben, Querschnittsabhängigkeiten, Steuern, Gebühren und Handelswährungsrisiko; keine Anlage- oder Erfolgsaussage.',
                           'Beobachtete Scores werden separat vorwärts ausgewertet. Noch nicht gereifte Horizonte bleiben offen.'],
            'retrospective':{'summary':summaries,'samples':rows,'excluded':dict(exclusions)},
            'observed':{'summary':observed_summary,'samples':observed,'matureCount':len(observed),'pending':dict(observed_pending),
                        'status':'mature' if observed else 'Noch keine gereiften beobachteten Ergebnisse; keine Rückrechnung als Ersatz.'}}
    (root/'data/evaluation.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    print(f'Score-Diagnostik: {len(rows)} rückblickende Stichproben; {len(observed)} gereifte beobachtete Ergebnisse.')
    return result
if __name__=='__main__':build(Path(__file__).resolve().parent)
