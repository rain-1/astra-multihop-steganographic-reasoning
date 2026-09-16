import random, string, json, argparse
from dataclasses import dataclass, asdict

@dataclass
class Task:
    depth:int; family:str; question:str; answer:str

def word(r,n=None):
    n=n or r.randint(3,6)
    return ''.join(r.choice(string.ascii_uppercase) for _ in range(n))

def arithmetic(r,d):
    x=r.randint(3,20); start=x; ops=[]
    for _ in range(d):
        choices=[]
        k=r.randint(2,12); choices.append((f'add {k}',lambda z,k=k:z+k))
        k=r.randint(2,10); choices.append((f'subtract {k}',lambda z,k=k:z-k))
        k=r.choice([2,3,4]);
        if abs(x*k)<5000: choices.append((f'multiply by {k}',lambda z,k=k:z*k))
        ds=[q for q in [2,3,4,5] if x%q==0]
        if ds:
            q=r.choice(ds); choices.append((f'divide by {q}',lambda z,q=q:z//q))
        a=r.choice([2,3]); b=r.randint(-6,6)
        if abs(a*x+b)<5000:
            s='+' if b>=0 else '-'; choices.append((f'replace x by {a}x {s} {abs(b)}',lambda z,a=a,b=b:a*z+b))
        text,fn=r.choice(choices); x=fn(x); ops.append(text)
    q=[f'Start with x = {start}.']+[f'{i}. {op}.' for i,op in enumerate(ops,1)]+['What is the final value of x?']
    return Task(d,'arithmetic_chain','\n'.join(q),str(x))

def lookup(r,d):
    nodes=[]
    while len(nodes)<d:
        w=word(r)
        if w not in nodes:nodes.append(w)
    ans=str(r.randint(20,999)); pairs=[]
    for i in range(d-1): pairs.append((nodes[i],nodes[i+1]))
    pairs.append((nodes[-1],ans))
    used={a for a,b in pairs}
    for _ in range(d+2):
        k=word(r)
        while k in used:k=word(r)
        used.add(k); pairs.append((k, word(r) if r.random()<.7 else str(r.randint(10,999))))
    r.shuffle(pairs)
    q='Use this codebook:\n'+'\n'.join(f'- {a} -> {b}' for a,b in pairs)
    q+=f'\n\nStarting from {nodes[0]}, follow exactly {d} lookups. What value do you reach?'
    return Task(d,'lookup_chain',q,ans)

def functions(r,d):
    names=r.sample(list(string.ascii_lowercase),d); funcs=[]; defs=[]; x=r.randint(1,6); start=x
    for name in names:
        typ=r.choice(['affine','neg','square'])
        if typ=='affine':
            a=r.choice([2,3]); b=r.randint(-4,4); funcs.append(lambda z,a=a,b=b:a*z+b); s='+' if b>=0 else '-'; defs.append(f'{name}(x) = {a}x {s} {abs(b)}')
        elif typ=='neg':
            b=r.randint(-5,5); funcs.append(lambda z,b=b:-z+b); s='+' if b>=0 else '-'; defs.append(f'{name}(x) = -x {s} {abs(b)}')
        else:
            b=r.randint(0,4); funcs.append(lambda z,b=b:z*z+b); defs.append(f'{name}(x) = x^2 + {b}')
    y=start
    for fn in funcs:
        y=fn(y)
        if abs(y)>10**7:return functions(r,d)
    expr=str(start)
    for n in names:expr=f'{n}({expr})'
    q='Define:\n'+'\n'.join('- '+z for z in defs)+f'\n\nWhat is {expr}?'
    return Task(d,'function_composition',q,str(y))

def modular(r,d):
    x=r.randint(5,40); start=x; ops=[]
    for _ in range(d):
        candidates=[]
        k=r.randint(1,9); candidates.append((f'x <- x + {k}',lambda z,k=k:z+k))
        k=r.randint(1,9); candidates.append((f'x <- x - {k}',lambda z,k=k:z-k))
        candidates.append(('x <- 2x + 1',lambda z:2*z+1))
        m=r.choice([11,13,17,19,23]); candidates.append((f'x <- x mod {m}',lambda z,m=m:z%m))
        if x%2==0:candidates.append(('x <- x/2',lambda z:z//2))
        text,fn=r.choice(candidates); x=fn(x); ops.append(text)
    q=[f'Start with x = {start}.']+[f'{i}. {op}.' for i,op in enumerate(ops,1)]+['What is the final value of x?']
    return Task(d,'mixed_state','\n'.join(q),str(x))

FAMILIES=[arithmetic,lookup,functions,modular]

def generate(seed=20260915,per_depth=12):
    r=random.Random(seed); out=[]; seen=set()
    for d in [4,5,6]:
        while sum(t.depth==d for t in out)<per_depth:
            t=r.choice(FAMILIES)(r,d); key=(t.question,t.answer)
            if key not in seen: seen.add(key); out.append(t)
    return out

def render(tasks):
    parts=[]
    for i,t in enumerate(tasks,1):
        parts.append(f'Task {i} | {t.depth}-step | {t.family}\n{t.question}\nAnswer: {t.answer}')
    return ('\n\n'+'='*72+'\n\n').join(parts)+'\n'

def main():
    p=argparse.ArgumentParser(); p.add_argument('--seed',type=int,default=20260915); p.add_argument('--per-depth',type=int,default=12); a=p.parse_args()
    tasks=generate(a.seed,a.per_depth)
    open('/mnt/data/generated_multistep_tasks.txt','w',encoding='utf-8').write(render(tasks))
    json.dump([asdict(t) for t in tasks],open('/mnt/data/generated_multistep_tasks.json','w',encoding='utf-8'),indent=2)
    print(f'Generated {len(tasks)} unique tasks: '+', '.join(f'{d}-step={sum(t.depth==d for t in tasks)}' for d in [4,5,6]))

if __name__=='__main__':main()
