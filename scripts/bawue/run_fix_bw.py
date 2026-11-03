import pandas as pd, re, importlib.util, sys, numpy as np

spec=importlib.util.spec_from_file_location("cf","/home/claude/bw/classify_bw2.py"); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
U=pd.read_parquet("/home/claude/bw/bw_units.parquet")
def s(v): return v if isinstance(v,str) else ""
def build(r):
    kul=s(r.kuleg); bod=s(r.bod_t); mat=s(r.mat_t)
    flags=[]
    m=re.search(r"unter Wald (meist |verbreitet |überwiegend |häufig |oft |stellenweise |örtlich |z\. T\. )?(podsolig|Podsol[-\w]*)",bod)
    if m and not re.match(r"stellenweise |örtlich |z\. T\. ",m.group(1) or ""): flags.append("unter Wald "+(m.group(1) or "")+"podsolig")
    if re.search(r"pseudovergleyt",bod) and "pseudovergleyt" not in kul: flags.append("verbreitet pseudovergleyt" if re.search(r"(verbreitet|meist|häufig|oft) pseudovergleyt",bod) else "selten pseudovergleyt")
    m2=re.search(r"\s+aus\s+",kul)
    types,subst=(kul[:m2.start()],kul[m2.end():]) if m2 else (kul,"")
    return types+("".join(", "+f for f in flags))+" aus "+subst+"; "+mat
def kalk_core(k, ab=False):
    k=s(k)
    if re.match(r"\s*(karbonatfrei|meist karbonatfrei|vereinzelt|stellenweise|örtlich|selten)",k): return False
    o=bool(re.search(r"ab Bodenoberfläche|unterhalb [0-4](\s|–|-|,)",k))
    if ab: o = o or bool(re.search(r"\bab [0-4](\s|–|-|,)", re.split(r"[,;]",k)[0]))
    return o
def carbsub(k):
    k=s(k).strip()
    if re.match(r"(karbonatfrei|kalkfrei|meist karbonatfrei|vorherrschend karbonatfrei|überwiegend karbonatfrei|vereinzelt|stellenweise|örtlich|selten|z\. ?T\.|teilweise)",k): return False
    m=re.search(r"(\d+)\s*(dm|[–\-]\s*>?\s*\d+\s*dm)",k)
    if re.search(r"ab Bodenoberfläche",k): return True
    return bool(m) and int(m.group(1))<=12
M={'6':6.5,'8':7.5,'7':7.0,'6b':6.75,'6a':6.25,'5':5.5,'4':4.5,'3':3.5,'2':2.75}
def ph(x):
    x=s(x).split('/')[0]; x=re.sub(r'\(.*?\)','',x)
    v=[M[y] for y in re.findall(r'6a|6b|[2-8]',x)]
    return (min(v),max(v)) if v else (None,None)
def carbsub2(k,kul):
    k=s(k).strip()
    if carbsub(k): return True
    if re.match(r"(stellenweise|z\. ?T\.|teilweise)",k) and re.search(r"[Gg]eschiebemergel|Löss\b|[Ss]andlöss",kul) and not re.search(r"riß",kul):
        m=re.search(r"(\d+)\s*(dm|[–\-]\s*>?\s*\d+\s*dm)",k)
        return bool(m) and int(m.group(1))<=10
    return False
def run(fix):
    c.FIX=dict((f,True) for f in fix); c.FIX['carbsub']=c.FIX.get('carbsub') or ('carbsub2' in fix); out=[]
    for r in U.itertuples():
        c.CUR_BODA=s(r.boda) or None; c.CUR_CARBSUB=(carbsub2(r.kalk,s(r.kuleg)) if 'carbsub2' in fix else carbsub(r.kalk)); c.CUR_KALKCORE=kalk_core(r.kalk, ab=('kalkab' in fix)); c.CUR_PHW=ph(r.phw)
        out.append(c.classify(r.Index,build(r),kalk_core(r.kalk, ab=('kalkab' in fix))))
    return pd.DataFrame(out,index=U.index,columns=['k','why','sure'])
