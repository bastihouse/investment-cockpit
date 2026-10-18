"""Monthly retrospective approximation using only releases published before the trading cutoff.
This is NOT an observed historical score and NOT a point-in-time vendor database.
"""
import calendar
import datetime as dt
import hashlib
import json
from pathlib import Path
from scoring import score
MODEL='research-v7.5-reconstruction-v1'

def month_ends(today, count=60):
    # Exclude the incomplete current month, never project a month-end into the future.
    end=today.replace(day=1)-dt.timedelta(days=1)
    result=[]
    for _ in range(count):
        result.append(end.isoformat())
        end=end.replace(day=1)-dt.timedelta(days=1)
    return sorted(result)

def inputs_at(reports, ticker, cutoff):
    available=[r for r in reports if r['ticker']==ticker and r['publishedAt']<cutoff and r['periodEnd']<=cutoff]
    by_end={}
    for r in sorted(available,key=lambda x:x['publishedAt']):by_end[(r['periodEnd'],r.get('periodMonths',3))]=r
    ordered=sorted(by_end.values(),key=lambda r:(r['periodEnd'],-r.get('periodMonths',3)))
    if not ordered:return {'status':'missing'},None,[]
    last=ordered[-1];age=(dt.date.fromisoformat(cutoff)-dt.date.fromisoformat(last['periodEnd'])).days
    if not 0<=age<=210:return {'status':'missing'},None,[]
    months=last.get('periodMonths',3);kind=last.get('kind','operating')
    facts={'status':'fresh','reportDate':last['periodEnd'],'currency':last.get('currency'),
           'growthBasis':last.get('growthBasis','quarterly-yoy'),'growthPeriodMonths':months,
           'accountingBasis':last.get('accountingBasis'),'qualityBasis':last.get('qualityBasis')}
    latest=[r for r in ordered if r.get('periodMonths',3)==3][-4:]
    contiguous=len(latest)==4 and all(70<=(dt.date.fromisoformat(b['periodEnd'])-dt.date.fromisoformat(a['periodEnd'])).days<=110 for a,b in zip(latest,latest[1:]))
    used=[last];eps=None
    if kind in ('bank','insurance'):
        prior=last.get('netIncomeYearAgo');value=last.get('netIncome')
        if prior and prior>0 and value is not None:facts['earningsGrowth']=value/prior-1
        facts.update(bookValuePerShare=last.get('bookValuePerShare'),returnOnEquity=last.get('returnOnEquity'))
        return facts,None,used
    if kind in ('reit','bdc'):
        raw=dict(last['specialist'])
        if kind=='reit' and contiguous:
            raw['affoQuarterPerShare']=[r['specialist']['affoQuarterPerShareValue'] for r in latest];used=latest
        facts['specialist']={'status':'fresh','currency':last['currency'],'raw':raw,'periodEnd':last['periodEnd'],'publishedAt':last['publishedAt'],'source':'Original issuer release','url':last['sourceUrl']}
        return facts,None,used
    if last.get('revenueYearAgo',0)>0:facts['revenueGrowth']=last['revenue']/last['revenueYearAgo']-1
    coefficients=[]
    if months==3 and contiguous:coefficients=[(r,1) for r in latest]
    elif months==12:coefficients=[(last,1)]
    elif months==6:
        year=int(last['periodEnd'][:4]);annual=by_end.get((f'{year-1}-12-31',12));half=by_end.get((f'{year-1}-06-30',6))
        if annual and half:coefficients=[(last,1),(annual,1),(half,-1)]
    if coefficients:
        used=[r for r,_ in coefficients]
        revenue=sum(r['revenue']*c for r,c in coefficients)
        if revenue>0 and all(r.get('operatingIncome') is not None for r,_ in coefficients):facts['operatingMargins']=sum(r['operatingIncome']*c for r,c in coefficients)/revenue
        verified=all(r.get('epsDiluted') is not None and (r.get('priceBasis')=='No stock split after 2020' or (r.get('priceBasisVerified') and isinstance(r.get('epsToPriceBasisFactor'),(int,float)) and r['epsToPriceBasisFactor']>=1)) for r,_ in coefficients)
        if verified:eps=sum(r['epsDiluted']/r.get('epsToPriceBasisFactor',1)*c for r,c in coefficients)
    return facts,eps,used

