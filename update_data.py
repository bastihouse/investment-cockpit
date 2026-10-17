#!/usr/bin/env python3
"""Free public Yahoo chart data only; no API keys. Fail closed and keep last valid data."""
import json, urllib.request, urllib.parse, datetime as dt, time, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
UTC=dt.timezone.utc
NOW=dt.datetime.now(UTC)
TODAY=NOW.date()
universe=json.loads((ROOT/'data/universe.json').read_text())
prev=json.loads((ROOT/'data/snapshot.json').read_text())
previous={p['ticker']:p for p in prev['quotes']}
quotes=[]; errors=[]; successes=0
for stock in universe:
 t,y=stock['ticker'],stock['yahoo']; old=previous.get(t,{})
 item={**stock,'price':None,'ytdPricePct':None,'peTTM':None,'forwardPE':None,'marketDate':None,'cachedAt':None,'source':[],'status':'missing','attempts':{},'researchScore':None}
 try:
  url='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(y,safe='')+'?range=2y&interval=1d&events=div%2Csplits'
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (InvestmentCockpitFree/7.0)','Accept':'application/json'})
  with urllib.request.urlopen(req,timeout=20) as response: payload=json.load(response)
  data=(payload.get('chart',{}).get('result') or [None])[0]
  if data is None: raise ValueError(str(payload.get('chart',{}).get('error') or 'no chart result'))
  ts=data.get('timestamp',[]); closes=(data.get('indicators',{}).get('quote') or [{}])[0].get('close',[])
  hist=[{'date':dt.datetime.fromtimestamp(i,UTC).date().isoformat(),'close':round(float(p),6)} for i,p in zip(ts,closes) if p is not None and float(p)>0]
  if not hist:raise ValueError('no valid close prices')
  last=hist[-1]; date=dt.date.fromisoformat(last['date']); lag=(TODAY-date).days
  if lag<0:raise ValueError('future market date')
  if lag>7:raise ValueError('last close older than 7 days')
  anchor=next((p for p in reversed(hist) if p['date']<=f'{TODAY.year-1}-12-31'),None)
  ytd=round((last['close']/anchor['close']-1)*100,4) if anchor and last['date'].startswith(str(TODAY.year)) else None
  item.update(price=last['close'],ytdPricePct=ytd,marketDate=last['date'],cachedAt=NOW.isoformat(),source=['Yahoo Finance Chart (inoffiziell)'],status='cached',attempts={'history':{'status':'ok','checkedAt':NOW.isoformat()}})
  (ROOT/'data/history'/f'{t}.json').write_text(json.dumps({'source':'Yahoo Finance Chart (inoffiziell) · unadjusted daily close','data':hist},ensure_ascii=False,separators=(',',':'))+'\n')
  successes+=1
 except Exception as exc:
  msg=str(exc)[:200];errors.append(f'{t}: {msg}')
  # Retain previous valid published closing price as clearly stale, never label fresh.
  if old.get('price') is not None:
   item.update(price=old['price'],ytdPricePct=old.get('ytdPricePct'),marketDate=old.get('marketDate'),cachedAt=old.get('cachedAt'),source=old.get('source',[]),status='stale')
  item['attempts']={'history':{'status':'error','error':msg,'checkedAt':NOW.isoformat()}}
 quotes.append(item)
 time.sleep(0.15)
snapshot={'generatedAt':NOW.isoformat(),'providerMode':'GitHub Actions · Yahoo Finance Chart (inoffiziell; ohne Garantie)','fmpConfigured':False,'refresh':{'running':False,'finishedAt':NOW.isoformat(),'processed':32,'total':32,'lastError':'; '.join(errors[:5]) if errors else None},'quotes':quotes}
(ROOT/'data/snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,separators=(',',':'))+'\n')
providers=[]
for q in quotes:
 entry={'ticker':q['ticker'],'name':q['name'],'sector':'unclassified','sectorLabel':'nicht klassifiziert','providers':{}}
 for k in ['history','quote','ratios','income','estimates','key_metrics']:
  entry['providers'][k]={'state':('fresh' if q['status']=='cached' else 'stale' if q['status']=='stale' else 'missing') if k=='history' else 'missing','lastAttempt':q['attempts'].get(k)}
 providers.append(entry)
summary={}
for k in ['history','quote','ratios','income','estimates','key_metrics']:
 summary[k]={'fresh':sum(p['providers'][k]['state']=='fresh' for p in providers),'stale':sum(p['providers'][k]['state']=='stale' for p in providers),'missing':sum(p['providers'][k]['state']=='missing' for p in providers),'lastError':sum(p['providers'][k]['lastAttempt'] is not None and p['providers'][k]['lastAttempt'].get('status')=='error' for p in providers),'notApplicable':0}
(ROOT/'data/provider-audit.json').write_text(json.dumps({'generatedAt':NOW.isoformat(),'fmpConfigured':False,'summary':summary,'stocks':providers},ensure_ascii=False,separators=(',',':'))+'\n')
print(f'Kurse aktualisiert: {successes}/32. Fehlgeschlagen: {len(errors)}')
for e in errors:print('WARN',e)
# All failures -> CI exits nonzero, preventing publication of empty data as success.
if successes==0:raise SystemExit('No symbols refreshed; previous valid data retained and marked stale')
