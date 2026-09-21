"""Causal Tardis snapshot extraction; local derived data, not redistribution."""
import argparse,csv,gzip,json,hashlib
from pathlib import Path
import numpy as np

def extract(source, output, max_age_us=5_000_000):
    source,output=Path(source),Path(output)
    records=[]; previous=None; boundary=None; last_local=None; rows=0; stale=0
    with gzip.open(source,'rt',newline='') as f:
        reader=csv.DictReader(f)
        required=['timestamp','local_timestamp']+[f'{s}[{i}].{v}' for s in ['bids','asks'] for i in range(25) for v in ['price','amount']]
        if not set(required).issubset(reader.fieldnames):raise ValueError('Missing snapshot fields')
        for row in reader:
            local=int(row['local_timestamp']); rows+=1
            if last_local is not None and local<last_local:raise ValueError('Local timestamps decrease')
            if boundary is None: boundary=((local+59_999_999)//60_000_000)*60_000_000
            # Strictly later event establishes all events at a boundary were consumed.
            while local>boundary:
                if previous is not None and boundary-int(previous['local_timestamp'])<=max_age_us:
                    records.append((boundary,previous))
                else:stale+=1
                boundary+=60_000_000
            previous=row;last_local=local
    # No extrapolation after final received record.
    arrays={'boundary_us':np.array([t for t,r in records],dtype=np.int64),
            'local_timestamp_us':np.array([int(r['local_timestamp']) for t,r in records],dtype=np.int64),
            'exchange_timestamp_us':np.array([int(r['timestamp']) for t,r in records],dtype=np.int64)}
    for side in ['bids','asks']:
        for value in ['price','amount']:
            arrays[f'{side}_{value}']=np.array([[float(r[f'{side}[{i}].{value}']) for i in range(25)] for t,r in records])
    for key,a in arrays.items():
        if not np.isfinite(a).all():raise ValueError('Nonfinite '+key)
    valid=(arrays['bids_price'][:,0]<arrays['asks_price'][:,0]) & (arrays['bids_amount']>=0).all(axis=1) & (arrays['asks_amount']>=0).all(axis=1) & (np.diff(arrays['bids_price'],axis=1)<0).all(axis=1) & (np.diff(arrays['asks_price'],axis=1)>0).all(axis=1)
    invalid=int((~valid).sum());arrays={k:a[valid] for k,a in arrays.items()}
    output.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(output,**arrays)
    audit={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'raw_rows':rows,'retained_boundaries':int(valid.sum()),'stale_boundaries':stale,'invalid_books':invalid,'max_age_us':max_age_us,'first_boundary_us':int(arrays['boundary_us'][0]),'last_boundary_us':int(arrays['boundary_us'][-1]),'maximum_actual_age_us':int((arrays['boundary_us']-arrays['local_timestamp_us']).max())}
    output.with_suffix('.json').write_text(json.dumps(audit,indent=2));return audit
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');a=p.parse_args();print(json.dumps(extract(a.source,a.output),indent=2))
