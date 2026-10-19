"""Shared, fingerprinted historical source inventory."""
import hashlib
import json
from pathlib import Path

def load_reports(root,apply_audit=True):
    root=Path(root);reports=[];hashes={};checks=[]
    paths=[root/'data/historical-reports.json',root/'data/historical-extensions.json']
    paths+=sorted((root/'data/historical-sec').glob('*.json'))
    paths+=[root/'data/historical-international.json',root/'data/historical-predecessors.json']
    for path in paths:
        if not path.exists():continue
        body=path.read_bytes();bundle=json.loads(body)
        reports.extend(bundle.get('reports',[]));checks.extend(bundle.get('collectionChecks',[]))
        hashes[str(path.relative_to(root/'data'))]=hashlib.sha256(body).hexdigest()
    audit=root/'data/historical-eps-audit.json'
    if apply_audit and audit.exists():
        body=audit.read_bytes();bundle=json.loads(body);hashes[audit.name]=hashlib.sha256(body).hexdigest()
        checks.extend(bundle.get('collectionChecks',[]))
        key=lambda r:(r['ticker'],r['periodEnd'],r.get('periodMonths',3),r['publishedAt'],r['documentSha256'])
        overlays={key(r):r for r in bundle.get('epsOverlays',[])}
        for row in reports:
            if key(row) in overlays:
                overlay=overlays[key(row)]
                for name in ('epsTtmApprox','epsTtmInputs','epsTtmBasis','epsBasisAudit'):row[name]=overlay[name]
    return reports,hashes,checks
