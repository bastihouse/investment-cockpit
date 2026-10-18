#!/usr/bin/env python3
"""Append original GAAP releases; preserve existing verified reports on fetch failure."""
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import re
from lxml import html
from collect_reconstruction_sources import ROOT,get,parsedate,numbers,TODAY
ORD={1:'First',2:'Second',3:'Third',4:'Fourth'}
SPLITS={
 'NVDA':[('2021-07-20',4,'https://nvidianews.nvidia.com/news/nvidia-announces-four-for-one-stock-split-pending-stockholder-approval-at-annual-meeting-set-for-june-3'),('2024-06-10',10,'https://investor.nvidia.com/files/doc_downloads/2024/05/NVIDIA-2024-Stock-Split-FAQ.pdf')],
 'AMZN':[('2022-06-06',20,'https://www.sec.gov/Archives/edgar/data/1018724/000101872422000009/amzn-20220309.htm')],
 'GOOGL':[('2022-07-18',20,'https://www.sec.gov/Archives/edgar/data/1652044/000119312522167375/d294315d8k.htm')], 'META':[]}
def parse_release(ticker,url):
 b=get(url);t=html.fromstring(b)
 for x in t.xpath('//script|//style|//nav|//footer|//header'):x.drop_tree()
 text=' '.join(t.text_content().split());match=re.search(r'(?:quarter|year) ended\s+([A-Z][a-z]+\s+\d{1,2},\s+20\d{2})',text)
 if not match:raise ValueError('No quarter end')
 end=parsedate(match[1]);pub=parsedate(text[:match.start()])
 if pub>TODAY.isoformat():return None
 if not 0<(dt.date.fromisoformat(pub)-dt.date.fromisoformat(end)).days<120:raise ValueError('Publication ordering')
 for table in t.xpath('//table'):
  rows=[[' '.join(c.text_content().split()) for c in tr.xpath('./th|./td') if c.text_content().strip()] for tr in table.xpath('.//tr')]
  def find(label):
   for r in rows:
    if r and re.fullmatch(label,r[0],re.I):return numbers(' '.join(r[1:]))
   return []
  rev=find('Total net sales' if ticker=='AMZN' else 'Revenue|Revenues')
  op=find('Operating income|Income from operations|Income \(loss\) from operations|Operating income \(loss\)')
  eps=find('Diluted earnings per share|Diluted earnings \(loss\) per share' if ticker=='AMZN' else 'Diluted')
  # Full GAAP statement, not first highlights table with sequential/non-GAAP columns.
  context=' '.join(table.text_content().split()).lower()
  if len(rev)<2 or len(op)<2 or len(eps)<2:continue
  if ticker=='NVDA' and ('weighted average' not in context and 'weighted-average' not in context):continue
  i=1 if ticker=='AMZN' else 0;j=1-i
  if not 0<rev[i]<1e7 or not 0<rev[j]<1e7 or not -rev[i]<op[i]<rev[i] or abs(eps[i])>100:raise ValueError('Implausible parsed GAAP values')
  splits=SPLITS[ticker];factor=1
  for date,ratio,_ in splits:
   if pub<date:factor*=ratio
  return dict(ticker=ticker,publishedAt=pub,periodEnd=end,revenue=rev[i],revenueYearAgo=rev[j],operatingIncome=op[i],epsDiluted=eps[i],epsToPriceBasisFactor=factor,priceBasisVerified=True,priceBasisAsOf=TODAY.isoformat(),splitEvents=[dict(tradingDate=d,ratio=r,url=u) for d,r,u in splits],currency='USD',units='USD millions, EPS USD/share as originally reported',sourceUrl=url,documentSha256=hashlib.sha256(b).hexdigest(),basis='Original release, current quarter GAAP column; EPS divided by disclosed later split factors to match split-adjusted price basis')
 raise ValueError('GAAP statement not found')
def urls(ticker,y,q):
 ordinal=ORD[q]
 if ticker=='NVDA':return [f'https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-{ordinal.lower()}-quarter-'+(f'and-fiscal-{y}' if q==4 else f'fiscal-{y}')]
 if ticker=='META':
  pub=y+(q==4);brand='Facebook' if y<=2021 and q<4 else 'Meta';title=f'{brand}-Reports-{ordinal}-Quarter-'+('and-Full-Year-' if q==4 else '')+str(y)+'-Results'
  return [f'https://investor.atmeta.com/investor-news/press-release-details/{pub}/{title}{suffix}/default.aspx' for suffix in (['-Initiates-Quarterly-Dividend',''] if y==2023 and q==4 else [''])]
 if ticker=='AMZN':
  special={(2021,1):'Amazon.com-Announces-First-Quarter-Results',(2021,2):'Amazon.com-Announces-Second-Quarter-Results-2dcdc6a32',(2021,3):'Amazon.com-Announces-Third-Quarter-Results',(2021,4):'Amazon.com-Announces-Fourth-Quarter-Results',(2022,1):'Amazon-com-Announces-First-Quarter-Results-f0188db95',(2023,2):'Amazon.com-Announces-Second-Quarter-Results',(2024,1):'Amazon-com-Announces-First-Quarter-Results-68b9258cd'}
  if (y,q) in special:return [f'https://ir.aboutamazon.com/news-release/news-release-details/{y+(q==4)}/{special[(y,q)]}/default.aspx']
  return [f'https://ir.aboutamazon.com/news-release/news-release-details/{y+(q==4)}/Amazon-com-Announces-{ordinal}-Quarter-Results/default.aspx']
def main():
 p=ROOT/'data/historical-reports.json';bundle=json.loads(p.read_text());existing={(r['ticker'],r['periodEnd']):r for r in bundle['reports']};errors=[]
 jobs=[(t,y,q) for t in ['NVDA','META','AMZN'] for y in range(2021,2028 if t=='NVDA' else 2027) for q in range(1,5) if not (y==(2027 if t=='NVDA' else 2026) and q>2)]
 def collect(job):
  t,y,q=job;last=None
  for url in urls(t,y,q):
   try:return parse_release(t,url)
   except Exception as e:last=e
  raise last
 with cf.ThreadPoolExecutor(max_workers=6) as pool:
  fs={pool.submit(collect,j):j for j in jobs}
  for f in cf.as_completed(fs):
   j=fs[f]
   try:
    r=f.result()
    if r:existing[(r['ticker'],r['periodEnd'])]=r;print(j,r['periodEnd'],r['revenue'],r['operatingIncome'],r['epsDiluted'],flush=True)
   except Exception as e:errors.append({'ticker':j[0],'period':str(j[1:]),'error':str(e)});print('FAILED',j,str(e),flush=True)
 bundle.update(collectedAt=dt.datetime.now(dt.timezone.utc).isoformat(),reports=sorted(existing.values(),key=lambda r:(r['ticker'],r['periodEnd'])),extensionErrors=errors)
 p.write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':'))+'\n');print('TOTAL',len(existing),'ERRORS',len(errors))
if __name__=='__main__':main()
