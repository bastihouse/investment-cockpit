#!/usr/bin/env python3
"""Free public data, no API keys. Independent price/fundamental status and no synthetic ratios."""
import datetime as dt
import json
import pathlib
import time
import concurrent.futures as cf
import urllib.parse
import urllib.request
from scoring import number, score, SPECIAL, LABELS
from validation import primary_checks, check_quote, issuer_reference
from archive import record_snapshot

ROOT = pathlib.Path(__file__).resolve().parent
UTC = dt.timezone.utc
NOW = dt.datetime.now(UTC)
TODAY = NOW.date()
STAMP = NOW.isoformat()
SOURCE = 'Yahoo Finance via yfinance (inoffiziell)'
CHART_BASIS = {}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')


def chart(symbol):
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(symbol, safe='') + f'?period1={int((NOW-dt.timedelta(days=6*366)).timestamp())}&period2={int(NOW.timestamp())}&interval=1d&events=div%2Csplits'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (InvestmentCockpitFree/7.1)', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=25) as response:
        payload = json.load(response)
    data = (payload.get('chart', {}).get('result') or [None])[0]
    if not data:
        raise ValueError('Kein Chart-Ergebnis')
    closes = (data.get('indicators', {}).get('quote') or [{}])[0].get('close', [])
    adjusted = (data.get('indicators', {}).get('adjclose') or [{}])[0].get('adjclose', [])
    history = []
    for idx, (ts, p) in enumerate(zip(data.get('timestamp', []), closes)):
        p = number(p)
        if p is None or p <= 0:
            continue
        day = dt.datetime.fromtimestamp(ts, UTC).date().isoformat()
        if day > TODAY.isoformat():
            continue
        row = {'date': day, 'close': round(p, 6)}
        adj = number(adjusted[idx]) if idx < len(adjusted) else None
        if adj is not None and adj > 0:
            row['adjustedClose'] = round(adj, 6)
        history.append(row)
    history = sorted({p['date']: p for p in history}.values(), key=lambda p: p['date'])
    if not history or (TODAY-dt.date.fromisoformat(history[-1]['date'])).days > 7:
        raise ValueError('Kein aktueller Tagesschluss innerhalb von 7 Tagen')
    currency = data.get('meta', {}).get('currency')
    CHART_BASIS[symbol] = sorted([
        {'tradingDate': dt.datetime.fromtimestamp(e['date'], UTC).date().isoformat(),
         'ratio': float(e['numerator']) / float(e['denominator'])}
        for e in data.get('events', {}).get('splits', {}).values()
        if e.get('denominator') and e.get('numerator') and e.get('date')
        and '2020-01-01' <= dt.datetime.fromtimestamp(e['date'], UTC).date().isoformat() <= TODAY.isoformat()
    ], key=lambda e: e['tradingDate'])
    return history, currency


def collect_fundamentals(symbol, price_date):
    """Provider P/E kept as supplied, never derive FY1/NTM from an unknown denominator."""
    import yfinance as yf
    stock = yf.Ticker(symbol)
    info = stock.get_info() or {}
    if info.get('symbol', '').upper() != symbol.upper():
        raise ValueError('Symbol in Kennzahlenantwort stimmt nicht überein')
    if not any(number(info.get(k)) is not None for k in ('trailingPE', 'forwardPE', 'revenueGrowth', 'operatingMargins')):
        raise ValueError('Keine geeigneten Kennzahlen geliefert')
    quarter = number(info.get('mostRecentQuarter'))
    report_date = dt.datetime.fromtimestamp(quarter, UTC).date() if quarter else None
    # Retrieval time is not a financial reporting date. Old/undated reports cannot receive score points.
    age = (TODAY-report_date).days if report_date else None
    status = 'fresh' if age is not None and 0 <= age <= 210 else 'unverified'
    facts = {k: number(info.get(k)) for k in ('trailingPE', 'forwardPE', 'trailingEps', 'forwardEps', 'revenueGrowth', 'operatingMargins', 'returnOnEquity', 'profitMargins', 'priceToBook', 'bookValue', 'returnOnAssets', 'earningsGrowth', 'regularMarketPrice')}
    facts.update(status=status, fetchedAt=STAMP, reportDate=report_date.isoformat() if report_date else None,
                 financialCurrency=info.get('financialCurrency'), quoteCurrency=info.get('currency'),
                 sector=info.get('sector'), industry=info.get('industry'), source=SOURCE,
                 sourceUrl='https://finance.yahoo.com/quote/'+urllib.parse.quote(symbol, safe='')+'/key-statistics/',
                 forwardBasis='Anbieterwert; FY1/NTM nicht unabhängig bestätigt',
                 periodNote='Umsatzwachstum und operative Marge nach Anbieterdefinition; jüngstes Berichtsdatum separat ausgewiesen.')
    facts.update(responseSymbol=info.get('symbol'),quoteType=info.get('quoteType'),sharesOutstanding=number(info.get('sharesOutstanding')),marketCap=number(info.get('marketCap')))
    market_time=number(info.get('regularMarketTime'))
    facts['providerPrice']=number(info.get('regularMarketPrice'))
    facts['providerPriceDate']=dt.datetime.fromtimestamp(market_time,UTC).date().isoformat() if market_time else None
    revision = {'status': 'missing', 'period': '+1y', 'fetchedAt': STAMP, 'source': SOURCE}
    try:
        trend = stock.get_eps_trend()
        estimate = stock.get_earnings_estimate()
        if trend is not None and '+1y' in trend.index and estimate is not None and '+1y' in estimate.index:
            row, est = trend.loc['+1y'], estimate.loc['+1y']
            revision.update(current=number(row.get('current')), **{'30daysAgo': number(row.get('30daysAgo'))},
                            numberOfAnalysts=number(est.get('numberOfAnalysts')), status='fresh')
    except Exception as exc:
        revision['error'] = str(exc)[:200]
    return facts, revision


