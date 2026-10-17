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
    if fresh and operating and revision.get('status') == 'fresh' and current is not None and old is not None and old > 0 and current > 0 and analysts is not None and analysts >= 3:
        change = current/old - 1
        parts['revisions'] = scale(change, -.10, .10, 15)
        details['revisions'] = f'EPS-Konsens +1y: {current:.4g} vs. {old:.4g} vor 30 Tagen ({change*100:+.2f}%; {int(analysts)} Analysten). −10% = 0 P.; +10% = 15 P.'
    else:
        if operating:
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
    coverage = sum(WEIGHTS[k] for k, v in parts.items() if v is not None)
    partial = round(sum(v for v in parts.values() if v is not None), 2)
    complete = coverage == 100
    return {'model': 'Transparent Research V7.1', 'sectorLabel': LABELS[profile],
            'profile': profile, 'parts': parts, 'weights': WEIGHTS, 'explanation': details,
            'missingReasons': {k: v for k, v in reasons.items() if parts[k] is None},
            'coveragePoints': coverage, 'partialPoints': partial, 'complete': complete,
            'total': partial if complete else None, 'riskMetrics': risk_metrics,
            'growthMetrics': {'growthPct': (fundamental.get('revenueGrowth')*100 if number(fundamental.get('revenueGrowth')) is not None else None)},
            'scope': 'Heuristisches Momentbild; Vergleich nur bei gleichem Profil und ähnlicher Branche. Keine Kaufempfehlung, kein validierter Backtest.'}
