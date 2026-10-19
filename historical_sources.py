"""Shared, fingerprinted historical source inventory."""
import hashlib
import json
from pathlib import Path

def load_reports(root):
    root=Path(root);reports=[];hashes={};checks=[]
    paths=[root/'data/historical-reports.json',root/'data/historical-extensions.json']
    paths+=sorted((root/'data/historical-sec').glob('*.json'))
    for path in paths:
        if not path.exists():continue
        body=path.read_bytes();bundle=json.loads(body)
        reports.extend(bundle.get('reports',[]));checks.extend(bundle.get('collectionChecks',[]))
        hashes[str(path.relative_to(root/'data'))]=hashlib.sha256(body).hexdigest()
    return reports,hashes,checks
