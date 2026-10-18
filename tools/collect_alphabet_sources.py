import sys,concurrent.futures as cf,subprocess,re,hashlib,json,datetime as dt
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent))
from collect_reconstruction_sources import get,ROOT,parsedate,numbers,TODAY
from extend_reconstruction_sources import SPLITS

def run(y,q):
 base=f'https://s206.q4cdn.com/479360582/files/doc_financials/{y}/q{q}/'
 urls=[f'https://s206.q4cdn.com/479360582/files/doc_financials/{y}q{q}-alphabet-earnings-release.pdf',base+f'{y}q{q}-alphabet-earnings-release.pdf',base+f'{y}q{q}-alphabet-earnings-release-pdf.pdf',base+f'{y}Q{q}_alphabet_earnings_release.pdf']
 last=None
 for url in urls:
  try:
   b=get(url)
   if not b.startswith(b'%PDF'):raise ValueError('Not PDF')
   text=subprocess.run(['pdftotext','-f','1','-l','3','-layout','-','-'],input=b,capture_output=True,check=True).stdout.decode();flat=' '.join(text.split());pub=parsedate(flat);m=re.search(r'(?:quarter|year) ended\s+([A-Z][a-z]+\s+\d{1,2},\s+20\d{2})',flat)
   if not m:raise ValueError('Missing quarter end')
   end=parsedate(m[1]);lines=text.splitlines()
   def pick(label):
    line=next(x for x in lines if re.match(r'^\s*(?:'+label+r')\s{2,}',x,re.I));return numbers(re.sub(r'^\s*(?:'+label+r')\s{2,}','',line,flags=re.I))
   rev=pick('Revenues');op=pick('Operating income');eps=pick('Diluted EPS|Diluted earnings per share|Diluted net income per (?:common )?share')
   if len(rev)<2 or len(op)<2 or len(eps)<2:raise ValueError('Missing paired columns')
   if pub>TODAY.isoformat():return None
   assert 0<rev[1]<1e7 and rev[0]>0 and 0<op[1]<rev[1] and 0<eps[1]<100 and end<pub
   factor=20 if pub<'2022-07-18' else 1
   r=dict(ticker='GOOGL',publishedAt=pub,periodEnd=end,revenue=rev[1],revenueYearAgo=rev[0],operatingIncome=op[1],epsDiluted=eps[1],epsToPriceBasisFactor=factor,priceBasisVerified=True,priceBasisAsOf=TODAY.isoformat(),splitEvents=[dict(tradingDate=d,ratio=r,url=u) for d,r,u in SPLITS['GOOGL']],currency='USD',units='USD millions, EPS USD/share as originally reported',sourceUrl=url,documentSha256=hashlib.sha256(b).hexdigest(),basis='Original issuer release GAAP highlights; current quarter column; later disclosed splits applied separately')
   print(y,q,end,rev[1],op[1],eps[1],flush=True);return r
  except Exception as e:last=e
 print('FAILED',y,q,str(last),flush=True)
def main():
 with cf.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(lambda j:run(*j),[(y,q) for y in range(2021,2027) for q in range(1,5) if not(y==2026 and q>2)]))
 p=ROOT/'data/historical-reports.json';bundle=json.loads(p.read_text());rows={(r['ticker'],r['periodEnd']):r for r in bundle['reports']}
 for r in results:
  if r:rows[(r['ticker'],r['periodEnd'])]=r
 bundle['reports']=sorted(rows.values(),key=lambda r:(r['ticker'],r['periodEnd']));p.write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':'))+'\n')

if __name__=='__main__':main()
