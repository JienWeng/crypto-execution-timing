"""Order-state reconstruction primitives for the open Hyperliquid archive."""
import numpy as np

OPEN=1
CANCELED=2
FILLED=5
REMOVE={2,4,7,10,11,12,13,14,16}

RECORD=np.dtype([
 ('ts','<u8'),('userId','<u4'),('isBuilder','?'),('statusId','<u1'),
 ('isAsk','?'),('limitPx','<u4'),('sz','<u4'),('oid','<u8'),
 ('timestampDiff','<u4'),('triggerCondition','<i4'),('triggered','?'),
 ('isTrigger','?'),('hasChildren','?'),('isPositionTpsl','?'),
 ('reduceOnly','?'),('orderTypeId','<u1'),('tifId','<u1'),
 ('triggerPx','<u4'),('origSz','<u4')])
assert RECORD.itemsize==54

def decode(encoded):
    encoded=np.asarray(encoded,np.uint32)
    return (encoded&0x1fffffff)/np.power(10.,encoded>>29)

def _remove(state,levels,oid):
    old=state.pop(int(oid),None)
    if old is None:return
    side,price,size=old;key=(side,price)
    remaining=levels.get(key,0.)-size
    if remaining<=1e-10:levels.pop(key,None)
    else:levels[key]=remaining

def apply(state,levels,oid,is_ask,price,size,status):
    oid=int(oid);is_ask=bool(is_ask);price=float(price);size=float(size);status=int(status)
    if status==OPEN or status==FILLED:
        _remove(state,levels,oid)
        if size>0 and price>0:
            state[oid]=(is_ask,price,size);levels[(is_ask,price)]=levels.get((is_ask,price),0.)+size
    elif status in REMOVE:
        _remove(state,levels,oid)

def top(levels,is_ask,n):
    items=[(price,size) for (side,price),size in levels.items() if side==is_ask and size>0]
    return sorted(items,key=lambda x:x[0],reverse=not is_ask)[:n]
