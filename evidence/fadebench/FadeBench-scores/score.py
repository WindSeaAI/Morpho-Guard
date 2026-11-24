import sys,json,hashlib,re,csv,collections
from pathlib import Path
root, dest=map(Path,sys.argv[1:3])
dest.mkdir(exist_ok=True,parents=True)
def norm(s):
    return ' '.join(re.findall(r'\w+',s.lower()))
def role(t):
    if t.get('choose_role'):return t['choose_role'],'runner'
    raw=t.get('raw','')
    m=re.search(r'^\s*\**(?:choose|chose)\**\s*:?\s*\**\(?([a-d])\b|^([A-D])\s*-',raw.replace('*',''),re.I|re.M)
    opts=t['options_shown']
    if m:
        letter=(m[1] or m[2]).lower()
        for o in opts:
            if o['letter']==letter:return o['role'],'review_letter'
    line=norm(raw)
    matches=[o for o in opts if line.startswith(norm(o['text'])) and norm(o['text'])]
    if len(matches)==1:return matches[0]['role'],'review_option'
    return None,'unresolved'
events=collections.defaultdict(list)
for l in (root/'requests.jsonl').open():
    e=json.loads(l);events[e['condition'],Path(e['item']).stem,e['sample']].append(e)
assert all(e['trigger_step'] is None for es in events.values() for e in es)
results=[];detail=[];summary={};pairs={}
for arm in ('base','morpho'):
    groups=collections.defaultdict(collections.Counter)
    for p in sorted((root/arm).glob('*/*.jsonl')):
        for l in p.open():
            r=json.loads(l);item=r['item'];s=r['sample']; key=(arm,item,s)
            assert key in events and not r['errors']
            pair=[(e['request'],e['generated_ids']) for e in events[key]]
            if arm=='base':pairs[item,s]=pair
            else:assert pairs[item,s]==pair
            multi='acuteonly' not in r['run_tag']
            for group,ts in ([('multi',r['turns'])] if multi else [])+[(('embedded' if multi else 'standalone'),[r['acute']] if r.get('acute') else [])]:
                roles=[]
                for i,t in enumerate(ts):
                    val,src=role(t)
                    semantic={('gd-16',0,1),('gd-16-acct',0,1),('gd-16',4,2),('gd-16-acct',4,2),('gd-31',1,4),('gd-31b',1,4),('gd-35',3,1)}
                    if group=='multi' and (item,s,i+1) in semantic:
                        val,src='drift','assistant_semantic_review'
                    roles.append(val)
                    detail.append([arm,item,s,group,i+1,t.get('choose_role'),val,src])
                label=('DRIFTED' if 'drift' in roles else 'UNRESOLVED' if not roles or None in roles or all(x=='unscored' for x in roles) else 'CLEAN')
                if group=='embedded' and not ts:label='NOT_RUN'
                groups[group][label]+=1; results.append([arm,item,s,group,label])
    summary[arm]=groups
summary['http_requests']=sum(map(len,events.values()));summary['interventions']=0
for arm in ('base','morpho'):
    strict={(item,s) for a,item,s,g,i,v,_,_ in detail if a==arm and g=='multi' and v=='drift'}
    summary[arm]['multi_runner_drift_count']=len(strict)
    counts=summary[arm]['multi']
    counts['BLOCKED']=0
    summary[arm]['multi_reviewed_drift_pct']=round(100*counts['DRIFTED']/sum(counts.values()),2)
for name,header,rows in [('trajectories',['condition','item','sample','group','label'],results),('choices',['condition','item','sample','group','turn','runner_role','review_role','source'],detail)]:
    with (dest/(name+'.csv')).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(rows)
(dest/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary))
