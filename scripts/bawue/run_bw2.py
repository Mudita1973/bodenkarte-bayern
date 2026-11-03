import pandas as pd
from run_fix_bw import *
REC=['colon','kalkab','carbsub2','ton','pslast','acidloess','sand','baendchen','anmoorph','podswald','loess','adj','haft','diorit','acidgap','pelpods','acidsand2','sand14','tf7','podsolreg']
fin=run(REC)
HAND={"a1":("13","Regosol bzw. Ranker aus saurem Gesteinsschutt der Gipfellagen; Prüfung: Hauptboden kein Felshumusboden, daher 13 statt 2"),
      "a207":("13","Regosol bzw. Ranker aus saurem Gesteinsschutt der Gipfellagen; Prüfung: Hauptboden kein Felshumusboden, daher 13 statt 2"),
      "a22":("13","Braunerde aus Schwarzwald-Moräne (Granit- und Gneismaterial): steiniger saurer Lehm, Prüfung: 13 statt 14"),
      "e37":("7","Rendzina-Braunerde: basenreiche Braunerde über Kalk, Prüfung: 7"),
      "f20":("7","Rendzina-Braunerde: basenreiche Braunerde über Kalk, Prüfung: 7"),
      "m1":("13","Braunerde-Ranker aus Sandstein: saurer, steiniger Lehm über Fels, Prüfung: 13"),
      "p139":("7","Tschernosem (Schwarzerde) aus Löss: basenreich, nächste Entsprechung 7"),
      "k116":("14","Braunerde aus Stubensandstein (entspricht dem Burgsandstein, im Dokument bei 14): sandig und sauer")}
for ke,(k,why) in HAND.items():
    if ke in fin.index: fin.loc[ke,["k","why","sure"]]=[k,why+" (Einzelfallprüfung, unsicher)",False]
U2=U.join(fin); U2["text"]=[build(r) for r in U.itertuples()]
U2.to_parquet("bw_units_cls.parquet")
tot=U2.km2.sum(); print(U2.groupby("k").km2.sum().round(0).sort_values(ascending=False).to_string()); print("unsicher",round(U2[~U2.sure.astype(bool)].km2.sum()/tot*100,1),"%")
old=pd.read_parquet("bw_units_cls_v1.parquet") if False else None
