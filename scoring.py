"""Transparent snapshot research model. No imputation or historical backtest claim."""
import math
import statistics

WEIGHTS = {'valuation': 30, 'growth': 25, 'quality': 20, 'revisions': 15, 'risk': 10}
SPECIAL = {'JPM': 'bank', 'ALV': 'insurance', 'G': 'insurance', 'O': 'reit',
           'ARCC': 'bdc', 'BRK.B': 'holding', 'KRP': 'royalty'}
LABELS = {'operating': 'Operativ', 'bank': 'Bank', 'insurance': 'Versicherung',
          'reit': 'REIT', 'bdc': 'BDC', 'holding': 'Holding', 'royalty': 'Royalty'}


def number(x):
    if isinstance(x, bool):
        return None
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (ValueError, TypeError):
        return None


def scale(value, low, high, points):
    return round(max(0, min(1, (value-low)/(high-low))) * points, 2)


def score(quote, history, fundamental, revision):
    profile = SPECIAL.get(quote['ticker'], 'operating')
    parts = {k: None for k in WEIGHTS}
    reasons = {k: 'Keine aktuellen, geeigneten Eingabedaten.' for k in WEIGHTS}
    details = {}
    fresh = fundamental.get('status') == 'fresh' and quote.get('status') == 'cached'
    operating = profile == 'operating'
    pe = number(quote.get('peTTM'))
    if fresh and operating and pe is not None and pe > 0:
        parts['valuation'] = scale(pe, 40, 10, 30)
        details['valuation'] = f'TTM-P/E {pe:.2f}×. Linear: ≤10× = 30 P.; ≥40× = 0 P.'
    if fresh and operating:
        for key, field, low, high, weight, label in [
            ('growth', 'revenueGrowth', -.05, .25, 25, 'Umsatzwachstum ggü. Vorjahr (Anbieter)'),
            ('quality', 'operatingMargins', 0, .30, 20, 'Operative Marge (Anbieter)')]:
            value = number(fundamental.get(field))
            if value is not None:
                parts[key] = scale(value, low, high, weight)
                details[key] = f'{label}: {value*100:.2f}%. Linear: {low*100:g}% = 0 P.; {high*100:g}% = {weight} P.'
    if not operating:
        for key in ('valuation', 'growth', 'quality', 'revisions'):
            reasons[key] = 'Sonderprofil: Das operative Modell ist hier nicht freigegeben; keine Ersatzbewertung.'
    current, old = number(revision.get('current')), number(revision.get('30daysAgo'))
    analysts = number(revision.get('numberOfAnalysts'))
    if fresh and profile in ('operating','bank','insurance') and revision.get('status') == 'fresh' and current is not None and old is not None and old > 0 and current > 0 and analysts is not None and analysts >= 3:
        change = current/old - 1
        parts['revisions'] = scale(change, -.10, .10, 15)
        details['revisions'] = f'EPS-Konsens +1y: {current:.4g} vs. {old:.4g} vor 30 Tagen ({change*100:+.2f}%; {int(analysts)} Analysten). −10% = 0 P.; +10% = 15 P.'
    else:
        if profile in ('operating','bank','insurance'):
            reasons['revisions'] = 'Benötigt +1y-EPS aktuell und vor 30 Tagen, beide positiv, sowie mindestens 3 Analysten.'
    prices = [number(p.get('adjustedClose')) for p in history[-253:]]
    if quote.get('status') == 'cached' and len(prices) >= 201 and all(p is not None and p > 0 for p in prices):
        returns = [math.log(b/a) for a, b in zip(prices, prices[1:])]
        vol = statistics.stdev(returns) * math.sqrt(252)
        parts['risk'] = scale(vol, .60, .15, 10)
        peak = prices[0]
        drawdown = 0
        for p in prices:
            peak = max(peak, p)
            drawdown = min(drawdown, p/peak - 1)
        details['risk'] = f'Annualisierte Tagesvolatilität {vol*100:.2f}% über {len(returns)} Handelstage. ≤15% = 10 P.; ≥60% = 0 P. Adjustierte Kursreihe.'
        risk_metrics = {'volatilityPct': round(vol*100, 3), 'maxDrawdownPct': round(drawdown*100, 3), 'observations': len(returns)}
    else:
        reasons['risk'] = 'Benötigt aktuellen Kurs und mindestens 201 gültige adjustierte Tagesschlusskurse.'
        risk_metrics = {}
    specialist = fundamental.get('specialist', {})
    raw = specialist.get('raw', {}) if specialist.get('status') == 'fresh' else {}
    def put(key, value, low, high, label):
        value = number(value)
        if value is not None:
            parts[key] = scale(value, low, high, WEIGHTS[key])
            details[key] = f'{label}: {value:.4g}. Linear: {low:g} = 0 P.; {high:g} = {WEIGHTS[key]} P.'
    if fresh and profile in ('bank','insurance'):
        pb = number(fundamental.get('priceToBook'))
        if pb is not None and pb > 0:
            put('valuation', pb, 2.5, 1.0, 'Kurs/Buchwert (Anbieter)')
        put('growth', fundamental.get('earningsGrowth'), -.05, .20, 'Gewinnwachstum ggü. Vorjahr, Anteil')
        put('quality', fundamental.get('returnOnEquity'), .05, .20 if profile=='bank' else .18, 'Eigenkapitalrendite (ROE), Anteil')
        for key in ('valuation','growth','quality'):
            if parts[key] is None: reasons[key]='Branchenmodell benötigt positives P/B, Gewinnwachstum bzw. ROE. Kein Ersatz durch Umsatz/operative Marge.'
    if quote.get('status')=='cached' and raw and specialist.get('currency')==quote.get('currency'):
        if profile=='reit':
            qs=raw.get('affoQuarterPerShare', [])
            if len(qs)==4 and all(number(v) is not None and v>0 for v in qs):
                affo=sum(qs)
                put('valuation',quote['price']/affo,25,12,'Preis / gemeldetes AFFO je Aktie (Summe vier Quartale)')
                previous=number(raw.get('affoQuarterPerShareYearAgo'))
                if previous and previous>0: put('growth',qs[-1]/previous-1,-.02,.10,'AFFO je Aktie, Quartal ggü. Vorjahr, Anteil')
            div=number(raw.get('dividendsPaidThousands')); cash=number(raw.get('affoAvailableThousands'))
            if div and div>0 and cash is not None: put('quality',cash/div,.9,1.5,'AFFO / gezahlte Ausschüttungen im Quartal')
            cur=[number(raw.get('guidanceCurrentLow')),number(raw.get('guidanceCurrentHigh'))]
            old=[number(raw.get('guidancePreviousLow')),number(raw.get('guidancePreviousHigh'))]
            if all(x is not None and x>0 for x in cur+old):
                put('revisions',sum(cur)/sum(old)-1,-.05,.05,'Änderung AFFO-Guidance-Mittelwert für dasselbe Fiskaljahr, Anteil (Emittent, kein Analystenkonsens)')
        elif profile=='bdc':
            nav=number(raw.get('navPerShare'));old=number(raw.get('navPreviousPerShare'))
            if nav and nav>0:
                put('valuation',quote['price']/nav,1.5,.8,'Kurs / berichteter NAV je Aktie')
                if old and old>0: put('growth',nav/old-1,-.05,.10,'NAV je Aktie ggü. '+str(raw.get('navPreviousDate'))+', Anteil (kein YoY)')
            nii=number(raw.get('niiQuarterPerShare')); div=number(raw.get('dividendQuarterPerShare')); lev=number(raw.get('debtToEquity'))
            if nii is not None and div and div>0 and lev is not None and lev>=0:
                coverage_score=scale(nii/div,.8,1.3,10)
                leverage_score=scale(lev,2,.5,10)
                parts['quality']=round(coverage_score+leverage_score,2)
                details['quality']=f'NII/Quartalsdividende {nii/div:.3f} (0.8→0, 1.3→10 P.) + Debt/Equity {lev:.2f} (2→0, 0.5→10 P.). Keine Kreditqualitätsprüfung.'
            reasons['revisions']='NII-Konsensrevisionen fehlen; GAAP-EPS-Revisionen sind kein Ersatz.'
        elif profile=='royalty':
            cash=number(raw.get('cashAvailableQuarterPerUnit')); div=number(raw.get('distributionQuarterPerUnit'))
            if cash is not None and cash>0 and quote.get('price') and quote['price']>0:
                put('valuation',cash*4/quote['price'],.06,.16,'Annualisierte Cash-available-Rendite aus einem Quartal; kein TTM und keine Prognose')
            if cash is not None and div and div>0:
                put('quality',cash/div,.8,1.5,'Cash available / Ausschüttung je Unit im Quartal')
            reasons['growth']='Vergleichbarer Vorjahreswert des Cash available je Unit fehlt.'
            reasons['revisions']='Revisionen des ausschüttbaren Cashflows fehlen; EPS-Konsens nicht verwendet.'
    if fresh and profile=='holding':
        pb=number(fundamental.get('priceToBook'))
        if pb is not None and pb>0: put('valuation',pb,2,1,'P/B-Buchwertproxy; kein Look-through-NAV / innerer Wert')
        reasons['growth']='Vergleichbares Buchwertwachstum je Aktie derselben Aktienklasse fehlt.'
        reasons['quality']='Look-through-Erträge und geprüfte Liquiditäts-/Verschuldungsdaten fehlen; GAAP-ROE nicht ersatzweise verwendet.'
        reasons['revisions']='EPS-Revisionen durch unrealisierte Anlagegewinne verzerrbar; keine Freigabe.'
    if quote.get('validation',{}).get('valuationBlocked'):
        parts['valuation']=None
        details.pop('valuation',None)
        reasons['valuation']='Datenprüfung meldet Abweichung: Bewertungs-Komponente bis zur Klärung gesperrt.'
    for key in list(reasons):
        if parts[key] is not None: reasons.pop(key,None)

    coverage = sum(WEIGHTS[k] for k, v in parts.items() if v is not None)
    partial = round(sum(v for v in parts.values() if v is not None), 2)
    complete = coverage == 100
    return {'model': 'Transparent Research V7.2', 'modelVersion':'research-v7.2.0', 'sectorLabel': LABELS[profile],
            'profile': profile, 'parts': parts, 'weights': WEIGHTS, 'explanation': details,
            'missingReasons': {k: v for k, v in reasons.items() if parts[k] is None},
            'coveragePoints': coverage, 'partialPoints': partial, 'complete': complete,
            'total': partial if complete else None, 'riskMetrics': risk_metrics,
            'growthMetrics': {'growthPct': (fundamental.get('revenueGrowth')*100 if number(fundamental.get('revenueGrowth')) is not None else None)},
            'scope': 'Profilabhängiges heuristisches Momentbild (Bank/Versicherung ohne CET1-/Solvenzbewertung);  Vergleich nur bei gleichem Profil und ähnlicher Branche. Keine Kaufempfehlung, kein validierter Backtest.'}
