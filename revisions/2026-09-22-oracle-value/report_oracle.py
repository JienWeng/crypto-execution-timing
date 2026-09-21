import csv,json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PILOT=HERE.parent/'2026-09-21-research-direction'

def load(path):
    rows=list(csv.DictReader(Path(path).open()))
    for r in rows:
        for k in r.keys()-{'asset','date','arm'}:r[k]=float(r[k]) if r[k] else None
    return rows

def main():
    oracle=load(HERE/'results/episodes.csv');learned=load(PILOT/'results/episodes.csv')
    output={'status':'post-pilot descriptive oracle diagnostic','modes':{}}
    for mode in (0,1):
        rows=[r for r in oracle if r['depletion']==mode]+[r for r in learned if r['depletion']==mode and r['arm'] in ('price','liquidity','both')]
        by={}
        for r in rows:by.setdefault((r['asset'],r['date'],int(r['arrival_us']),r['fraction']),{})[r['arm']]=r
        report={}
        needed={'reference','price','liquidity','both','oracle_price','oracle_liquidity','full_oracle'}
        for size in (.01,.05,.20):
            groups={k:g for k,g in by.items() if k[3]==size and needed<=g.keys() and all(g[a]['shortfall_bps'] is not None for a in needed)}
            ad={}
            for (asset,date,arrival,_),g in groups.items():
                ref=g['reference']['shortfall_bps']
                ad.setdefault((asset,date),[]).append({a:ref-g[a]['shortfall_bps'] for a in needed})
            ad={k:{a:float(np.mean([x[a] for x in v])) for a in needed} for k,v in ad.items()}
            dates=sorted({d for a,d in ad})
            daily={d:{a:float(np.mean([v[a] for (asset,date),v in ad.items() if date==d])) for a in needed} for d in dates}
            means={a:float(np.mean([v[a] for v in daily.values()])) for a in needed}
            report[str(size)]={'common_complete_arrivals':len(groups),'savings_bps':means,
                'oracle_liquidity_minus_price_bps':means['oracle_liquidity']-means['oracle_price'],
                'incremental_liquidity_given_price_bps':means['full_oracle']-means['oracle_price'],
                'incremental_price_given_liquidity_bps':means['full_oracle']-means['oracle_liquidity'],
                'unused_price_value_bps':means['oracle_price']-means['price'],
                'unused_liquidity_value_bps':means['oracle_liquidity']-means['liquidity'],
                'price_realization_ratio':means['price']/means['oracle_price'] if means['oracle_price']>0 else None,
                'liquidity_realization_ratio':means['liquidity']/means['oracle_liquidity'] if means['oracle_liquidity']>0 else None,
                'daily_savings':daily}
        output['modes'][str(mode)]=report
    (HERE/'results/summary.json').write_text(json.dumps(output,indent=2))
    main=output['modes']['0']
    lines=['# How much price and liquidity information was available ex post?','',
           'Post-pilot exploratory diagnostic. Oracle schedules use future information and are not implementable strategies. Independent-snapshot replay is the clean optimization upper bound reported below.','',
           '| Sale / displayed depth | Learned price | Hindsight price input | Learned liquidity | Hindsight liquidity input | Full oracle | Added liquidity given price |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for size in (.01,.05,.20):
        x=main[str(size)];m=x['savings_bps']
        lines.append(f"| {size:.0%} | {m['price']:.3f} | {m['oracle_price']:.3f} | {m['liquidity']:.3f} | {m['oracle_liquidity']:.3f} | {m['full_oracle']:.3f} | {x['incremental_liquidity_given_price_bps']:.3f} |")
    x=main['0.05'];m=x['savings_bps']
    lines+=['','Positive values are savings in basis points relative to the seasonal current-book reference. Means give equal weight to each evaluation date and to assets within dates.','',
            f"At the central size, the hindsight-price schedule saves {m['oracle_price']:.3f} bps and the full oracle saves {m['full_oracle']:.3f} bps. Adding realized future books after future prices are known contributes {x['incremental_liquidity_given_price_bps']:.3f} bps. The learned price and liquidity policies instead lose {abs(m['price']):.3f} and {abs(m['liquidity']):.3f} bps.",'',
            'Only the full oracle is an upper bound on proceeds within this planner. The single-input hindsight schedules optimize using one realized input and a reference for the other. The liquidity-only schedule can therefore lose total proceeds when its timing conflicts with subsequent price changes. The initial protocol described all three as upper bounds; that wording was too broad and is corrected here without changing the schedules or results.','',
            'The negative learned-to-hindsight comparison shows that the tested forecasts move schedules in the wrong direction on average. It is not an estimate of statistical forecast efficiency. Hindsight value establishes ex-post decision relevance, not forecastability.','',
            '## Interpretation','',
            'The earlier negative result is not explained by an absence of price-timing opportunity. Future prices dominate this short-horizon replay: once future prices are supplied, adding the realized future book contributes only 0.033, 0.045 and 0.075 bps at the three sizes. The incremental amount rises with size but remains small relative to roughly 26--27 bps of hindsight price value. The research problem is therefore causal price forecasting and safe policy calibration; liquidity forecasts are a secondary refinement under this design.','',
            'Five dates, one exchange, snapshot replay and hindsight optimization prevent a publication-grade effectiveness claim. The next study needs longer data and a fresh evaluation period. These observations cannot serve as untouched confirmation after this diagnostic.']
    (HERE/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({s:{k:v for k,v in main[s].items() if k!='daily_savings'} for s in main},indent=2))

if __name__=='__main__':main()
