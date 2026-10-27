"""Public ETF/FX closing series; independent, explicit cache status on failures."""
import concurrent.futures as cf
import datetime as dt
import json
from pathlib import Path
from update_data import chart

SPONSOR='https://www.ssga.com/us/en/individual/capabilities/equities/sector-investing/select-sector-etfs'
CATALOG=[('SPY','S&P 500 · SPY-Proxy','USD',None),('QQQ','Nasdaq-100 · QQQ-Proxy','USD',None),('EXSA.DE','STOXX Europe 600 · EXSA-Proxy','EUR',None),
 ('XLK','US-Technologie','USD','Technology'),('XLF','US-Finanzen','USD','Financial Services'),
 ('XLE','US-Energie','USD','Energy'),('XLV','US-Gesundheit','USD','Healthcare'),
 ('XLI','US-Industrie','USD','Industrials'),('XLY','US-zyklischer Konsum','USD','Consumer Cyclical'),
 ('XLP','US-Basiskonsum','USD','Consumer Defensive'),('XLU','US-Versorger','USD','Utilities'),
 ('XLB','US-Grundstoffe','USD','Basic Materials'),('XLRE','US-Immobilien','USD','Real Estate'),
 ('XLC','US-Kommunikation','USD','Communication Services'),
 ('GBPUSD=X','USD je GBP','USD','fx'),('CHFUSD=X','USD je CHF','USD','fx'),('DKKUSD=X','USD je DKK','USD','fx'),('SEKUSD=X','USD je SEK','USD','fx'),('EURUSD=X','USD je EUR','USD','fx'),('KRW=X','KRW je USD','KRW','fx')]

def build(root,today=None,fetcher=None):
    root=Path(root);today=today or dt.datetime.now(dt.timezone.utc).date();fetcher=fetcher or chart
    path=root/'data/benchmarks.json';old=json.loads(path.read_text()).get('series',{}) if path.exists() else {}
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    def collect(item):
        symbol,name,currency,sector=item
        row=dict(symbol=symbol,name=name,currency=currency,sector=sector,sourceUrl='https://finance.yahoo.com/quote/'+symbol+'/',
                 metadataSourceUrl=('https://www.ishares.com/de/privatanleger/de/produkte/251931/EXSA' if symbol=='EXSA.DE' else 'https://www.invesco.com/us/en/financial-products/etfs/invesco-qqq-trust-series-1.html' if symbol=='QQQ' else 'https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy' if symbol=='SPY' else SPONSOR) if sector!='fx' else None,attemptedAt=stamp)
        try:
            history,actual=fetcher(symbol)
            if actual!=currency:raise ValueError('Unexpected quote currency')
            # Never compare the current, potentially incomplete trading day.
            history=[p for p in history if p['date']<today.isoformat()]
            if len(history)<2 or (today-dt.date.fromisoformat(history[-1]['date'])).days>7:raise ValueError('No recent completed daily observations')
            row.update(status='fresh',fetchedAt=stamp,priceDate=history[-1]['date'],data=history)
        except Exception as e:
            previous=old.get(symbol,{})
            if previous.get('currency')!=currency:previous={}
            row.update(status='cached' if previous.get('data') else 'missing',fetchedAt=previous.get('fetchedAt'),
                       priceDate=previous.get('priceDate'),data=previous.get('data',[]),error=str(e)[:200])
        return symbol,row
    with cf.ThreadPoolExecutor(max_workers=3) as pool:series=dict(pool.map(collect,CATALOG))
    result=dict(schemaVersion=1,generatedAt=stamp,completedBefore=today.isoformat(),source='Yahoo Finance Chart (unofficial)',
      policy='ETF market-price proxies, not official index total returns. adjustedClose is a provider dividend/split-adjusted return proxy. USD/EUR presentation uses historical FX; no future fill, carry limited in UI. ETF fees are embedded; personal taxes and trading costs are not modelled.',series=series)
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    print('Benchmark/FX series:',{s:r['status'] for s,r in series.items()});return result

if __name__=='__main__':build(Path(__file__).resolve().parent)