def reconstruct_point(stock,history,reports,month):
    known=[p for p in history if p['date']<=month]
    last=known[-1] if known else None
    # A missing monthly price cannot be replaced with an arbitrarily old close.
    valid=last is not None and 0<=(dt.date.fromisoformat(month)-dt.date.fromisoformat(last['date'])).days<=7
    cutoff=last['date'] if valid else month
    facts,eps,used=inputs_at(reports,stock['ticker'],cutoff) if valid else ({'status':'missing'},None,[])
    pe=last['close']/eps if valid and eps and eps>0 and facts.get('currency')==stock['currency'] else None
    book=facts.get('bookValuePerShare')
    if valid and book and book>0 and facts.get('currency')==stock['currency']:facts['priceToBook']=last['close']/book
    q={'ticker':stock['ticker'],'currency':stock['currency'],'price':last['close'] if valid else None,'status':'cached' if valid else 'missing','peTTM':pe}
    r=score(q,known,facts,{'status':'missing'})
    r.update(model='V7.5 historical reconstruction · unchanged weights and thresholds',modelVersion=MODEL)
    for key in ('valuation','growth','quality'):
        r['explanation'][key]=r['explanation'].get(key,'').replace('(Anbieter)','(veröffentlichte Quartalsmeldung)').replace('TTM-P/E','KGV-Näherung aus Quartals-EPS')
    if r['parts']['revisions'] is None:r['missingReasons']['revisions']='Geeignete historische Analysten- bzw. Emittentenrevisionen fehlen; keine heutigen Schätzungen eingesetzt.'
    if facts.get('qualityBasis') and r['parts']['quality'] is not None:r['explanation']['quality']+=' Basis: '+facts['qualityBasis']
    r['scope']='Rückrechnung mit heutigen Regeln und unveränderten Schwellen. Quartals-EPS-Summe als TTM-Näherung; kein damals gespeicherter Score und kein exakter historischer Anbieterquotient.'
    return {'date':month,'priceDate':last['date'] if valid else None,'ticker':stock['ticker'],'name':stock['name'],
            'profile':r['profile'],'price':q['price'],'currency':stock['currency'],'parts':r['parts'],
            'total':r['total'],'partialPoints':r['partialPoints'],'coveragePoints':r['coveragePoints'],
            'inputs':{'peApprox':round(pe,6) if pe else None,'epsQuarterSum':round(eps,6) if eps is not None else None,
                      'quarterRevenueGrowth':facts.get('revenueGrowth'),'operatingMarginTTM':facts.get('operatingMargins'),
                      'growthBasis':facts.get('growthBasis'),'growthPeriodMonths':facts.get('growthPeriodMonths'),
                      'earningsGrowth':facts.get('earningsGrowth'),'priceToBook':facts.get('priceToBook'),
                      'returnOnEquity':facts.get('returnOnEquity'),'qualityBasis':facts.get('qualityBasis'),
                      'accountingBasis':facts.get('accountingBasis'),'specialist':facts.get('specialist',{}).get('raw'),
                      'risk':r['riskMetrics'],'reportEnd':facts.get('reportDate')},
            'explanation':r['explanation'],'missingReasons':r['missingReasons'],
            'sources':[{'publishedAt':r['publishedAt'],'periodEnd':r['periodEnd'],'url':r['sourceUrl'],
                        'statementUrl':r.get('statementUrl'),'documentSha256':r['documentSha256'],
                        'epsDilutedReported':r.get('epsDiluted'),'epsToPriceBasisFactor':r.get('epsToPriceBasisFactor',1),
                        'splitEvents':r.get('splitEvents',[]),'priceBasisAsOf':r.get('priceBasisAsOf')} for r in used]}

def build(root,today=None):
    root=Path(root);today=today or dt.date.today()
    bundle_path=root/'data/historical-reports.json'
    bundle=json.loads(bundle_path.read_text())
    extension_path=root/'data/historical-extensions.json'
    extensions=json.loads(extension_path.read_text()) if extension_path.exists() else {'reports':[]}
    source_bundles={'historical-reports.json':hashlib.sha256(bundle_path.read_bytes()).hexdigest()}
    if extension_path.exists():source_bundles['historical-extensions.json']=hashlib.sha256(extension_path.read_bytes()).hexdigest()
    bundle['reports']=bundle['reports']+extensions['reports']
    universe=json.loads((root/'data/universe.json').read_text())
    months=month_ends(today);stocks=[]
    for s in universe:
        p=root/'data/history'/(s['ticker']+'.json')
        data=json.loads(p.read_text()).get('data',[]) if p.exists() else []
        history=sorted(data,key=lambda r:r['date'])
        points=[reconstruct_point(s,history,bundle['reports'],m) for m in months]
        stocks.append({'ticker':s['ticker'],'name':s['name'],'hasIssuerReports':any(r['ticker']==s['ticker'] for r in bundle['reports']),
                       'firstPriceDate':history[0]['date'] if history else None,'points':points})
    output={'schemaVersion':1,'modelVersion':MODEL,'calculatedAt':dt.datetime.now(dt.timezone.utc).isoformat(),
            'kind':'retrospective-reconstruction','monthEnds':months,'sourceBundles':source_bundles,'reportBundleSha256':hashlib.sha256(json.dumps(source_bundles,sort_keys=True).encode()).hexdigest(),
            'reportCount':len(bundle['reports']),'issuerTickers':sorted(set(r['ticker'] for r in bundle['reports'])),
            'method':'Fixed thresholds; original issuer quarterly/half-year/annual reporting periods remain labelled. Operating TTM uses four quarters, one annual statement, or current H1 + prior FY - prior H1. Verified same-currency EPS basis only. Bank/insurance reported profit/book/ROE and REIT/BDC specialist fields never replaced by operating-model metrics. Historical revisions missing. Release must precede actual trading cutoff; fundamentals expire 210 days after period end.',
            'limitations':['No historical consensus revisions or forward P/E. No normalized total score.',
                          'Not a contemporaneously archived vendor dataset; issuer web pages can change retrospectively. Document hash identifies the retrieved source, not a historical attestation.',
                          'EPS-sum approximations differ from exact diluted TTM EPS due to rounding and weighted-share changes. Originally reported EPS are divided by documented later split factors to match price units; raw EPS and split sources remain attached.',
                          'Yahoo adjusted histories are retrieved today and can be revised. Separate retrospective diagnostics do not establish predictive validation.',
                          'Universe selected today: survivorship/selection bias; missing reports and prices remain gaps.',
                          'Issuer coverage is listed in issuerTickers. Other stocks have only historical market-risk points. New issuer releases and split events must be added to the source bundle.'],
            'stocks':stocks}
    path=root/'data/reconstruction.json';path.write_text(json.dumps(output,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    print(f'Rekonstruktion: {len(months)} Monatsenden, {len(stocks)} Aktien, {len(bundle["reports"])} Primärberichte; kein vollständiger Gesamt-Score ohne Revisionen.')
    return output
if __name__=='__main__':build(Path(__file__).resolve().parent)
