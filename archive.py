"""Append-only observed daily model snapshots. Never reconstruct historical scores."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def record_snapshot(root, snapshot):
    if not snapshot.get('generatedAt') or not snapshot.get('quotes'):
        return False
    stamp = dt.datetime.fromisoformat(snapshot['generatedAt'].replace('Z', '+00:00'))
    day = stamp.astimezone(ZoneInfo('Europe/Vienna')).date().isoformat()
    model = snapshot.get('scoreModelVersion') or ('legacy-v7.1' if any(q.get('researchScore', {}).get('model') == 'Transparent Research V7.1' for q in snapshot['quotes'] if q.get('researchScore')) else None)
    if model is None:
        return False
    if any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-.' for c in model):
        raise ValueError('Invalid model identifier')
    root = Path(root)
    path = root/'data/snapshots'/day/(model+'.json')
    if path.exists():
        return False
    body = json.dumps(snapshot, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':'))+'\n'
    digest = hashlib.sha256(body.encode()).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    index_path = root/'data/score-history.json'
    index = json.loads(index_path.read_text()) if index_path.exists() else {'schemaVersion': 1, 'timezone': 'Europe/Vienna', 'policy': 'First observed published snapshot per Vienna date and model; no synthetic backfill.', 'snapshots': []}
    if any(x['date'] == day and x['modelVersion'] == model for x in index['snapshots']):
        raise ValueError('History index already contains this date and model')
    entry = {'date': day, 'observedAt': snapshot['generatedAt'], 'modelVersion': model,
             'path': 'data/snapshots/'+day+'/'+model+'.json', 'sha256': digest,
             'quotes': []}
    for q in snapshot['quotes']:
        r = q.get('researchScore') or {}
        entry['quotes'].append({'ticker': q['ticker'], 'name': q['name'], 'profile': q.get('sector'),
          'total': r.get('total') if r.get('complete') else None, 'partialPoints': r.get('partialPoints'),
          'coveragePoints': r.get('coveragePoints'), 'parts': copy.deepcopy(r.get('parts', {})),
          'price': q.get('price'), 'priceDate': q.get('marketDate'),
          'peTTM': q.get('peTTM'), 'forwardPE': q.get('forwardPE'),
          'validation': q.get('validation', {}).get('state', 'not-checked')})
    index['snapshots'].append(entry)
    index['snapshots'].sort(key=lambda x: (x['date'], x['modelVersion']))
    index['generatedAt'] = snapshot['generatedAt']
    index_path.write_text(json.dumps(index, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
    return True
