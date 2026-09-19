#!/usr/bin/env python3
"""Rebuild full-paper figures from frozen results; never reruns or changes models."""
from pathlib import Path
import csv, gzip, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/full/figures'; OUT.mkdir(parents=True,exist_ok=True)
D=json.loads((ROOT/'revisions/2026-09-19/results/study.json').read_text())
with gzip.open(ROOT/'revisions/2026-09-19/results/primary_episodes.csv.gz','rt') as f: E=list(csv.DictReader(f))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.titlesize':11,'svg.fonttype':'none','savefig.facecolor':'white'})
BLUE='#205e82'; ORANGE='#bd652b'; GREEN='#427b66'; GRAY='#7a8290'; RED='#a23c48'
MONTHS=['2026-'+str(m).zfill(2) for m in range(3,9)]
LABELS=['Mar','Apr','May','Jun','Jul','Aug']; ASSETS=['BTCUSDT','ETHUSDT']
CAP={}
def save(fig,name,caption):
 fig.savefig(OUT/(name+'.png'),dpi=300,bbox_inches='tight'); fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(fig);CAP[name]=caption

def primary(rows):return [r for r in rows if r['eta']==2 and r['risk']==1]
def pooled(policy):return next(r for r in primary(D['pooled_results']) if r['policy']==policy)
def window(symbol,month,policy):return next(r for r in primary(D['window_results']) if (r['symbol'],r['month'],r['policy'])==(symbol,month,policy))
def forest(ax,rows,labels,field='mean_gain',interval='gain_ci95',color=BLUE):
 y=np.arange(len(rows));means=np.array([r[field] for r in rows]);ci=np.array([r[interval] for r in rows]);ax.errorbar(means,y,xerr=np.maximum(0,np.array([means-ci[:,0],ci[:,1]-means])),fmt='o',color=color,ms=4,capsize=3,lw=1.3);ax.set_yticks(y,labels);ax.invert_yaxis();ax.axvline(0,color=GRAY,lw=.8);ax.grid(axis='x',alpha=.18);ax.set_xlabel('Mean gain relative to baseline (bps)')

# 1: a fully specified mathematical example, not an empirical price path.
fig,axs=plt.subplots(1,3,figsize=(10,3.2),layout='constrained')
for p,c,l in [([3,2],BLUE,'Early-high'),([2,2],GRAY,'Flat'),([1,2],ORANGE,'Early-low')]:axs[0].plot([1,2],p,'o-',color=c,label=l)
axs[0].set(xticks=[1,2],xlabel='Execution slot',ylabel='Forecast price (arbitrary units)',title='(a) Identical terminal forecast');axs[0].legend(frameon=False,fontsize=8)
for k,(v,c,l) in enumerate([([.75,.25],BLUE,'Early-high'),([.5,.5],GRAY,'Flat'),([.25,.75],ORANGE,'Early-low')]):axs[1].bar(np.array([1,2])+(k-1)*.23,v,width=.22,color=c,label=l)
axs[1].set(xticks=[1,2],xlabel='Execution slot',ylabel='Fraction of fixed order',title='(b) Different schedules',ylim=(0,.85))
axs[2].bar(['Early-high','Flat','Early-low'],[.125,0,-.375],color=[BLUE,GRAY,ORANGE]);axs[2].axhline(0,color=GRAY,lw=.7);axs[2].set(ylabel='Objective gain (arbitrary units)',title='(c) Different realised value')
save(fig,'fig01_endpoint_example','Synthetic two-slot example, not observed cryptocurrency data. The realised price vector is (3,2), total volume is one, and K(u)=u1²+u2². Forecasts (3,2), (2,2), and (1,2) share terminal forecast 2 but imply schedules (0.75,0.25), (0.5,0.5), and (0.25,0.75). Gains relative to the flat-forecast baseline are 0.125, 0, and −0.375 in arbitrary objective units. Thus identical endpoint accuracy need not identify execution timing value.')

# 2: calendar design.
fig,ax=plt.subplots(figsize=(9,3.8),layout='constrained');cols=[BLUE,ORANGE,GREEN]
for row in range(6):
 for j,label in enumerate(['Fit','Calibrate','Evaluate']):ax.barh(row,1,left=row+j,color=cols[j],edgecolor='white');ax.text(row+j+.5,row,label,ha='center',va='center',fontsize=8,color='white')
