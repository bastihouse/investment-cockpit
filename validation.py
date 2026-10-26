"""Evidence-labelled plausibility checks; same-provider consistency != independent confirmation."""
import datetime as dt
import json
import time
import urllib.request
from scoring import number, SPECIAL

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


def check_quote(q, primary=None, issuer=None, history=None):
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
    profile=q.get('sector') or SPECIAL.get(q.get('ticker'),'operating')
    currency=q.get('currency'); same_currency=currency and f.get('quoteCurrency')==currency and f.get('financialCurrency')==currency
    if profile=='operating' and number(q.get('peTTM')) is not None and not same_currency:
        add('EPS-/Handelswährung','unavailable',blocks=['valuation'],note='Berichts- und Handelswährung bzw. ADR-EPS-Basis nicht eindeutig gleich. Keine unterstellte Wechselkurs- oder ADR-Umrechnung.')
    if profile in ('bank','insurance','holding') and f.get('status')=='fresh':
        book,pb=number(f.get('bookValue')),number(f.get('priceToBook'))
        if not same_currency or book is None or book<=0 or pb is None or pb<=0:
            add('Buchwert je Aktie / Währung','unavailable',blocks=['valuation'],note='Positiver Buchwert derselben Handels- und Berichtswährung erforderlich; Anbieterquotient allein reicht nicht.')
        else:
            derived=p/book if p and p>0 else None
            dev=abs(derived/pb-1) if derived else None
            add('P/B ↔ Kurs / Buchwert je Aktie','pass' if dev is not None and dev<=.10 else 'warning',blocks=[] if dev is not None and dev<=.10 else ['valuation'],left=pb,right=derived,deviationPct=round(dev*100,3) if dev is not None else None,independence='Gleicher Anbieter; keine Bestätigung der Aktienklasse.')
            if pb<.10 or pb>100:
                add('P/B-Einheiten und Aktienklasse','warning',blocks=['valuation'],note='Extremer Quotient: mögliche Aktienklassen- oder Einheitendifferenz. Keine automatische Skalierung; Prüfung erforderlich.')
        if q.get('ticker')=='BRK.B' and f.get('bookValueShareClass')!='BRK.B':
            add('Berkshire B: belegte Buchwert-Aktienklasse','unavailable',blocks=['valuation'],note='Buchwert der Klasse B nicht belegt. A/B-Faktor 1500 wird nicht stillschweigend eingesetzt.')
    if f.get('responseSymbol') and f['responseSymbol'].upper()!=str(q.get('yahoo','')).upper():
        add('Aktienidentität','warning',blocks=['valuation','growth','quality','revisions'],note='Antwortsymbol passt nicht zum angefragten Handelssymbol.')
    if history:
        jumps=[]
        for a,b in zip(history,history[1:]):
            x,y=number(a.get('adjustedClose')),number(b.get('adjustedClose'))
            if x and y and x>0 and y>0 and (y/x>4 or y/x<.25):jumps.append(b['date'])
        if jumps:add('Adjustierte Kursbasis / Splits','warning',blocks=['risk'],note='Mehr als Faktor 4 zwischen benachbarten adjustierten Schlüssen: '+', '.join(jumps[-3:])+'. Marktrisiko bis zur Prüfung gesperrt; kein automatischer Splitfaktor.')
    if issuer:
        reference=issuer.get('eps'); eps=number(f.get('trailingEps'))
        if reference and same_currency and issuer.get('currency')==currency and reference['periodEnd']==f.get('reportDate') and reference['value']>0 and eps is not None:
            dev=abs(eps/reference['value']-1)
            add('EPS ↔ Original-Emittentenmeldungen','pass' if dev<=.15 else 'warning',blocks=[] if dev<=.15 else ['valuation'],left=eps,right=reference['value'],deviationPct=round(dev*100,3),source='Issuer original releases',url=issuer['url'],period=reference['periodEnd'],independence='Primärquelle ausschließlich für die EPS-Näherung; Kurs und Konsens nicht bestätigt.',note='Vier gemeldete, auf die Kurs-Aktienbasis angepasste Quartals-EPS; Rundung und gewichtete Aktienzahlen können abweichen.',sourceReports=issuer['reports'])
        else:add('EPS ↔ Original-Emittentenmeldungen','unavailable',source='Issuer original releases',url=issuer.get('url'),note='Berichtsende, positive EPS-Summe, Währung oder Aktienbasis nicht vergleichbar; keine Bestätigung.')
    # Limited primary statement comparisons: exact period/definition, independent of EPS.
    statement_checks=[]
    reference_facts=(issuer or {}).get('facts',{})
    if profile=='operating' and issuer:
        aligned=reference_facts.get('reportDate')==f.get('reportDate') and reference_facts.get('status')=='fresh' and f.get('status')=='fresh'
        for field,title,threshold in [('revenueGrowth','Umsatzwachstum ↔ Originalabschluss',.03),('operatingMargins','TTM-Marge ↔ Originalabschluss',.03)]:
            left,right=number(f.get(field)),number(reference_facts.get(field))
            quarter_ok=field!='revenueGrowth' or reference_facts.get('growthPeriodMonths')==3
            valid=aligned and quarter_ok and left is not None and right is not None and issuer.get('currency')==f.get('financialCurrency')
            check={'name':title,'state':'pass' if valid and abs(left-right)<=threshold else 'warning' if valid else 'unavailable',
                   'blocks':[],'source':'Filed financial statements','url':issuer.get('url'),'period':f.get('reportDate'),
                   'independence':'Primärabgleich nur dieser Kennzahl; keine Bestätigung von Kurs, EPS oder Konsens.',
                   'note':'Gleiche Berichtsperiode und Währung; Wachstum nur Quartal/Vorjahresquartal, Marge aus belegtem TTM-Abschluss. Toleranz 3 Prozentpunkte. Diagnose ohne automatische Score-Freigabe.' if valid else 'Gleiche Periode, Währung oder passende Kennzahlendefinition fehlt; kein Bestätigungsabgleich.',
                   'sourceReports':issuer.get('reports',[])}
            if valid:check.update(left=left,right=right,deviationPp=round(abs(left-right)*100,4))
            checks.append(check);statement_checks.append(check)
    warnings=[c for c in checks if c['state']=='warning']
    independent=any(c['state']=='pass' and c.get('source') in ('SEC Companyfacts','Issuer original releases') for c in checks)
    blocked={}
    for c in checks:
        for key in c.get('blocks',['valuation'] if c['state']=='warning' else []):blocked.setdefault(key,[]).append(c['name'])
    return {'state':'warning' if warnings else 'primary-checked' if independent else 'consistent' if any(c['state']=='pass' for c in checks) else 'unverified',
            'valuationBlocked':'valuation' in blocked, 'blockedCategories':blocked, 'independentEPSConfirmed':independent,'independentFundamentalChecks':sum(c['state']=='pass' for c in statement_checks),'checks':checks,
            'note':'Prüfungen bestätigen weder Fair Value noch den Zeitraum des Forward-P/E. Abweichungen sperren die Bewertungs-Komponente bis zur Klärung.'}


def issuer_reference(ticker,bundle,today):
    from reconstruct import inputs_at
    cutoff=(today+dt.timedelta(days=1)).isoformat()
    facts,eps,used=inputs_at(bundle.get('reports',[]),ticker,cutoff)
    if not used:return None
    return {'eps':{'value':eps,'periodEnd':facts.get('reportDate')} if eps is not None else None,
            'currency':used[-1].get('currency'),'url':used[-1]['sourceUrl'],'facts':facts,
            'reports':[{'periodEnd':r['periodEnd'],'publishedAt':r['publishedAt'],'url':r['sourceUrl'],'sha256':r['documentSha256']} for r in used]}
