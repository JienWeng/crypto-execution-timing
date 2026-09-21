"""Paired, descriptive reporting for a five-date development pilot."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ARMS=('reference','price','liquidity','both','twap')
SIZES=(.01,.05,.20)


def main():
    rows=list(csv.DictReader((HERE/'results/episodes.csv').open()))
    for r in rows:
        for k in r.keys()-{'asset','date','arm'}:
            r[k]=float(r[k]) if r[k] else None
    summary={'status':'five-date development pilot; descriptive, not confirmatory','panels':{}}
    daily_output=[]
    for mode in (1,0):
        rs=[r for r in rows if r['depletion']==mode]
        groups={}
        for r in rs:
            key=(r['asset'],r['date'],int(r['arrival_us']))
            groups.setdefault(key,{})[(r['fraction'],r['arm'])]=r
        complete={k:g for k,g in groups.items() if len(g)==15 and all(r['shortfall_bps'] is not None for r in g.values())}
        counts={arm:{'orders':len([r for r in rs if r['arm']==arm]),
                     'incomplete':sum(r['shortfall_bps'] is None for r in rs if r['arm']==arm),
                     'fallbacks':sum(r['fallback'] for r in rs if r['arm']==arm)} for arm in ARMS}
        panel={'arrivals':len(groups),'common_complete_arrivals_all_sizes_arms':len(complete),'counts':counts,'sizes':{}}
        for size in SIZES:
            by_asset_day={}
            for (asset,date,_),g in complete.items():
                baseline=g[(size,'reference')]['shortfall_bps']
                by_asset_day.setdefault((asset,date),[]).append({arm:baseline-g[(size,arm)]['shortfall_bps'] for arm in ARMS})
            ad={k:{arm:float(np.mean([r[arm] for r in v])) for arm in ARMS} for k,v in by_asset_day.items()}
            dates=sorted({k[1] for k in ad})
            daily={date:{arm:float(np.mean([v[arm] for (asset,d),v in ad.items() if d==date])) for arm in ARMS} for date in dates}
            means={arm:float(np.mean([v[arm] for v in daily.values()])) for arm in ARMS}
            assets={asset:{arm:float(np.mean([v[arm] for (a,d),v in ad.items() if a==asset])) for arm in ARMS} for asset in ('BTC','ETH','ADA')}
            components={}
            for arm in ARMS:
                day_components={}
                for (asset,date,_),g in complete.items():
                    ref=g[(size,'reference')];r=g[(size,arm)];scale=1e4/ref['arrival_notional']
                    day_components.setdefault((asset,date),[]).append({k:(ref[k]-r[k])*scale for k in ('timing_shortfall_dollars','spread_dollars','depth_dollars')})
                comps={}
                for k in ('timing_shortfall_dollars','spread_dollars','depth_dollars'):
                    adcomps={adkey:float(np.mean([v[k] for v in values])) for adkey,values in day_components.items()}
                    comps[k]=float(np.mean([np.mean([v for (a,d),v in adcomps.items() if d==date]) for date in dates]))
                if abs(sum(comps.values())-means[arm])>1e-6:raise AssertionError('decomposition does not sum to gain')
                components[arm]=comps
            panel['sizes'][str(size)]={'savings_bps':means,'daily_savings':daily,'asset_savings':assets,
                                      'liquidity_minus_price_bps':means['liquidity']-means['price'],
                                      'interaction_bps':means['both']-means['price']-means['liquidity'],
                                      'components_bps':components}
            for date,values in daily.items():
                daily_output.append({'depletion':mode,'size':size,'date':date,**values})
        panel['size_contrast_bps']=panel['sizes']['0.2']['liquidity_minus_price_bps']-panel['sizes']['0.01']['liquidity_minus_price_bps']
        # Size-specific attrition is always shown, not concealed by pooling.
        panel['completion_by_size_arm']={str(s):{arm:float(np.mean([r['shortfall_bps'] is not None for r in rs if r['fraction']==s and r['arm']==arm])) for arm in ARMS} for s in SIZES}
        panel['guard_triggered']=any(v<.99 for arms in panel['completion_by_size_arm'].values() for v in arms.values())
        summary['panels'][str(mode)]=panel
    (HERE/'results/summary.json').write_text(json.dumps(summary,indent=2))
    with (HERE/'results/daily.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(daily_output[0]));w.writeheader();w.writerows(daily_output)
    panel=summary['panels']['1']
    fig,axes=plt.subplots(1,2,figsize=(10,4.5))
    colors={'price':'#245a81','liquidity':'#b35c20','both':'#32734d'}
    for arm,color in colors.items():
        axes[0].plot([1,5,20],[panel['sizes'][str(s)]['savings_bps'][arm] for s in SIZES],'-o',label=arm.capitalize(),color=color)
    for ax in axes:
        ax.axhline(0,color='#666666',lw=.8);ax.set_xscale('log');ax.set_xticks([1,5,20],['1%','5%','20%']);ax.set_xlabel('Sale as share of displayed bid depth')
        ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Savings versus reference (bps)');axes[0].legend(frameon=False)
    axes[0].set_title('Five held-out dates: descriptive means',fontsize=11)
    for date in sorted(panel['sizes']['0.01']['daily_savings']):
        axes[1].plot([1,5,20],[panel['sizes'][str(s)]['daily_savings'][date]['liquidity']-panel['sizes'][str(s)]['daily_savings'][date]['price'] for s in SIZES],'-o',alpha=.65,label=date)
    axes[1].set_ylabel('Liquidity minus price savings (bps)');axes[1].set_title('Daily variation in relative value',fontsize=11)
    axes[1].legend(frameon=False,fontsize=7)
    fig.text(.02,.01,'Coinbase April 2021 pilot. Matched complete orders; hypothetical snapshot replay. No significance claim.',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(HERE/'figures/pilot_information_value.png',dpi=180);fig.savefig(HERE/'figures/pilot_information_value.svg');plt.close(fig)
    lines=['# Price versus liquidity: development pilot results','',summary['status']+'.','',
           'This is an implementation and research-feasibility test. It does not replace the existing manuscript with a validated new empirical contribution.','',
           'Training: 8–13 April 2021. Evaluation: 14–18 April 2021. Assets: BTC, ETH and ADA on Coinbase. Forecasts and order sizes were fixed before strategy outcomes.','',
           f"Valid arrival windows: {panel['arrivals']}. Common complete arrivals across all three sizes and all five policies: {panel['common_complete_arrivals_all_sizes_arms']}. Means give equal weight to each date and, within a date, each represented asset.",'',
           '| Sale / displayed depth | Price savings | Liquidity savings | Both savings | Liquidity − price | Interaction |',
           '|---|---:|---:|---:|---:|---:|']
    for size in SIZES:
        s=panel['sizes'][str(size)];v=s['savings_bps']
        lines.append(f"| {size:.0%} | {v['price']:.6f} | {v['liquidity']:.6f} | {v['both']:.6f} | {s['liquidity_minus_price_bps']:.6f} | {s['interaction_bps']:.6f} |")
    lines+=['','All entries are basis points; positive savings means lower cost than the seasonal current-book reference.', '',
            f"Prespecified large-minus-small contrast in relative liquidity value: {panel['size_contrast_bps']:+.6f} bps. This is a point estimate, not an established crossover.",'',
            f"Completion guard triggered (>1% incomplete in any arm/size): **{panel['guard_triggered']}**. Consult summary.json for every completion rate. If triggered, complete-order contrasts do not support claims for the original arrival population.",'',
            '## Cost explanation at the 5% size','',
            '| Policy | Price-timing savings | Spread savings | Depth savings | Total |','|---|---:|---:|---:|---:|']
    for arm in ('price','liquidity','both'):
        s=panel['sizes']['0.05'];c=s['components_bps'][arm]
        lines.append(f"| {arm} | {c['timing_shortfall_dollars']:.6f} | {c['spread_dollars']:.6f} | {c['depth_dollars']:.6f} | {s['savings_bps'][arm]:.6f} |")
    lines+=['','The components are an exact accounting identity, not causal effects. Common proportional fees scale differences in gross proceeds; the 10bps illustrative sensitivity is retained in episodes.csv.','',
            '## Interpretation limits','',
            '- Five evaluation dates cannot establish reliable population uncertainty or persistent effectiveness. No significance tests or confidence intervals are presented.',
            '- The sample is from April 2021 and a single exchange. Current-market and cross-venue generalization are untested.',
            '- Snapshot replay lacks counterfactual market responses, queue information, independently observed receipt latency, and exchange lot/minimum-order enforcement.',
            '- Retained consumed depth is a stated sensitivity convention. A price leaving the top levels does not prove cancellation. Independent-snapshot results are separately retained.',
            '- Full-window quality exclusions condition on subsequent data availability; completion exclusions can introduce policy-dependent selection. Counts and the completion guard must accompany every claim.',
            '- The restricted liquidity model changes spread and total quantity while preserving other ladder gaps. A weak result can reflect this approximation and forecast error; it does not establish that liquidity information is intrinsically worthless.',
            '', 'See CONTRIBUTION.md for the intended empirical claim, PRIOR_ART_AUDIT.md for close predecessors, and PILOT_PROTOCOL.md for frozen design.']
    lines+=['','## Completion and practical benchmark','',
            '| Policy | 5% savings (bps) | Completion at 1% | Completion at 5% | Completion at 20% |',
            '|---|---:|---:|---:|---:|']
    for arm in ARMS:
        c=panel['completion_by_size_arm'];v=panel['sizes']['0.05']['savings_bps'][arm]
        lines.append(f"| {arm} | {v:.6f} | {c['0.01'][arm]:.4%} | {c['0.05'][arm]:.4%} | {c['0.2'][arm]:.4%} |")
    lines+=['','TWAP is a secondary benchmark. Its loss against the reference is descriptive evidence on these same dates, not independent confirmation of the reference policy.']
    (HERE/'PILOT_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({mode:{'size_contrast_bps':p['size_contrast_bps'],'guard':p['guard_triggered'],'matched':p['common_complete_arrivals_all_sizes_arms'],'savings_5pct':p['sizes']['0.05']['savings_bps']} for mode,p in summary['panels'].items()},indent=2))


if __name__=='__main__':main()