ax.set(xticks=np.arange(8)+.5,xticklabels=['Jan','Feb']+LABELS,yticks=np.arange(6),yticklabels=[f'Window {i+1}' for i in range(6)],xlim=(0,8),title='2026 rolling chronology · applied separately to Bitcoin and Ether');ax.invert_yaxis();ax.tick_params(length=0);ax.spines[['left','bottom']].set_visible(False)
save(fig,'fig02_rolling_design','Rolling calendar design for each asset. Every evaluation month uses the preceding month for exposure calibration and the month before that for forecast fitting. January–August 2026 supply six evaluation windows per asset. This is a review-driven retrospective exploratory extension: calendar ordering prevents within-window look-ahead but does not make the study prospectively preregistered or the entire sample previously unseen.')

# 3: decomposition.
profiles=['learned','parallel','ramp','mirror'];decomp={}
for p in profiles:
 r=[x for x in primary(D['decompositions']) if x['profile']==p];n=sum(x['episodes'] for x in r);decomp[p]={k:sum(x[k]*x['episodes'] for x in r)/n for k in ['price_alignment','baseline_cost_gradient','curvature','mean_shifted_quantity']}
fig,axs=plt.subplots(1,2,figsize=(10,3.7),layout='constrained');x=np.arange(4)
for i,(k,l,c,sign) in enumerate([('price_alignment','Price alignment A',BLUE,1),('baseline_cost_gradient','Gradient cost −B',GRAY,-1),('curvature','Curvature cost −C',ORANGE,-1)]):axs[0].bar(x+(i-1)*.24,[sign*decomp[p][k] for p in profiles],width=.23,label=l,color=c)
axs[0].set(xticks=x,xticklabels=['Learned','Parallel','Ramp','Mirror'],ylabel='Contribution to gain (bps)',title='(a) Mean benefit–cost components');axs[0].axhline(0,color=GRAY,lw=.8);axs[0].legend(frameon=False,fontsize=8)
forest(axs[1],[pooled(p) for p in profiles],['Learned','Parallel','Ramp','Mirror']);axs[1].set_title('(b) Net objective gain with 95% intervals')
save(fig,'fig03_benefit_cost','Primary costs (eta=2, r=1), pooled across 17,664 episodes. Panel (a) reports episode-weighted A, −B and −C, whose sum is objective gain at full exposure. B is numerically zero at these interior solutions. Panel (b) shows frozen-result 95% calendar-day bootstrap intervals; both assets are resampled jointly on each of 184 dates. The parallel profile is analytically equivalent to the baseline (floating-point residuals below plotting resolution). The mirror is a deliberate diagnostic counterfactual, not an independently estimated competitor.')

# 4: complete window heterogeneity, authentic stored intervals.
fig,axs=plt.subplots(1,2,figsize=(10,4.7),sharex=True,layout='constrained')
for ax,a in zip(axs,ASSETS):
 for offset,p,c in [(-.14,'learned',BLUE),(.14,'ramp',ORANGE)]:
  rr=[window(a,m,p) for m in MONTHS];v=np.array([r['mean_gain'] for r in rr]);ci=np.array([r['gain_ci95'] for r in rr]);ax.errorbar(v,np.arange(6)+offset,xerr=np.maximum(0,np.array([v-ci[:,0],ci[:,1]-v])),fmt='o',color=c,ms=4,capsize=2,label=p.capitalize())
 ax.axvline(0,color=GRAY,lw=.8);ax.set(yticks=np.arange(6),yticklabels=LABELS,title=a.replace('USDT',''),xlabel='Mean objective gain (bps)');ax.invert_yaxis();ax.grid(axis='x',alpha=.18)
axs[0].legend(frameon=False,fontsize=8)
save(fig,'fig04_monthly_gains','All twelve asset-month evaluation cells under the primary costs. Points are full-exposure learned and ramp mean objective gains; bars are their stored 95% within-window calendar-day bootstrap intervals. Intervals are conditional on the fitted forecasts and calibrated design, with no multiple-comparison adjustment. Overlapping rolling windows are not independent replications.')

# 5: previous-month exposure decisions.
fig,axs=plt.subplots(1,2,figsize=(9,3.3),layout='constrained')
for ax,a in zip(axs,ASSETS):
 for p,c,marker in [('plugin',BLUE,'o'),('conservative',ORANGE,'s')]:ax.plot(np.arange(6),[window(a,m,p)['weight'] for m in MONTHS],marker=marker,color=c,label=p.capitalize(),lw=1.5)
 ax.set(xticks=np.arange(6),xticklabels=LABELS,ylim=(-.04,1.04),ylabel='Weight on learned schedule',title=a.replace('USDT',''));ax.grid(axis='y',alpha=.18)
axs[0].legend(frameon=False,fontsize=8,loc='upper left')
save(fig,'fig05_calibrated_exposure','Primary-cost schedule-mixture weights determined using the preceding calibration month, displayed against the subsequent evaluation month. The plug-in rule selects positive weights in six of twelve cells. The conservative rule selects zero in all cells, exactly reproducing the baseline. These are implemented ex ante within each retrospective split, not weights chosen from evaluation outcomes.')

