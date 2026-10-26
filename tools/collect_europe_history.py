#!/usr/bin/env python3
"""Filed GAAP/IFRS statement history for exact European issuer mappings.
Issuer-level income data may serve local shares; never transfer ADR EPS/share bases.
No current vendor figures, later filing dates or adjusted profits backfilled.
"""
import datetime as dt,hashlib,json,re,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT.parent/'tmp/reconstruction-sources'
def get(url):
 CACHE.mkdir(parents=True,exist_ok=True);p=CACHE/hashlib.sha256(url.encode()).hexdigest()
 if p.exists():return p.read_bytes()
 with urlopen(Request(url,headers={'User-Agent':'InvestmentCockpit public research; github.com/bastihouse/investment-cockpit'}),timeout=25) as response:body=response.read()
 p.write_bytes(body);return body
from scoring import SPECIAL
# Local listing -> SEC reporting issuer ticker, reported functional currency.
ISSUERS={'ASML.AS':('ASML','EUR'),'SAP.DE':('SAP','EUR'),'NOVN.SW':('NVS','USD'),'NOVO-B.CO':('NVO','DKK'),'AZN.L':('AZN','USD'),'TTE.PA':('TTE','USD'),'SHELL.AS':('SHEL','USD'),'ULVR.L':('UL','EUR'),'BP.L':('BP','USD'),'HSBA.L':('HSBC','USD'),'UBSG.SW':('UBS','USD'),'SAN.PA':('SNY','EUR'),'INGA.AS':('ING','EUR'),'DBK.DE':('DB','EUR'),'GSK.L':('GSK','GBP'),'BATS.L':('BTI','GBP'),'RIO.L':('RIO','USD'),'NG.L':('NGG','GBP'),'REL.L':('RELX','GBP'),'DGE.L':('DEO','USD'),'VOD.L':('VOD','EUR'),'NOKIA.HE':('NOK','EUR'),'RACE.MI':('RACE','EUR'),'ARGX.BR':('ARGX','USD')}

def extract(payload,ticker,currency,today,body_hash):
 profile=SPECIAL.get(ticker,'operating');financial=profile in ('bank','insurance','holding');facts=payload.get('facts',{});out=[]
 namespace='ifrs-full' if 'ifrs-full'in facts else 'us-gaap';f=facts.get(namespace,{})
 tags=(['ProfitLossAttributableToOwnersOfParent','ProfitLossAttributableToOrdinaryEquityHoldersOfParentEntity','NetIncomeLossAvailableToCommonStockholdersBasic','NetIncomeLoss'] if financial else ['Revenue','RevenueFromContractsWithCustomers','RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'])
 optags=['ProfitLossFromOperatingActivities','OperatingIncomeLoss']
 def values(tag):return [dict(r,tag=tag,namespace=namespace,unit=currency) for r in f.get(tag,{}).get('units',{}).get(currency,[]) if isinstance(r.get('val'),(int,float)) and not isinstance(r['val'],bool)]
 def unique(xs):return xs[0] if xs and len({r['val'] for r in xs})==1 else None
 for tag in tags:
  rows=values(tag)
  for r in rows:
   try:
    start,end,filed=[dt.date.fromisoformat(r[k]) for k in ('start','end','filed')];days=(end-start).days
    months=next((m for m,lo,hi in [(3,65,110),(6,150,200),(12,330,380)] if lo<=days<=hi),None)
    if not months or r.get('form') not in ('20-F','6-K','10-K','10-Q') or filed>today or end>=filed or end<dt.date(2020,1,1) or (filed-end).days>180:continue
    if not re.fullmatch(r'\d{10}-\d{2}-\d{6}',r.get('accn','')):continue
    current=unique([x for x in rows if all(x.get(k)==r[k] for k in ('accn','start','end'))])
    if not current:continue
    prior=unique([x for x in rows if x.get('accn')==r['accn'] and x.get('start') and 350<=(end-dt.date.fromisoformat(x['end'])).days<=378 and abs((dt.date.fromisoformat(x['end'])-dt.date.fromisoformat(x['start'])).days-days)<=14])
    if not prior or prior['val']<=0 or (not financial and current['val']<=0):continue
    op=None
    for ot in optags:
     op=unique([x for x in values(ot) if all(x.get(k)==r[k] for k in ('accn','start','end'))])
     if op:break
    url=f'https://www.sec.gov/Archives/edgar/data/{int(payload["cik"])}/{r["accn"].replace("-","")}/{r["accn"]}-index.html'
    rec=dict(ticker=ticker,kind=profile,periodStart=r['start'],periodEnd=r['end'],periodMonths=months,publishedAt=r['filed'],currency=currency,units='Millions of '+currency,sourceUrl=url,documentSha256=body_hash,accession=r['accn'],sourceType='SEC European issuer filed '+namespace,sourceInputs=[x for x in [current,prior,op] if x],priceBasisVerified=False,epsDiluted=None,growthBasis={3:'quarterly-yoy',6:'half-year-yoy',12:'annual-yoy'}[months]+('-shareholder-net-income' if financial else ''),basis='Original filed statement concepts, same accession and equal prior duration. SEC filing date is conservative availability; no earlier earnings date assumed. Reporting currency retained. Local shares and ADRs never share an EPS/valuation basis. No adjusted profit substitution.')
    if financial:rec.update(netIncome=r['val']/1e6,netIncomeYearAgo=prior['val']/1e6)
    else:rec.update(revenue=r['val']/1e6,revenueYearAgo=prior['val']/1e6,operatingIncome=op['val']/1e6 if op else None)
    out.append(rec)
   except (ValueError,KeyError,TypeError):continue
 # First filing per exact period; concept order preferred, never move restated values backwards.
 first={}
 for r in sorted(out,key=lambda x:x['publishedAt']):first.setdefault((r['periodEnd'],r['periodMonths']),r)
 return sorted(first.values(),key=lambda r:(r['periodEnd'],r['periodMonths']))

def main():
 mapping=json.loads(get('https://www.sec.gov/files/company_tickers.json'));ciks={r['ticker']:int(r['cik_str']) for r in mapping.values()};today=dt.date.today();path=ROOT/'data/historical-europe.json';old=json.loads(path.read_text()).get('reports',[]) if path.exists() else [];reports=[];checks=[]
 for ticker,(alias,currency) in ISSUERS.items():
  try:
   cik=ciks[alias];url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json';body=get(url);p=json.loads(body)
   if int(p['cik'])!=cik:raise ValueError('Wrong reporting issuer')
   rows=extract(p,ticker,currency,today,hashlib.sha256(body).hexdigest())
   if not rows:raise ValueError('No compatible filed periods for exact reported currency/concepts')
   reports.extend(rows);checks.append(dict(ticker=ticker,status='collected',periods=len(rows),sourceUrl=url,cik=cik,issuer=p.get('entityName'),reportCurrency=currency));print(ticker,len(rows),flush=True)
  except Exception as e:
   retained=[r for r in old if r['ticker']==ticker];reports.extend(retained);checks.append(dict(ticker=ticker,status='open',reason=str(e)[:200],retainedPeriods=len(retained)));print(ticker,'OPEN',str(e)[:160],flush=True)
  time.sleep(.15)
 path.write_text(json.dumps(dict(schemaVersion=1,collectedAt=dt.datetime.now(dt.timezone.utc).isoformat(),reports=reports,collectionChecks=checks,policy='First filed statement periods; raw GAAP/IFRS concepts and operands retained; no ADR EPS transfer. Failed sources keep prior verified periods. Not run automatically in daily CI.'),ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
if __name__=='__main__':main()
