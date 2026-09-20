"""Fixed transfer assets: download/check only, no outcome analysis."""
import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'revisions/2026-09-19'))
import download_extended as source
SYMBOLS=['SOLUSDT','BNBUSDT','XRPUSDT']
MONTHS=[f'2026-{m:02d}' for m in range(1,9)]
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(source.acquire,[(s,m) for s in SYMBOLS for m in MONTHS]))
    (HERE/'transfer_manifest.json').write_text(json.dumps({'expected_archives':24,'verified_archives':sum(r['status']=='verified' for r in rows),'records':rows},indent=2)+'\n')
    if any(r['status']!='verified' for r in rows):raise SystemExit('Incomplete sample; no substitution')
