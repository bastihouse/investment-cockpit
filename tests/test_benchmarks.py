import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks import build,CATALOG

class BenchmarkTests(unittest.TestCase):
 def test_catalog_has_broad_sector_and_fx_series(self):
  self.assertEqual(len(CATALOG),15);self.assertEqual(len({x[0] for x in CATALOG}),15)
  self.assertIn('QQQ',[x[0] for x in CATALOG])
  self.assertEqual(sum(x[3] not in (None,'fx') for x in CATALOG),11)
 def test_current_day_excluded_and_failed_cache_keeps_original_timestamp(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir()
   old={'series':{'XLK':{'currency':'USD','fetchedAt':'2026-10-15T12:00:00Z','priceDate':'2026-10-15','data':[{'date':'2026-10-15','close':10,'adjustedClose':9}]},'XLF':{'currency':'EUR','data':[{'date':'2026-10-15','close':10}]}}}
   (root/'data/benchmarks.json').write_text(json.dumps(old))
   def fetch(symbol):
    if symbol in ('XLK','XLF'):raise RuntimeError('unavailable')
    return [{'date':'2026-10-15','close':10,'adjustedClose':9},{'date':'2026-10-16','close':11,'adjustedClose':10},{'date':'2026-10-19','close':999,'adjustedClose':999}], 'KRW' if symbol=='KRW=X' else 'USD'
   result=build(root,dt.date(2026,10,19),fetch)
   self.assertEqual(result['series']['SPY']['priceDate'],'2026-10-16');self.assertEqual(len(result['series']['SPY']['data']),2)
   self.assertEqual(result['series']['XLK']['status'],'cached');self.assertEqual(result['series']['XLK']['fetchedAt'],'2026-10-15T12:00:00Z')
   self.assertEqual(result['series']['XLF']['status'],'missing');self.assertEqual(result['series']['XLF']['data'],[])
 def test_wrong_currency_cannot_be_published_as_valid(self):
  with tempfile.TemporaryDirectory() as folder:
   r=build(Path(folder),dt.date(2026,10,19),lambda s:([{'date':'2026-10-15','close':1},{'date':'2026-10-16','close':2}],'EUR'))
   self.assertTrue(all(x['status']=='missing' for x in r['series'].values()))

if __name__=='__main__':unittest.main()
