"""Acquire three CC0 archives using pinned lengths and SHA256; run at repo root."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

HERE=Path(__file__).resolve().parent

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(1024*1024):h.update(block)
    return h.hexdigest()

def acquire(item):
    path=Path(item['path']);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.stat().st_size!=item['bytes'] or sha(path)!=item['sha256']:
            raise ValueError(f'existing archive differs from pinned source: {path}')
        return {'path':str(path),'verified':True,'reused':True}
    temporary=path.with_suffix(path.suffix+'.part')
    if temporary.exists():raise ValueError(f'partial download exists: {temporary}')
    received=0
    with urllib.request.urlopen(item['url'],timeout=60) as response,temporary.open('xb') as f:
        while block:=response.read(1024*1024):
            received+=len(block)
            if received>item['bytes']:raise ValueError('download exceeds pinned length')
            f.write(block)
    if received!=item['bytes'] or sha(temporary)!=item['sha256']:
        raise ValueError(f'source checksum mismatch: {temporary}')
    temporary.replace(path)
    return {'path':str(path),'verified':True,'reused':False}

if __name__=='__main__':
    provenance=json.loads((HERE/'CC0_DATA_PROVENANCE.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(acquire,provenance['files']))
    print(json.dumps(results,indent=2))
