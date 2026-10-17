"""Evidence-labelled plausibility checks; same-provider consistency != independent confirmation."""
import datetime as dt
import json
import time
import urllib.request
from scoring import number

UA = 'InvestmentCockpit/7.2 public research https://github.com/bastihouse/investment-cockpit'
SEC_SAMPLE = {'MSFT':'0000789019', 'AAPL':'0000320193', 'NVDA':'0001045810', 'JPM':'0000019617'}


def reported_eps(payload, now):
    rows = payload.get('facts', {}).get('us-gaap', {}).get('EarningsPerShareDiluted', {}).get('units', {}).get('USD/shares', [])
    unique = {}
    for r in rows:
        try:
            start, end, filed = (dt.date.fromisoformat(r[k]) for k in ('start','end','filed'))
            if filed > now or end > now or not 70 <= (end-start).days <= 110 or number(r.get('val')) is None:
                continue
            key = (start,end)
            if key not in unique or filed > unique[key][0]:
                unique[key] = (filed, float(r['val']), r.get('accn'))
        except (ValueError, KeyError):
            continue
    periods = sorted([(a,b,*v) for (a,b),v in unique.items()], key=lambda r:r[1])
    if len(periods)<4:
        return None
    last=periods[-4:]
    if any(abs((b[0]-a[1]).days)>7 for a,b in zip(last,last[1:])) or (now-last[-1][1]).days>210:
        return None
    return {'value':round(sum(x[3] for x in last),6), 'periodStart':last[0][0].isoformat(),
            'periodEnd':last[-1][1].isoformat(), 'filed':max(x[2] for x in last).isoformat(),
            'method':'Summe von vier gemeldeten Quartals-EPS (Diluted); kann wegen Verwässerung/Splits vom exakten TTM-EPS abweichen.',
            'accessions':[x[4] for x in last]}


def primary_checks(today):
    results={}
    for ticker,cik in SEC_SAMPLE.items():
        url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json'})
            with urllib.request.urlopen(req,timeout=15) as res:
                payload=json.load(res)
            eps=reported_eps(payload,today)
            results[ticker]={'state':'available' if eps else 'unavailable','source':'SEC Companyfacts', 'url':url,'eps':eps,
                             'note':None if eps else 'Keine vier eindeutig zusammenhängenden Quartals-EPS gefunden.'}
        except Exception as exc:
            results[ticker]={'state':'unavailable','source':'SEC Companyfacts','url':url,'eps':None,'note':str(exc)[:180]}
        time.sleep(.2)
    return results


def check_quote(q, primary=None):
    f=q.get('fundamentals',{})
    checks=[]
    def add(name,state,**kw): checks.append({'name':name,'state':state,**kw})
    p,provider=number(q.get('price')),number(f.get('providerPrice'))
    same_date=f.get('providerPriceDate')==q.get('marketDate')
    if p and provider and same_date:
        deviation=abs(p/provider-1)
        add('Schlusskurs ↔ Yahoo Quote','pass' if deviation<=.02 else 'warning',deviationPct=round(deviation*100,3),left=p,right=provider,
            independence='Gleicher Anbieter, nur Konsistenzprüfung',source='Yahoo Chart / Yahoo Quote',period=q.get('marketDate'))
    else:
        add('Schlusskurs ↔ Yahoo Quote','unavailable',note='Preis oder identischer Handelstag fehlt; kein Vergleich unterschiedlicher Zeitpunkte.')
    eps,pe=number(f.get('trailingEps')),number(q.get('peTTM'))
    if p and eps and eps>0 and pe and f.get('quoteCurrency')==q.get('currency') and f.get('financialCurrency')==q.get('currency'):
        derived=p/eps
        deviation=abs(derived/pe-1)
        add('P/E ↔ Kurs / Anbieter-EPS','pass' if deviation<=.08 else 'warning',deviationPct=round(deviation*100,3),left=pe,right=round(derived,4),
            independence='Gleicher Anbieter, keine unabhängige Bestätigung',source='Yahoo Quote',period='TTM nach Anbieter')
    else:
        add('P/E ↔ Kurs / Anbieter-EPS','unavailable',note='EPS, positiver Quotient oder eindeutig gleiche Berichts-/Handelswährung fehlen. ADRs werden nicht umgerechnet.')
    if primary is not None:
        r=primary.get('eps')
        if r and eps is not None and f.get('financialCurrency')=='USD' and f.get('quoteCurrency')=='USD':
            # Only compare when the annual period end matches the provider report end.
            if r['periodEnd']==f.get('reportDate') and abs(r['value'])>.00001:
                dev=abs(eps/r['value']-1)
                add('EPS ↔ SEC-Quartalsmeldungen','pass' if dev<=.15 else 'warning',left=eps,right=r['value'],deviationPct=round(dev*100,3),
                    source='SEC Companyfacts',url=primary['url'],period=r['periodStart']+' bis '+r['periodEnd'],
                    independence='Unabhängige Primärquelle für EPS; Preis nicht unabhängig geprüft.',note=r['method'])
            else:
                add('EPS ↔ SEC-Quartalsmeldungen','unavailable',source='SEC Companyfacts',url=primary['url'],note='Berichtsperioden stimmen nicht eindeutig überein; kein scheinbarer Bestätigungsvergleich.')
        else:
            add('EPS ↔ SEC-Quartalsmeldungen','unavailable',source='SEC Companyfacts',url=primary.get('url'),note=primary.get('note') or 'EPS-Basis nicht vergleichbar.')
    else:
        add('EPS ↔ SEC-Quartalsmeldungen','not-sampled',note='Nicht Teil der SEC-Stichprobe (MSFT, AAPL, NVDA, JPM).')
    warnings=[c for c in checks if c['state']=='warning']
    independent=any(c['state']=='pass' and c.get('source')=='SEC Companyfacts' for c in checks)
    return {'state':'warning' if warnings else 'primary-checked' if independent else 'consistent' if any(c['state']=='pass' for c in checks) else 'unverified',
            'valuationBlocked':bool(warnings), 'independentEPSConfirmed':independent,'checks':checks,
            'note':'Prüfungen bestätigen weder Fair Value noch den Zeitraum des Forward-P/E. Abweichungen sperren die Bewertungs-Komponente bis zur Klärung.'}
