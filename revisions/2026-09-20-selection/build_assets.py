#!/usr/bin/env python3
"""Generate publication assets from frozen selection results; no model reruns."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'submission/forecast-selection-study/source'
for name in ['figures','tables']:(OUT/name).mkdir(parents=True,exist_ok=True)
D=json.loads((HERE/'results/study.json').read_text())
TRANSFER={'SOLUSDT','BNBUSDT','XRPUSDT'}
P=['endpoint','path','contrasts','economic','zero']
N={'endpoint':'Endpoint MSE','path':'Path MSE','contrasts':'Contrast MSE','economic':'Economic','zero':'Zero baseline'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','savefig.facecolor':'white'})
BLUE='#245c80';ORANGE='#b76532';CAP={}
def summary(p,eta=2,risk=1,cohort='transfer'):
 return next(x for x in D['summary'] if (x['policy'],x['eta'],x['risk'],x['cohort'])==(p,eta,risk,cohort))
W=[x for x in D['windows'] if x['eta']==2 and x['risk']==1]
T=[x for x in W if x['symbol'] in TRANSFER]
def forest(ax,rows,labels):
 v=np.array([x['mean_gain'] for x in rows]);c=np.array([x['ci95'] for x in rows]);ax.errorbar(v,np.arange(len(rows)),xerr=np.maximum(0,np.array([v-c[:,0],c[:,1]-v])),fmt='o',color=BLUE,capsize=3,ms=5);ax.set_yticks(np.arange(len(rows)),labels);ax.invert_yaxis();ax.axvline(0,color='#888888',lw=.9);ax.grid(axis='x',alpha=.2)
def save(fig,name,cap):
 for ext in ['png','svg']:fig.savefig(OUT/'figures'/f'{name}.{ext}',dpi=300,bbox_inches='tight')
 plt.close(fig);CAP[name]=cap
fig,ax=plt.subplots(figsize=(8,3.8),layout='constrained');forest(ax,[summary(p) for p in P],[N[p] for p in P]);ax.set(xlabel='Objective gain relative to zero baseline (bps)',title='Primary historical transfer: SOL, BNB and XRP')
save(fig,'transfer_selectors','Primary-cost (eta=2, r=1) transfer results over 26,496 episodes and 184 calendar dates. Bars are the frozen conditional 95% seven-calendar-day circular moving-block bootstrap intervals, with transfer assets resampled jointly by date. The economic and contrast selectors choose identical candidates and have identical results; they are not independent successes. All four selectors have negative mean gains relative to the zero baseline.')
fig,ax=plt.subplots(figsize=(8,4),layout='constrained');R=[x for x in D['summary'] if x['cohort']=='transfer' and x['policy']=='economic_minus_endpoint'];forest(ax,R,[f"η={x['eta']:g}, r={x['risk']:g}" for x in R]);ax.set(xlabel='Economic minus endpoint objective gain (bps)',title='Paired selector improvement across assumed costs')
save(fig,'transfer_cost_sensitivity','Transfer-sample paired economic-minus-endpoint differences for all six specified cost scenarios. Bars are the frozen conditional 95% seven-calendar-day circular moving-block bootstrap intervals, not independently constructed policy intervals. Positive differences indicate lower loss relative to endpoint selection, not positive gains relative to the zero baseline. Costs are assumed rather than empirically estimated.')
fig,ax=plt.subplots(figsize=(8,6.7),layout='constrained');T=sorted(T,key=lambda x:(['SOLUSDT','BNBUSDT','XRPUSDT'].index(x['symbol']),x['evaluation']));values=[x['gains']['economic']-x['gains']['endpoint'] for x in T];labels=[x['symbol'][:-4]+' '+x['evaluation'][5:] for x in T];ax.barh(np.arange(18),values,color=[BLUE if x>=0 else ORANGE for x in values],height=.7);ax.set_yticks(np.arange(18),labels);ax.invert_yaxis();ax.axvline(0,color='#777777',lw=.8);ax.set(xlabel='Economic minus endpoint mean objective gain (bps)',title='All 18 transfer asset-month cells · primary costs');ax.grid(axis='x',alpha=.18)
save(fig,'transfer_monthly_differences','All eighteen transfer asset-month paired mean differences under the primary costs; month labels 03–08 denote March–August 2026. No cell is excluded, and no cell-level confidence intervals are implied. SOL in March accounts for most of the aggregate improvement. This heterogeneity cautions against interpreting the pooled contrast as a uniformly beneficial selection rule.')
def fmt(v):return f'{v:.5f}'
def esc(s):return s.replace('_',r'\_')
def table(name,columns,header,rows,long=False):
 env='longtable' if long else 'tabular';lines=[r'\begin{'+env+'}{'+columns+'}',r'\toprule',header+r' \\',r'\midrule']
 if long:lines +=[r'\endhead']
 lines += [' & '.join(row)+r' \\' for row in rows];lines +=[r'\bottomrule',r'\end{'+env+'}'];(OUT/'tables'/name).write_text('\n'.join(lines)+'\n')
rows=[]
for p in P:
 r=summary(p);z=18 if p=='zero' else sum(w['chosen'][p]=='zero' for w in T);rows.append([N[p],fmt(r['mean_gain']),f"[{fmt(r['ci95'][0])}, {fmt(r['ci95'][1])}]",f'{z}/18'])
table('primary_selectors.tex','lrrr',r'Selector & Mean gain & Conditional 95\% interval & Zero choices',rows)
rows=[]
for w in sorted(W,key=lambda x:(x['symbol'],x['evaluation'])):
 rows.append([w['symbol'][:-4],w['evaluation'][5:]]+[esc(w['chosen'][p]) for p in P[:-1]]+[fmt(w['gains'][p]) for p in ['endpoint','path','contrasts','economic']]+[fmt(w['gains']['economic']-w['gains']['endpoint'])])
table('all_primary_windows.tex','ll'+('l'*4)+('r'*5),r'Asset & Month & End ID & Path ID & Contr. ID & Econ. ID & End gain & Path gain & Contr. gain & Econ. gain & Econ.$-$End',rows,long=True)
rows=[]
cohorts=sorted(set(x['cohort'] for x in D['summary']));
for p in D['candidate_names']:
 row=[esc(p)]
 for c in cohorts:
  r=summary(p,cohort=c);row +=[fmt(r['mean_gain']),f"[{fmt(r['ci95'][0])}, {fmt(r['ci95'][1])}]"]
 rows.append(row)
table('fixed_candidates.tex','lrrrr','Candidate & '+' & '.join(c.capitalize()+r' mean & 95\% interval' for c in cohorts),rows)
rows=[]
for r in R:
 eta=r['eta'];risk=r['risk'];rows.append([f'{eta:g}',f'{risk:g}',fmt(summary('endpoint',eta,risk)['mean_gain']),fmt(summary('economic',eta,risk)['mean_gain']),fmt(r['mean_gain']),f"[{fmt(r['ci95'][0])}, {fmt(r['ci95'][1])}]"])
table('cost_differences.tex','rrrrrr',r'$\eta$ & $r$ & Endpoint gain & Economic gain & Paired difference & Conditional 95\% interval',rows)
assert all(w['chosen']['economic']==w['chosen']['contrasts'] for w in W)
nonzero=[w for w in T if w['chosen']['economic']!='zero'];assert all(w['gains']['economic']<0 for w in nonzero)
sol=next(w for w in T if w['symbol']=='SOLUSDT' and w['evaluation']=='2026-03');total=sum(w['episodes']*(w['gains']['economic']-w['gains']['endpoint']) for w in T);share=sol['episodes']*(sol['gains']['economic']-sol['gains']['endpoint'])/total
notes=f'Primary transfer economic-minus-endpoint: {summary("economic_minus_endpoint")}. Economic nonzero selections: {len(nonzero)}/18; all have negative gain relative to baseline. SOL March contributes {share:.4%} of the aggregate episode-weighted paired difference. Economic and contrast candidate IDs coincide in all 30 primary windows. Fixed-candidate columns: {cohorts}. All results frozen; no refitting.'
(HERE/'figure_captions.md').write_text('# Figure captions\n\n'+'\n\n'.join('## '+k+'\n\n'+v for k,v in CAP.items())+'\n\n## Exact diagnostic notes\n\n'+notes+'\n')
print(notes)
