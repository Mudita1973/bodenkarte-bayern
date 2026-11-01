// Distinguish the user's target descriptions from the evidence in a soil legend.
function interpretSoilLegends(data){
 const names={2:'Organik mit flachgründigem Felsboden',6:'Braunerde auf Lehm / Schluff · Teilmerkmale',7:'Braunerde mit Carbonat-/Basenbezug',8:'Lehm / Ton mit Stauwasserhinweisen',13:'Lehm mit steinigem Silikatsubstrat',14:'Podsolierung mit Sand / Lehm',15:'Podsolierung mit Grundwasserhinweis',16:'Moor-/Lehm-/Podsolhinweise',19:'Stauwasser mit Moor-/Silikathinweisen'};
 for(const p of data.profiles){p.target=p.name;p.name=names[p.code]||p.name}
 const six=data.profiles.find(p=>p.code===6);
 six.rule='Lehm oder Schluff und Braunerde / Parabraunerde genannt; kein Podsol-, Carbonat- oder Vernässungshinweis in der gesamten Legende, einschließlich Nebenböden. Das ist eine Vorauswahl nach Teilmerkmalen. Leicht saurer pH und gute Durchlässigkeit sind nicht belegt.';
 for(const l of data.legends){
  const wet=/pseudogley|stagnogley|gley|staunass|stauwasser|vernäss|moor|torf/i.test(l.text);
  if(wet)l.comparison.matches=l.comparison.matches.filter(n=>![6,13,14].includes(n));
  const clay=/lehm|schluff|\bton\b/i.test(l.first_substrate||'');
  if(clay&&/pseudogley|pseudovergley|stagnogley|stauwasser/i.test(l.text)&&!l.comparison.matches.includes(8))l.comparison.matches.push(8);
  l.comparison.matches.sort((a,b)=>a-b);
 }
}
function soilHydrology(l){
 const text=l.text,main=text.split(/gering verbreitet|selten/i)[0];
 const stau=/pseudogley|pseudovergley|stagnogley|staunass|stauwasser/i;
 if(stau.test(text))return {value:stau.test(main)?'Hinweis auf zeitweisen Wasserstau':'Zeitweiser Wasserstau in Nebenböden möglich',status:'Abgeleitet / Indiz',reason:(stau.test(main)?'Stauwassergeprägter Bodentyp in der Hauptbeschreibung.':'Pseudogley-/Stauwasserhinweis nur in Nebenböden; nicht auf jeden Punkt der Fläche übertragbar.')+' Deshalb kein Nachweis guter Durchlässigkeit. Die aktuelle Wasserleitfähigkeit ist nicht gemessen.'};
 if(/gley|grundwasser|vega|moor|torf/i.test(text))return {value:'Grundwasser-, Auen- oder Moorhinweis',status:'Abgeleitet / Indiz',reason:'Die Legende beschreibt wassergeprägte Böden. Daraus ergibt sich keine gemessene Durchlässigkeitsklasse und keine heutige Feuchte.'};
 return {value:'Keine Durchlässigkeitsklasse ableitbar',status:'Nicht ableitbar',reason:'Die Legende nennt hier keinen Vernässungshinweis. Auch lehmige Böden können dicht gelagert sein; Bodenstruktur, Unterboden und aktuelle Nutzung müssen gesondert geprüft werden.'};
}
function soilAcidity(l){
 const text=l.text,pod=/podsol/i.test(text),carbonate=/carbonat|kalk|mergel|rendzina/i.test(text.replace(/carbonatfrei\w*|kalkfrei\w*/gi,''));
 if(pod&&carbonate)return 'Podsolierung und Carbonatbezug werden beide genannt, möglicherweise in unterschiedlichen Böden oder Schichten. Daraus folgt keine einheitliche pH-Klasse.';
 if(pod)return 'Podsolierung ist ein Versauerungsindiz. Wie sauer der heutige Oberboden ist, bleibt ohne Standortwert offen.';
 if(carbonate)return 'Carbonat-/Kalkbezug ist genannt. Er kann den Untergrund oder Nebenböden betreffen; ein kalkhaltiger Oberboden ist damit nicht belegt.';
 return 'Kein spezifisches Säureindiz im Legendentext. Braunerde allein bedeutet weder „leicht sauer“ noch eine feste pH-Spanne. Ein Standortwert fehlt.';
}
function soilSummaryHTML(l){
 const text=l.text.replace(/^[^:]+:\s*/,''),types=text.split(/\baus\b/i)[0].replace(/[,;\s]+$/,''),hydro=soilHydrology(l),six=l.comparison.matches.includes(6);
 const reason=six?'Suchprofil 6: Nur Textur und Bodentyp passen zur Vorauswahl. Säuregrad und gute Durchlässigkeit sind damit nicht bestätigt.':/pseudogley|stagnogley|gley|vernäss|moor/i.test(l.text)?'Nicht in Suchprofil 6: Die Legende nennt auch wassergeprägte Böden. Solche Flächen gelten hier nicht mehr als Treffer für die Vorauswahl ohne Vernässungshinweis.':'Keine vollständige Gleichsetzung mit einer Zielkategorie der Abbildung.';
 return '<section class="soil-summary"><h3>Diese Bodeneinheit verständlich</h3><dl><dt>Bodengesellschaft laut Legende</dt><dd>'+esc(types)+'</dd><dt>Oberes Substrat</dt><dd>'+esc(l.first_substrate||'Keine eindeutige Textur im ersten Substrat erfasst')+'</dd><dt>Wasser / Entwässerung</dt><dd>'+esc(hydro.value)+'. '+esc(hydro.reason)+'</dd><dt>Säuregrad</dt><dd>'+esc(soilAcidity(l))+'</dd></dl><p class="search-verdict">'+esc(reason)+'</p><p class="note">Die Originallegende beschreibt eine Bodengesellschaft. Nebenböden und wechselnde Schichten bleiben relevant. Weitere amtliche Kennwerte: Standortauskunft im UmweltAtlas; heutige Verhältnisse durch eine Standortprüfung klären.</p><a href="https://www.lfu.bayern.de/boden/was_sind_boeden/bodentypen/index.htm" target="_blank" rel="noopener noreferrer">LfU: Eigenschaften und Unterschiede der Bodentypen ↗</a></section>';
}
