"""Rerun the frozen pilot in isolation and compare exact outputs."""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent


def main(data_dir):
    expected=HERE/'results'
    with tempfile.TemporaryDirectory(prefix='crypto-liquidity-pilot-') as tmp:
        out=Path(tmp)/'results'
        env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
        subprocess.run([sys.executable,str(HERE/'pilot_study.py'),'--data-dir',str(Path(data_dir).resolve()),'--output',str(out)],check=True,env=env)
        checks={name:hashlib.sha256((expected/name).read_bytes()).hexdigest()==hashlib.sha256((out/name).read_bytes()).hexdigest()
                for name in ['episodes.csv','fits.json','forecast_errors.json','data_audit.json']}
        if not all(checks.values()):raise AssertionError(checks)
        (HERE/'reproduction_verification.json').write_text(json.dumps({'verified':True,'exact_byte_matches':checks,'timestamps_excluded':'run_manifest.json start/completion times; input paths can differ'},indent=2))
        print(json.dumps(checks,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',required=True);a=p.parse_args();main(a.data_dir)