def main():
    universe = json.loads((ROOT/'data/universe.json').read_text())
    old_snapshot = json.loads((ROOT/'data/snapshot.json').read_text())
    previous = {q['ticker']: q for q in old_snapshot['quotes']}
    record_snapshot(ROOT,old_snapshot)
    primaries=primary_checks(TODAY)
    report_bundle=json.loads((ROOT/'data/historical-reports.json').read_text())
    sector_path=ROOT/'data/sector-inputs.json'
    specialist_inputs=json.loads(sector_path.read_text()) if sector_path.exists() else {}
    quotes, errors, successes = [], [], 0
    def collect(stock):
        errors=[];successes=0
        ticker = stock['ticker']
        old = previous.get(ticker, {})
        profile = SPECIAL.get(ticker, 'operating')
        item = {**stock, 'price': None, 'ytdPricePct': None, 'peTTM': None, 'forwardPE': None,
                'marketDate': None, 'cachedAt': None, 'source': [], 'status': 'missing', 'attempts': {},
                'sector': profile, 'sectorLabel': LABELS[profile], 'fundamentals': {'status': 'missing'},
                'revision': {'status': 'missing'}, 'researchScore': None}
        histpath = ROOT/'data/history'/f'{ticker}.json'
        history = []
        try:
            history, currency = chart(stock['yahoo'])
            if currency and currency != stock['currency']:
                raise ValueError('Handelswährung stimmt nicht mit Aktienuniversum überein')
            last = history[-1]
            anchor = next((p for p in reversed(history) if p['date'] <= f'{TODAY.year-1}-12-31'), None)
            ytd = round((last['close']/anchor['close']-1)*100, 4) if anchor and last['date'].startswith(str(TODAY.year)) else None
            item.update(price=last['close'], ytdPricePct=ytd, marketDate=last['date'], cachedAt=STAMP,
                        source=['Yahoo Finance Chart (inoffiziell)'], status='cached')
            item['attempts']['history'] = {'status': 'ok', 'checkedAt': STAMP}
            write(histpath, {'source': 'Yahoo Finance Chart · Schlusskurse ohne Dividendenreinvestition', 'fetchedAt': STAMP,
                             'currency': stock['currency'], 'data': history, 'splitEvents': CHART_BASIS[stock['yahoo']],
                             'priceBasis': 'Provider split-adjusted close; adjustedClose also includes dividend adjustments'})
            successes += 1
        except Exception as exc:
            msg = str(exc)[:200]
            errors.append(f'{ticker}/history: {msg}')
            item['attempts']['history'] = {'status': 'error', 'checkedAt': STAMP, 'error': msg}
            if old.get('price') is not None:
                for field in ('price', 'ytdPricePct', 'marketDate', 'cachedAt', 'source'):
                    item[field] = old.get(field)
                item['status'] = 'stale'
            if histpath.exists():
                history = json.loads(histpath.read_text()).get('data', [])
        try:
            facts, revision = collect_fundamentals(stock['yahoo'], item.get('marketDate'))
            item['fundamentals'], item['revision'] = facts, revision
            for src, dest in [('trailingPE', 'peTTM'), ('forwardPE', 'forwardPE')]:
                value = number(facts.get(src))
                # Direct provider ratios only, same quoted currency; negative ratios remain non-meaningful.
                if value is not None and value > 0 and facts.get('quoteCurrency') == stock['currency'] and not (src == 'trailingPE' and number(facts.get('trailingEps')) is not None and facts['trailingEps'] <= 0):
                    item[dest] = value
            item['source'].append(SOURCE)
            item['attempts']['fundamentals'] = {'status': 'ok', 'checkedAt': STAMP}
        except Exception as exc:
            msg = str(exc)[:200]
            errors.append(f'{ticker}/fundamentals: {msg}')
            item['attempts']['fundamentals'] = {'status': 'error', 'checkedAt': STAMP, 'error': msg}
            if old.get('fundamentals', {}).get('fetchedAt'):
                item['fundamentals'] = {**old['fundamentals'], 'status': 'stale'}
                # Stale values remain only inside diagnostics; current displayed P/E is deliberately blank.
        special=specialist_inputs.get(ticker)
        if special:
            report=dt.date.fromisoformat(special['periodEnd'])
            published=dt.date.fromisoformat(special['publishedAt'])
            status='fresh' if 0<=(TODAY-report).days<=210 and published<=TODAY else 'stale'
            item['fundamentals']['specialist']={**special,'status':status,'maintenance':'Kuratierte Primärquelle; keine automatische Aktualisierung bei neuen Quartalsberichten.'}
        item['validation']=check_quote(item,primaries.get(ticker),issuer_reference(ticker,report_bundle,TODAY),history)
        if special:
            item['validation']['checks'].append({'name':'Emittenten-Spezialkennzahlen','state':'primary-reference' if status=='fresh' else 'unavailable','source':special['source'],'url':special['url'],'period':special['periodEnd'],'note':'Rohwerte manuell aus diesem Bericht geprüft; Aktualität neuerer Berichte nicht automatisch bestätigt.'})
        item['researchScore'] = score(item, history, item['fundamentals'], item['revision'])
        print(f"{ticker}: Kurs={item['status']} | P/E={item['peTTM']} | Forward={item['forwardPE']} | Abdeckung={item['researchScore']['coveragePoints']}/100", flush=True)
        time.sleep(.35)
        return item,errors,successes
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        for item,issues,success in pool.map(collect,universe):
            quotes.append(item);errors.extend(issues);successes+=success
    selection_path=ROOT/'data/sp500-selection.json'
    selection=json.loads(selection_path.read_text()) if selection_path.exists() else None
    snapshot = {'schemaVersion': 3, 'scoreModelVersion':'research-v7.5.0', 'generatedAt': STAMP, 'providerMode': 'GitHub Actions · Yahoo Chart + yfinance (kostenlos, inoffiziell)',
                'universeCount':len(universe),'universeSelection':{k:v for k,v in selection.items() if k!='holdings'} if selection else None,
                'fmpConfigured': False, 'refresh': {'running': False, 'finishedAt': dt.datetime.now(UTC).isoformat(),
                'processed': len(quotes), 'total': len(universe), 'lastError': '; '.join(errors[:5]) if errors else None}, 'quotes': quotes}
    snapshot['validationSummary']={
      'primaryEPSConfirmed':sum(q['validation']['independentEPSConfirmed'] for q in quotes),
      'warnings':sum(q['validation']['state']=='warning' for q in quotes),
      'consistent':sum(q['validation']['state']=='consistent' for q in quotes),
      'primarySample':len(set(primaries)|{r['ticker'] for r in report_bundle.get('reports',[]) if r.get('epsDiluted') is not None}),
      'secSample':len(primaries),
      'curatedPrimaryReports':sum(q['fundamentals'].get('specialist',{}).get('status')=='fresh' for q in quotes)}
    write(ROOT/'data/snapshot.json', snapshot)
    if successes:
        record_snapshot(ROOT,snapshot)
    providers = []
    categories = ['history', 'quote', 'ratios', 'income', 'estimates', 'key_metrics']
    for q in quotes:
        facts = q['fundamentals']
        states = {'history': 'fresh' if q['status'] == 'cached' else q['status'],
                  'quote': 'fresh' if q['status'] == 'cached' else q['status'],
                  'ratios': 'fresh' if q['peTTM'] is not None or q['forwardPE'] is not None else 'missing',
                  'income': 'fresh' if facts.get('status') == 'fresh' and number(facts.get('revenueGrowth')) is not None else 'missing',
                  'estimates': 'fresh' if q['revision'].get('status') == 'fresh' else 'missing',
                  'key_metrics': 'fresh' if facts.get('status') == 'fresh' and number(facts.get('operatingMargins')) is not None else 'missing'}
        providers.append({'ticker': q['ticker'], 'name': q['name'], 'sector': q['sector'], 'sectorLabel': q['sectorLabel'],
                          'providers': {k: {'state': states[k], 'source': 'Yahoo Chart' if k in ('history', 'quote') else SOURCE,
                          'lastAttempt': q['attempts'].get('history' if k in ('history', 'quote') else 'fundamentals'),
                          'reason': 'Status des letzten technischen Abrufs; keine unabhängige Finanzprüfung.'} for k in categories}})
    summary = {k: {**{state: sum(p['providers'][k]['state'] == state for p in providers) for state in ('fresh', 'stale', 'missing')},
                   'lastError': sum(p['providers'][k].get('lastAttempt', {}).get('status') == 'error' for p in providers), 'notApplicable': 0} for k in categories}
    write(ROOT/'data/provider-audit.json', {'generatedAt': STAMP, 'fmpConfigured': False, 'summary': summary, 'stocks': providers})
    print(f'Kurse: {successes}/{len(universe)} | P/E: {sum(q["peTTM"] is not None for q in quotes)} | Forward: {sum(q["forwardPE"] is not None for q in quotes)}')
    if not successes:
        raise SystemExit('Keine Kurse aktualisiert. Veröffentlichung abgebrochen.')

if __name__ == '__main__':
    main()