# 6: objective and monetary estimands differ by inventory preference.
fig,ax=plt.subplots(figsize=(8.5,4.4),layout='constrained');policies=['learned','ramp','mirror','half','plugin','conservative']
for offset,field,ci,c,l in [(-.14,'mean_gain','gain_ci95',BLUE,'Objective'),(.14,'mean_monetary_gain','monetary_ci95',ORANGE,'Monetary')]:
 rr=[pooled(p) for p in policies];v=np.array([r[field] for r in rr]);q=np.array([r[ci] for r in rr]);ax.errorbar(v,np.arange(6)+offset,xerr=np.maximum(0,np.array([v-q[:,0],q[:,1]-v])),fmt='o',color=c,ms=4,capsize=2,label=l)
ax.set(yticks=np.arange(6),yticklabels=[p.capitalize() for p in policies],xlabel='Mean gain relative to baseline (bps)',title='Primary-cost pooled outcomes');ax.invert_yaxis();ax.axvline(0,color=GRAY,lw=.8);ax.legend(frameon=False);ax.grid(axis='x',alpha=.18)
save(fig,'fig06_objective_monetary','Objective and monetary gains under the primary costs. Objective gain includes the specified inventory preference; monetary gain omits that preference but retains the assumed temporary-impact charge. Both use the same replay prices and schedules. Bars are stored 95% calendar-day bootstrap intervals. Monetary gain is a model-based replay estimand, not realised profit after observed exchange execution costs.')

# 7: six specified cost scenarios.
fig,axs=plt.subplots(1,2,figsize=(10,4.2),sharex=True,layout='constrained')
for ax,p in zip(axs,['learned','plugin']):
 rr=[r for r in D['pooled_results'] if r['policy']==p];forest(ax,rr,[f"η={r['eta']:g}, r={r['risk']:g}" for r in rr]);ax.set_title(p.capitalize()+' schedule exposure')
save(fig,'fig07_cost_sensitivity','All six specified cost scenarios, with full learned exposure on the left and the prior-month plug-in schedule mixture on the right. Points and 95% calendar-day bootstrap intervals are drawn directly from the frozen analysis. Eta is an assumed impact coefficient and r an inventory preference; neither is estimated from exchange order-book execution. This scenario analysis does not constitute a calibrated real-world cost estimate.')

# 8: an explicitly new descriptive influence analysis, no inference or model selection.
leave=[]
for m in MONTHS:
 rows=[r for r in E if r['month']!=m];leave.append({'excluded_month':m,'episodes_retained':len(rows),'mean_learned_gain':float(np.mean([float(r['learned_gain']) for r in rows])),'mean_ramp_gain':float(np.mean([float(r['ramp_gain']) for r in rows]))})
days=sorted(set(r['utc_day'] for r in E),key=int); daily=[]
for day in days:
 rows=[r for r in E if r['utc_day']==day];daily.append({'utc_day':int(day),'episodes':len(rows),'mean_learned_gain':float(np.mean([float(r['learned_gain']) for r in rows]))})
fig,axs=plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
axs[0].plot(np.array([r['utc_day'] for r in daily],dtype='datetime64[D]'),[r['mean_learned_gain'] for r in daily],color=BLUE,lw=.85);axs[0].axhline(0,color=GRAY,lw=.7);axs[0].set(ylabel='Daily mean learned gain (bps)',title='(a) Both assets pooled by UTC date');axs[0].tick_params(axis='x',rotation=30)
for p,c in [('learned',BLUE),('ramp',ORANGE)]:axs[1].plot([r['mean_'+p+'_gain'] for r in leave],np.arange(6),'o',color=c,label=p.capitalize())
axs[1].axvline(0,color=GRAY,lw=.8);axs[1].axvline(pooled('learned')['mean_gain'],color=BLUE,lw=.8,ls='--',label='All-month learned');axs[1].set(yticks=np.arange(6),yticklabels=['Omit '+x for x in LABELS],xlabel='Remaining-sample mean gain (bps)',title='(b) Leave-one-month-out description');axs[1].invert_yaxis();axs[1].legend(frameon=False,fontsize=8)
save(fig,'fig08_descriptive_influence','Additional ex post descriptive diagnostics from unchanged primary episode results; no forecasts, weights or schedules are refitted. Panel (a) averages learned gains across both assets for each UTC date. Panel (b) excludes one evaluation month from both assets and recomputes the remaining episode-weighted means; the dashed line is the all-month learned mean. No confidence intervals or robustness claims are implied. This display diagnoses sample concentration and must not be used to select months for the headline estimate.')

