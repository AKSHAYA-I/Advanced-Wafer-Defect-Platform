import numpy as np

PARAMS = ['temperature_c','pressure_torr','gas_flow_sccm','etch_rate_nm_min','voltage_v','current_ma']

def rank_causes(payload):
    # Model-based engineering heuristic: ranks deviation from training reference ranges.
    # It is intentionally labelled probable, not physical causation.
    refs = {
      'temperature_c': (390, 510), 'pressure_torr': (20, 50), 'gas_flow_sccm': (90, 210),
      'etch_rate_nm_min': (55, 105), 'voltage_v': (180, 260), 'current_ma': (8, 22)
    }
    scores=[]
    for p in PARAMS:
        lo, hi = refs[p]
        x=float(payload[p]); d=max(0, lo-x, x-hi)/(hi-lo)
        scores.append((p, float(min(1, d + 0.05))))
    scores.sort(key=lambda z:z[1], reverse=True)
    step_score = {'CMP':.18,'Deposition':.24,'Etching':.35,'Lithography':.16,'Oxidation':.12}.get(payload['process_step'], .1)
    results=[{'process_step':payload['process_step'],'parameter':p,'probability':round(float(max(s, step_score if i==0 else s)),4),
              'explanation':f'Model-based screening flags {p} relative to the configured reference distribution.'} for i,(p,s) in enumerate(scores[:3])]
    return results
