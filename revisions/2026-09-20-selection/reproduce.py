"""Re-run unchanged experiment in an isolated output directory and compare exact outputs."""
import gzip,json,shutil,tempfile
from pathlib import Path
import selection_study as study
original=study.HERE
with tempfile.TemporaryDirectory(prefix='crypto-selection-reproduction-') as td:
    stage=Path(td)
    for n in ['protocol.md','protocol_lock.json']:shutil.copy2(original/n,stage/n)
    study.HERE=stage
    study.run()
    left=json.loads((original/'results/study.json').read_text());right=json.loads((stage/'results/study.json').read_text())
    left.pop('completed_utc');right.pop('completed_utc');assert left==right
    assert (original/'results/fits.json').read_bytes()==(stage/'results/fits.json').read_bytes()
    for n in ['daily.csv.gz','primary_episodes.csv.gz']:
        assert gzip.open(original/'results'/n,'rb').read()==gzip.open(stage/'results'/n,'rb').read()
    (original/'reproduction_verification.json').write_text(json.dumps({'status':'exact_match','study_equal_excluding_completed_utc':True,'fits_byte_equal':True,'daily_and_episode_csv_uncompressed_byte_equal':True,'original_results_overwritten':False},indent=2)+'\n')
print('EXACT REPRODUCTION VERIFIED')