report={'source':'Frozen study.json and primary_episodes.csv.gz; no model refit','primary_decomposition':decomp,'pooled_primary':primary(D['pooled_results']),'leave_one_month_out_descriptive':leave,'daily_descriptive':daily,'figure_count':len(CAP)}
(ROOT/'analysis').mkdir(exist_ok=True);(ROOT/'analysis/full_diagnostics.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'manuscript/full/figure_captions.md').write_text('# Full-paper figure captions\n\n'+'\n\n'.join('## '+k+'\n\n'+v for k,v in CAP.items())+'\n')
print(json.dumps({'figures':len(CAP),'leave_one_month_out':leave,'decomposition':decomp},indent=2))

# Four complete numerical tables, generated directly from frozen results.
s=D
OUT=ROOT/'manuscript/full'
(OUT/'tables').mkdir(exist_ok=True)
primary={r['policy']:r for r in s['pooled_results'] if r['eta']==2 and r['risk']==1}
names={'learned':'Learned','parallel':'Parallel','ramp':'Ramp','mirror':'Mirror','half':'Half learned','plugin':'Plug-in','conservative':'Lower-percentile'}
lines=[r'\begin{tabular}{lrrr}',r'\toprule',r'Profile & Price alignment & Curvature & Net gain [95\% interval] \\',r'\midrule']
for p in ['parallel','learned','ramp','mirror']:
 a=[r for r in s['decompositions'] if r['eta']==2 and r['risk']==1 and r['profile']==p];w=np.array([r['episodes'] for r in a]);v=primary[p]
 A=np.average([r['price_alignment'] for r in a],weights=w);C=np.average([r['curvature'] for r in a],weights=w)
 if p=='parallel':A=C=0;v=dict(v,mean_gain=0,gain_ci95=[0,0])
 lines.append(f"{names[p]} & {A:.5f} & {C:.5f} & {v['mean_gain']:.5f} [{v['gain_ci95'][0]:.5f}, {v['gain_ci95'][1]:.5f}] \\\\")
lines += [r'\bottomrule',r'\end{tabular}'];(OUT/'tables/profiles.tex').write_text('\n'.join(lines)+'\n')
lines=[r'\begin{tabular}{llrrrrrr}',r'\toprule',r'Asset & Month & Hit rate & Terminal $R^2$ & Learned & Ramp & $w_P$ & $w_C$ \\',r'\midrule']
for f in s['forecast_diagnostics']:
 rr={r['policy']:r for r in s['window_results'] if r['symbol']==f['symbol'] and r['month']==f['evaluation'] and r['eta']==2 and r['risk']==1}
 lines.append(f"{f['symbol'][:-4]} & {f['evaluation'][5:]} & {100*f['terminal_directional_accuracy']:.1f}\\% & {f['terminal_r2_vs_zero']:.5f} & {rr['learned']['mean_gain']:.5f} & {rr['ramp']['mean_gain']:.5f} & {rr['plugin']['weight']:.3f} & {rr['conservative']['weight']:.3f} \\\\")
lines += [r'\bottomrule',r'\end{tabular}'];(OUT/'tables/windows.tex').write_text('\n'.join(lines)+'\n')
lines=[r'\begin{tabular}{lrrr}',r'\toprule',r'Exposure policy & Objective gain & 95\% interval & Monetary gain \\',r'\midrule']
for p in ['learned','half','plugin','conservative']:
 v=primary[p];lines.append(f"{names[p]} & {v['mean_gain']:.5f} & [{v['gain_ci95'][0]:.5f}, {v['gain_ci95'][1]:.5f}] & {v['mean_monetary_gain']:.5f} \\\\")
lines += [r'\bottomrule',r'\end{tabular}'];(OUT/'tables/calibrated.tex').write_text('\n'.join(lines)+'\n')
lines=[r'\begin{tabular}{rrrrr}',r'\toprule',r'$\eta$ & $r$ & Learned gain & 95\% interval & Plug-in gain \\',r'\midrule']
for eta,risk in [(.5,0),(.5,1),(2,0),(2,1),(5,0),(5,1)]:
 rr={r['policy']:r for r in s['pooled_results'] if r['eta']==eta and r['risk']==risk};v=rr['learned']
 lines.append(f"{eta:g} & {risk:g} & {v['mean_gain']:.5f} & [{v['gain_ci95'][0]:.5f}, {v['gain_ci95'][1]:.5f}] & {rr['plugin']['mean_gain']:.5f} \\\\")
lines += [r'\bottomrule',r'\end{tabular}'];(OUT/'tables/sensitivity.tex').write_text('\n'.join(lines)+'\n')
