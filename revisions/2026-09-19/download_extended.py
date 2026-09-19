"""Fixed Jan–Aug 2026 BTC/ETH spot sample: acquisition and schema checks only.

Official specification: https://github.com/binance/binance-public-data
Never overwrites archives, checksum files, or the original data manifest.
No returns, outcomes, features, or policy decisions are computed here.
"""
import csv
import hashlib
import io
import json
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw'
MANIFEST = Path(__file__).with_name('data_manifest.json')
SYMBOLS = ('BTCUSDT', 'ETHUSDT')
MONTHS = tuple(f'2026-{month:02d}' for month in range(1, 9))


def download(url):
    for attempt in range(3):
        try:
            with urlopen(url, timeout=90) as response:
                return response.read()
        except HTTPError as error:
            if error.code < 500 or attempt == 2:
                raise
        except OSError:
            if attempt == 2:
                raise


def validate(blob, name, month):
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        if archive.namelist() != [name.removesuffix('.zip') + '.csv']:
            raise ValueError('unexpected archive members')
        rows = list(csv.reader(io.StringIO(archive.read(archive.namelist()[0]).decode('utf-8'))))
    return validate_rows(rows, month)


def validate_rows(rows, month):
    """Validate exact raw CSV rows; return row metadata and boolean checks."""
    if not rows or not all(len(row) == 12 for row in rows):
        raise ValueError('expected nonempty exact 12-column schema')
    values = np.array(rows, dtype=np.float64)
    # Parse integer fields directly, so fractional timestamps cannot be rounded away.
    opens = np.array([int(row[0]) for row in rows], dtype=np.int64)
    closes = np.array([int(row[6]) for row in rows], dtype=np.int64)
    trades = np.array([int(row[8]) for row in rows], dtype=np.int64)
    start = datetime.strptime(month, '%Y-%m').replace(tzinfo=timezone.utc)
    end = datetime(start.year + (start.month == 12), start.month % 12 + 1, 1, tzinfo=timezone.utc)
    start_us, end_us = int(start.timestamp()) * 1_000_000, int(end.timestamp()) * 1_000_000
    expected = (end_us - start_us) // 60_000_000
    checks = {
        'exact_12_columns': True,
        'finite_all_columns': bool(np.isfinite(values).all()),
        'expected_calendar_rows': len(rows) == expected,
        'microsecond_minute_grid': bool((opens % 60_000_000 == 0).all()),
        'no_duplicates_or_gaps': bool((np.diff(opens) == 60_000_000).all()),
        'start_boundary': int(opens[0]) == start_us,
        'end_boundary': int(opens[-1]) == end_us - 60_000_000,
        'close_timestamp': bool((closes == opens + 60_000_000 - 1).all()),
        'positive_prices': bool((values[:, 1:5] > 0).all()),
        'ohlc_bounds': bool(((values[:, 2] >= values[:, 1]) &
                             (values[:, 2] >= values[:, 4]) &
                             (values[:, 3] <= values[:, 1]) &
                             (values[:, 3] <= values[:, 4]) &
                             (values[:, 3] <= values[:, 2])).all()),
        'nonnegative_base_quote_taker_volumes': bool((values[:, [5, 7, 9, 10]] >= 0).all()),
        'taker_base_le_total': bool((values[:, 9] <= values[:, 5]).all()),
        'taker_quote_le_total': bool((values[:, 10] <= values[:, 7]).all()),
        'nonnegative_integer_trade_counts': bool((trades >= 0).all()),
    }
    if not all(checks.values()):
        raise ValueError(f'validation failed: {checks}')
    return {'rows': len(rows), 'expected_rows': expected, 'checks': checks,
            'first_open_us': int(opens[0]), 'last_open_us': int(opens[-1])}


def acquire(pair):
    symbol, month = pair
    name = f'{symbol}-1m-{month}.zip'
    url = f'https://data.binance.vision/data/spot/monthly/klines/{symbol}/1m/{name}'
    path = RAW / name
    checksum_path = RAW / (name + '.CHECKSUM')
    record = {'symbol': symbol, 'month': month, 'url': url,
              'checksum_url': url + '.CHECKSUM', 'path': str(path.relative_to(ROOT)),
              'reused_existing_archive': path.exists(),
              'checked_utc': datetime.now(timezone.utc).isoformat()}
    try:
        checksum = download(url + '.CHECKSUM').decode('ascii')
        parts = checksum.split()
        if len(parts) != 2 or not re.fullmatch(r'[0-9a-fA-F]{64}', parts[0]) or parts[1].lstrip('*') != name:
            raise ValueError('unexpected official checksum format')
        blob = path.read_bytes() if path.exists() else download(url)
        digest = hashlib.sha256(blob).hexdigest()
        if digest != parts[0].lower():
            raise ValueError('official exchange SHA256 mismatch; existing archive preserved')
        if checksum_path.exists() and checksum_path.read_text().split()[0].lower() != digest:
            raise ValueError('cached checksum mismatch; existing checksum preserved')
        record.update(validate(blob, name, month))
        # Exclusive creation guarantees existing files are not replaced.
        if not path.exists():
            with path.open('xb') as handle:
                handle.write(blob)
        if not checksum_path.exists():
            with checksum_path.open('x') as handle:
                handle.write(checksum)
        record.update(status='verified', sha256=digest, bytes=len(blob),
                      official_sha256_verified=True)
    except Exception as error:
        record.update(status='error', error_type=type(error).__name__, error=str(error))
    print(json.dumps({k: record[k] for k in ('symbol', 'month', 'status')}), flush=True)
    return record


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(acquire, [(symbol, month) for symbol in SYMBOLS for month in MONTHS]))
    manifest = {
        'source_documentation': 'https://github.com/binance/binance-public-data',
        'scope': 'Binance public spot monthly one-minute klines, BTCUSDT and ETHUSDT, January–August 2026 UTC',
        'expected_archives': 16, 'verified_archives': sum(r['status'] == 'verified' for r in records),
        'no_outcomes_computed': True, 'prices_are_execution_proxies': True,
        'records': records,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    if manifest['verified_archives'] != manifest['expected_archives']:
        raise SystemExit('Incomplete fixed sample: see data_manifest.json; no substitute months selected.')


if __name__ == '__main__':
    main()
