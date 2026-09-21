"""Re-run the locked oracle diagnostic and compare deterministic outputs."""
import argparse,hashlib,os,subprocess,sys,tempfile,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(data_dir):
    with tempfile.TemporaryDirectory(prefix='oracle-value-') as td:
        out=Path(td)/'results'
        env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
        subprocess.run([sys.executable,str(HERE/'oracle_study.py'),'--data-dir',str(Path(data_dir).resolve()),'--output',str(out)],check=True,env=env)
        checks={n:digest(HERE/'results'/n)==digest(out/n) for n in ('episodes.csv','audit.json','manifest.json')}
        if not all(checks.values()):raise AssertionError(checks)
        (HERE/'reproduction_verification.json').write_text(json.dumps({'verified':True,'exact_byte_matches':checks},indent=2))
        print(json.dumps(checks,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',required=True);a=p.parse_args();main(a.data_dir)
