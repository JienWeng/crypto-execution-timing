import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
OUT=HERE.parents[1]/'manuscript/revised'
OUT.mkdir(exist_ok=True);(OUT/'tables').mkdir(exist_ok=True);(OUT/'figures').mkdir(exist_ok=True)
s=json.loads((HERE/'results/study.json').read_text())
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
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(1,2,figsize=(9,3.4),constrained_layout=True)
for i,p in enumerate(['parallel','learned','ramp','mirror']):
 v=primary[p];x=0 if p=='parallel' else v['mean_gain'];lo,hi=(0,0) if p=='parallel' else v['gain_ci95']
 ax[0].errorbar(x,3-i,xerr=[[x-lo],[hi-x]],fmt='o',color='#244c69',capsize=3)
ax[0].axvline(0,color='gray',lw=.8,ls='--');ax[0].set_yticks(range(4),['Mirror','Ramp','Learned','Parallel']);ax[0].set_xlabel('Paired objective gain (bps)');ax[0].set_title('Identical endpoint predictions; different outcomes')
a=[r for r in s['decompositions'] if r['eta']==2 and r['risk']==1 and r['profile']=='learned'];weights=np.array([r['episodes'] for r in a]);R=np.average([r['price_alignment']-r['baseline_cost_gradient'] for r in a],weights=weights);C=np.average([r['curvature'] for r in a],weights=weights)
w=np.linspace(0,1,101);ax[1].plot(w,w*R-w*w*C,color='#244c69');ax[1].axhline(0,color='gray',ls='--',lw=.8);ax[1].set_xlabel('Weight on learned schedule deviation');ax[1].set_ylabel('Pooled mean objective gain (bps)');ax[1].set_title('Retrospective benefit–cost diagnostic')
for a,b,label in [(0,0,'0'),(.5,.5*R-.25*C,'1/2'),(1,R-C,'1')]:ax[1].plot(a,b,'o',color='#a4472d')
fig.savefig(OUT/'figures/timing_value.png',dpi=220);plt.close(fig)
print('Built four tables and main figure.')
