"""Monthly retrospective approximation using only releases published before the trading cutoff.
This is NOT an observed historical score and NOT a point-in-time vendor database.
"""
import calendar
import datetime as dt
import hashlib
import json
from pathlib import Path
from scoring import score
MODEL='research-v7.2-reconstruction-v2'

def month_ends(today, count=60):
    # Exclude the incomplete current month, never project a month-end into the future.
    end=today.replace(day=1)-dt.timedelta(days=1)
    result=[]
    for _ in range(count):
        result.append(end.isoformat())
        end=end.replace(day=1)-dt.timedelta(days=1)
    return sorted(result)

def inputs_at(reports, ticker, cutoff):
    # Date-only releases are deliberately usable from the NEXT trading date.
    available=[r for r in reports if r['ticker']==ticker and r['publishedAt']<cutoff and r['periodEnd']<=cutoff]
    by_end={}
    for r in sorted(available,key=lambda x:x['publishedAt']):by_end[r['periodEnd']]=r
    latest=sorted(by_end.values(),key=lambda r:r['periodEnd'])[-4:]
    facts={'status':'missing'};pe_eps=None;used=[]
    if not latest:return facts,pe_eps,used
    last=latest[-1];age=(dt.date.fromisoformat(cutoff)-dt.date.fromisoformat(last['periodEnd'])).days
    if not 0<=age<=210:return facts,pe_eps,used
    facts={'status':'fresh','reportDate':last['periodEnd'],'revenueGrowth':last['revenue']/last['revenueYearAgo']-1}
    used=[last]
    contiguous=len(latest)==4 and all(70<=(dt.date.fromisoformat(b['periodEnd'])-dt.date.fromisoformat(a['periodEnd'])).days<=110 for a,b in zip(latest,latest[1:]))
    if contiguous:
        used=latest
        facts['operatingMargins']=sum(r['operatingIncome'] for r in latest)/sum(r['revenue'] for r in latest)
        # Match publication-date reported EPS to today's split-adjusted price units.
        # Split events change units only; financial values are still restricted by publication.
        if all(r.get('priceBasis')=='No stock split after 2020' or (r.get('priceBasisVerified') and isinstance(r.get('epsToPriceBasisFactor'),(int,float)) and r['epsToPriceBasisFactor']>=1) for r in latest):
            pe_eps=sum(r['epsDiluted']/r.get('epsToPriceBasisFactor',1) for r in latest)
    return facts,pe_eps,used

def reconstruct_point(stock,history,reports,month):
    known=[p for p in history if p['date']<=month]
    last=known[-1] if known else None
    # A missing monthly price cannot be replaced with an arbitrarily old close.
    valid=last is not None and 0<=(dt.date.fromisoformat(month)-dt.date.fromisoformat(last['date'])).days<=7
    cutoff=last['date'] if valid else month
    facts,eps,used=inputs_at(reports,stock['ticker'],cutoff) if valid else ({'status':'missing'},None,[])
    pe=last['close']/eps if valid and eps and eps>0 else None
    q={'ticker':stock['ticker'],'price':last['close'] if valid else None,'status':'cached' if valid else 'missing','peTTM':pe}
    r=score(q,known,facts,{'status':'missing'})
    r.update(model='V7.2 thresholds · historical reconstruction',modelVersion=MODEL)
    for key in ('valuation','growth','quality'):
        r['explanation'][key]=r['explanation'].get(key,'').replace('(Anbieter)','(veröffentlichte Quartalsmeldung)').replace('TTM-P/E','KGV-Näherung aus Quartals-EPS')
    r['missingReasons']['revisions']='Historischer Analystenkonsens nicht verfügbar; keine heutigen Schätzungen eingesetzt.'
    r['scope']='Rückrechnung mit heutigen V7.2-Schwellen. Quartals-EPS-Summe als TTM-Näherung; kein damals gespeicherter Score und kein exakter historischer Anbieterquotient.'
    return {'date':month,'priceDate':last['date'] if valid else None,'ticker':stock['ticker'],'name':stock['name'],
            'profile':r['profile'],'price':q['price'],'currency':stock['currency'],'parts':r['parts'],
            'total':r['total'],'partialPoints':r['partialPoints'],'coveragePoints':r['coveragePoints'],
            'inputs':{'peApprox':round(pe,6) if pe else None,'epsQuarterSum':round(eps,6) if eps is not None else None,
                      'quarterRevenueGrowth':facts.get('revenueGrowth'),'operatingMarginTTM':facts.get('operatingMargins'),
                      'risk':r['riskMetrics'],'reportEnd':facts.get('reportDate')},
            'explanation':r['explanation'],'missingReasons':r['missingReasons'],
            'sources':[{'publishedAt':r['publishedAt'],'periodEnd':r['periodEnd'],'url':r['sourceUrl'],
                        'statementUrl':r.get('statementUrl'),'documentSha256':r['documentSha256'],
                        'epsDilutedReported':r['epsDiluted'],'epsToPriceBasisFactor':r.get('epsToPriceBasisFactor',1),
                        'splitEvents':r.get('splitEvents',[]),'priceBasisAsOf':r.get('priceBasisAsOf')} for r in used]}

def build(root,today=None):
    root=Path(root);today=today or dt.date.today()
    bundle_path=root/'data/historical-reports.json'
    bundle=json.loads(bundle_path.read_text())
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
            'kind':'retrospective-reconstruction','monthEnds':months,'reportBundleSha256':hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
            'reportCount':len(bundle['reports']),'issuerTickers':sorted(set(r['ticker'] for r in bundle['reports'])),
            'method':'V7.2 thresholds; quarterly reported YoY revenue growth, sum-of-four-quarter operating margin, positive quarterly diluted EPS sum as TTM approximation, trailing adjusted daily volatility. No analyst revisions. Release must precede actual trading cutoff; fundamentals expire 210 days after period end.',
            'limitations':['No historical consensus revisions or forward P/E. No normalized total score.',
                          'Not a contemporaneously archived vendor dataset; issuer web pages can change retrospectively. Document hash identifies the retrieved source, not a historical attestation.',
                          'Quarterly EPS sum differs from exact diluted TTM EPS due to rounding and weighted-share changes. Originally reported EPS are divided by documented later split factors to match price units; raw EPS and split sources remain attached.',
                          'Yahoo adjusted histories are retrieved today and can be revised. No return-backtest or predictive validation.',
                          'Universe selected today: survivorship/selection bias; missing reports and prices remain gaps.',
                          'Issuer coverage is listed in issuerTickers. Other stocks have only historical market-risk points. New issuer releases and split events must be added to the source bundle.'],
            'stocks':stocks}
    path=root/'data/reconstruction.json';path.write_text(json.dumps(output,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    print(f'Rekonstruktion: {len(months)} Monatsenden, {len(stocks)} Aktien, {len(bundle["reports"])} Primärberichte; kein vollständiger Gesamt-Score ohne Revisionen.')
    return output
if __name__=='__main__':build(Path(__file__).resolve().parent)
