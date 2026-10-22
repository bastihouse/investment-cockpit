/* Presentation only: observed score drivers, compact help, mobile layout and themes. */
(function(){'use strict';
const finite=v=>typeof v==='number'&&Number.isFinite(v),labels={valuation:'Bewertung',growth:'Wachstum',quality:'Qualität',revisions:'Revisionen',risk:'Marktrisiko'};
function explainChange(before,after,beforeModel,afterModel){
 const api=typeof window==='undefined'?require('./insights.js'):window.CockpitInsights,d=api.diffQuotes(before,after,beforeModel,afterModel);
 const f=before?.fundamentals||{},g=after?.fundamentals||{},profile=after?.sector||after?.researchScore?.profile;
 const reportA=f.specialist?.periodEnd||f.reportDate,reportB=g.specialist?.periodEnd||g.reportDate;
 const priceChanged=finite(before?.price)&&finite(after?.price)&&before.price>0&&Math.abs(after.price-before.price)>.000001;
 const reportChanged=!!reportA&&!!reportB&&reportA!==reportB;
 const drivers=d.rows.map(row=>{
  const blocks=after?.validation?.blockedCategories?.[row.key]||[],reason=after?.researchScore?.missingReasons?.[row.key];
  const metrics=row.inputs.filter(x=>!['Schlusskurs','Berichtsende'].includes(x.label));
  let kind='unverändert',title='Keine Änderung',note='Punkte und verwendete Eingaben unverändert.';
  if(!d.comparable){kind='model';title=before&&after?'Modell oder Profil gewechselt':before?'Aktie fehlt im Vergleichsstand':'Erste Beobachtung';note='Für diese Stände gibt es keine zulässige Punktedifferenz.';}
  else if(row.state==='coverage-lost'){kind='gap';title=blocks.length?'Eingabe gesperrt':'Daten fehlen oder sind veraltet';note=reason||'Diese Kategorie ist im Vergleichsstand nicht mehr freigegeben.';}
  else if(row.state==='coverage-added'){kind='coverage';title='Datenabdeckung ergänzt';note='Erstmals in diesem Vergleich berechenbar; kein ausgewiesener Unternehmensgewinn.';}
  else if(row.state==='missing'){kind='gap';title='Weiterhin offen';note=reason||'In beiden Ständen fehlen geeignete Eingaben.';}
  else if(row.key==='risk'&&row.inputs.length){kind='risk';title='Marktrisiko verändert';note='Die gespeicherte Volatilität bzw. das rollierende Kursfenster hat sich verändert.';}
  else if(row.key==='revisions'&&metrics.length){kind='estimates';title='Konsens / Prognose verändert';note=profile==='reit'?'Die hinterlegte AFFO-Guidance hat sich verändert.':'Die gespeicherten Konsenswerte oder deren Vergleichsbasis haben sich verändert.';}
  else if(row.key==='valuation'&&priceChanged){
   // A price-only explanation needs a stable, evidenced denominator and a matching ratio.
   let stableDenominator=false,ratioA,ratioB;
   if(profile==='operating'){stableDenominator=finite(f.trailingEps)&&f.trailingEps>0&&f.trailingEps===g.trailingEps;ratioA=before.peTTM;ratioB=after.peTTM;}
   if(['bank','insurance','holding'].includes(profile)){stableDenominator=finite(f.bookValue)&&f.bookValue>0&&f.bookValue===g.bookValue;ratioA=f.priceToBook;ratioB=g.priceToBook;}
   if(profile==='bdc'){stableDenominator=finite(f.specialist?.raw?.navPerShare)&&f.specialist.raw.navPerShare===g.specialist?.raw?.navPerShare;ratioA=before.price/f.specialist.raw.navPerShare;ratioB=after.price/g.specialist.raw.navPerShare;}
   if(profile==='reit'){const a=f.specialist?.raw?.affoQuarterPerShare,b=g.specialist?.raw?.affoQuarterPerShare;stableDenominator=Array.isArray(a)&&a.length===4&&a.every(x=>finite(x)&&x>0)&&JSON.stringify(a)===JSON.stringify(b);if(stableDenominator){ratioA=before.price/a.reduce((s,x)=>s+x,0);ratioB=after.price/b.reduce((s,x)=>s+x,0);}}
   const sameCurrency=before.currency===after.currency&&!!after.currency&&(['reit','bdc'].includes(profile)?f.specialist?.currency===before.currency&&g.specialist?.currency===after.currency:f.financialCurrency===before.currency&&g.financialCurrency===after.currency);
   const ratioMatches=finite(ratioA)&&finite(ratioB)&&ratioA>0&&Math.abs(ratioB/ratioA-after.price/before.price)<.002;
   kind='price';title=stableDenominator&&ratioMatches&&sameCurrency&&!reportChanged?'Kursbewegung bei gleicher Kennzahl':'Kurs und Bewertungsdaten verändert';note=title.startsWith('Kursbewegung')?'Der gespeicherte Bewertungsquotient folgt der Kursänderung; die Vergleichskennzahl blieb gleich.':'Kurs und Bewertungsquote werden gemeinsam gezeigt; ihr Einfluss wird nicht künstlich einzeln zugerechnet.';
  }
  else if(metrics.length){kind='metric';title='Kennzahl verändert';note=reportChanged?'Veränderte Eingaben mit neuer Berichtsperiode im Datenbestand.':'Die verwendeten Kennzahlen haben sich zwischen den gespeicherten Ständen verändert.';}
  else if(reportChanged&&row.key!=='risk'){kind='report';title='Neue Berichtsperiode';note='Neuer Berichtsstand im Anbieterbestand; Punkte können trotzdem gleich bleiben.';}
  else if(row.state==='points-changed'){kind='unresolved';title='Punkte verändert – Ursache offen';note='Die gespeicherten Eingaben erklären die Differenz nicht vollständig. Regeln und Freigaben prüfen.';}
  else if(row.inputs.length){title='Eingaben verändert, Punkte gleich';note='Die begrenzte oder gerundete Skala kann trotz neuer Eingaben dieselben Punkte liefern.';}
  if(row.state==='unchanged'&&kind!=='unverändert')note+=' Die Kategorie-Punkte blieben unverändert.';
  return {...row,kind,title,note,blocks,metrics};
 });
 return {...d,drivers,reportChanged,reportBefore:reportA,reportAfter:reportB,priceChanged,
  pricePct:priceChanged&&before.currency===after.currency?(after.price/before.price-1)*100:null,
  sameMarketDate:!!before?.marketDate&&before.marketDate===after?.marketDate};
}
// Locale-aware displayed values; absent values stay last in either direction.
function tableSortValue(value,textOnly=false){
 const text=String(value??'').replace(/[\u00a0\u202f]/g,' ').replace(/[−–]/g,'-').trim();
 if(!text||/^(?:[-—]+|n\.?\s*[av]\.?)$/i.test(text))return null;
 if(textOnly)return {type:'text',value:text};
 if(/^(?:null|NaN|fehlt|unbekannt|nicht verfügbar|nicht vergleichbar|keine(?:\s|$)|Teilbewertung$)/i.test(text))return null;
 let date=text.match(/^(\d{4})-(\d{2})-(\d{2})(?:\b|T)/);if(date)return {type:'number',value:Date.UTC(+date[1],+date[2]-1,+date[3])};
 date=text.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})(?:\b|,)/);if(date)return {type:'number',value:Date.UTC(+date[3],+date[2]-1,+date[1])};
 const match=text.match(/^[+\-]?(?:\d[\d .,'’]*\d|\d)(?:e[+\-]?\d+)?/i);
 if(match){let number=match[0].replace(/[ '’]/g,'');if(number.includes(','))number=number.replace(/\./g,'').replace(',','.');else if(/^[+\-]?\d{1,3}(?:\.\d{3})+$/.test(number))number=number.replace(/\./g,'');const n=Number(number);if(Number.isFinite(n))return {type:'number',value:n};}
 return {type:'text',value:text};
}
const tableCollator=new Intl.Collator('de-AT',{numeric:true,sensitivity:'base'});
function compareTableValues(a,b,direction=1){if(a===null)return b===null?0:1;if(b===null)return -1;if(a.type!==b.type)return a.type==='number'?-1:1;return direction*(a.type==='number'?a.value-b.value:tableCollator.compare(a.value,b.value));}
function validateTableSorts(input){
 if(!input||input.version!==1||!input.tables||typeof input.tables!=='object'||Array.isArray(input.tables))throw Error('Ungültige Sortierwahl.');
 const entries=Object.entries(input.tables);if(entries.length>250)throw Error('Zu viele Sortierwahlen.');const tables=Object.create(null);
 for(const [key,value] of entries){if(key.length>2000||!value||typeof value.column!=='string'||value.column.length>240||![1,-1].includes(value.direction))throw Error('Ungültige Sortierwahl.');tables[key]={column:value.column,direction:value.direction};}
 return {version:1,tables};
}
if(typeof module!=='undefined'&&module.exports)module.exports={explainChange,tableSortValue,compareTableValues,validateTableSorts};if(typeof document==='undefined')return;
const $=id=>document.getElementById(id),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),num=(v,d=2)=>finite(v)?v.toLocaleString('de-AT',{maximumFractionDigits:d}):'—',signed=v=>finite(v)?(v>0?'+':'')+num(v)+' P.':'—';
let openInfo;
function renderDrivers({a,b,before,after}){
 const host=$('changeDrivers');if(!host)return;const d=explainChange(a,b,window.CockpitInsights.modelOf(before),window.CockpitInsights.modelOf(after));
 const sum=d.totalDelta!=null?'Gesamt-Score '+signed(d.totalDelta):d.comparable?'Gemeinsam belegte Kategorien '+signed(d.sharedDelta):'Keine vergleichbare Score-Differenz';
 const value=(x,label)=>x==null?'fehlt':Array.isArray(x)?x.map(v=>finite(v)?num(v,4):String(v)).join(' / '):finite(x)?(/Umsatzwachstum|Gewinnwachstum|Operative Marge|ROE/.test(label)?num(x*100)+'%':num(x,4)):String(x);
 host.innerHTML=`<div class="driver-summary"><strong>${esc(sum)}</strong><span>${d.comparable?d.coverageBefore+'% → '+d.coverageAfter+'% Abdeckung':'Modell / Profil getrennt'}</span>${d.pricePct!=null?'<span>Kurs '+(d.pricePct>0?'+':'')+num(d.pricePct)+'%</span>':''}${d.reportChanged?'<span>Berichtsperiode '+esc(d.reportBefore)+' → '+esc(d.reportAfter)+'</span>':''}${d.sameMarketDate?'<span>Gleicher letzter Handelstag</span>':''}</div><div class="driver-grid">${d.drivers.map(r=>`<article class="driver-card"><header><b>${labels[r.key]}</b><strong>${signed(r.delta)}</strong></header><div class="driver-tag">${esc(r.title)}</div><p>${esc(r.note)}</p>${r.inputs.length?'<dl>'+r.inputs.map(x=>'<div><dt>'+esc(x.label)+'</dt><dd>'+esc(value(x.before,x.label))+' → '+esc(value(x.after,x.label))+'</dd></div>').join('')+'</dl>':''}${r.blocks.length?'<p>'+esc(r.blocks.join(' · '))+'</p>':''}</article>`).join('')}</div><p class="driver-footnote">Beobachtete Änderungen. Neue Datenabdeckung ist kein Score-Gewinn.</p>`;
 host.querySelectorAll('.driver-card p').forEach(p=>{if(p.textContent.length>155)p.classList.add('compact-candidate');});
}
window.CockpitExperience={renderDrivers,explainChange};
function boot(){
 const selectionPanel=document.createElement('div');selectionPanel.className='panel';selectionPanel.id='universeSelectionPanel';$('overview').prepend(selectionPanel);
 const groupControls=[];
 for(const id of ['overviewSearch','r71ScoreSearch','lmSearch']){
  const input=$(id);if(!input)continue;
  const label=document.createElement('label');label.textContent='Aktienuniversum ';
  const select=document.createElement('select');select.setAttribute('aria-label','Aktienuniversum '+id);
  select.innerHTML='<option value="all">Alle Aktien</option><option value="original">Bisherige Auswahl · 32 Aktien</option><option value="sp500">S&P 500 · Top 100</option>';
  label.append(select);input.before(label);groupControls.push(select);
  select.onchange=()=>{universeGroup=select.value;groupControls.forEach(s=>s.value=universeGroup);lmRender();lsRender();};
 }
 function renderUniverseBadges(){
  const all=lmState.data?.quotes||[];
  for(const row of document.querySelectorAll('#overviewRows tr,#lmRows tr')){
   const ticker=row.dataset.ticker||row.querySelector('[data-open-score]')?.dataset.openScore;
   const q=all.find(q=>q.ticker===ticker),cell=row.cells[0];if(!q?.sp500Top100||!cell)continue;
   if(cell.querySelector('.universe-rank'))continue;
   const badge=document.createElement('small');badge.className='universe-rank';badge.style.display='block';badge.textContent='S&P-Rang ≈ '+q.sp500Top100.rank+' · Gewicht ≈ '+num(q.sp500Top100.weightProxyPct,3)+'%';cell.append(badge);
  }
 }
 for(const id of ['overviewRows','lmRows'])if($(id))new MutationObserver(renderUniverseBadges).observe($(id),{childList:true});
 function renderUniverseSelection(){
  const all=lmState.data?.quotes||[],meta=lmState.data?.universeSelection;if(!all.length)return;
  renderUniverseBadges();
  document.querySelector('.brand-eyebrow').textContent='Investment Research · '+all.length+' Aktien';
  const subtitle=$('overviewRows')?.closest('.panel')?.querySelector('.dashboard-panel-head p');if(subtitle)subtitle.textContent=all.length+' Aktien · '+all.filter(q=>q.sp500Top100).length+' im S&P-500-Top-100-Snapshot';
  if(!meta){selectionPanel.textContent='Universum wird geladen …';return;}
  selectionPanel.innerHTML=`<b>${all.length} Aktien · 100 S&P-500-Positionen · ${all.filter(q=>q.originalUniverse===false).length} Ergänzungen</b><p class="muted">Auswahlstand ${esc(meta.asOf)} · Rangfolge nach Indexgewicht, angenähert durch SPY-Bestände.</p><details><summary>Auswahl, Gewichte & Quelle ⓘ</summary><p>Feste Auswahl der 100 größten Aktienpositionen aus den täglichen SPY-Beständen. Fondsgewichte dienen als Näherung für die streubesitzbereinigten S&P-500-Indexgewichte. Originalgewichte von S&P sind nicht unabhängig bestätigt. Aktienklassen zählen einzeln; Überschneidungen mit der bisherigen Auswahl werden einmal geführt.</p><p>Die Auswahl wird nicht automatisch ausgetauscht. Rückblicke auf heutige Top-100-Aktien enthalten Auswahl- und Survivorship-Bias. Historische Finanzdaten werden je Aktie separat belegt.</p><a href="${esc(meta.sourceUrl)}" target="_blank" rel="noopener noreferrer">Originalbestände von State Street ↗</a> · <a href="./data/sp500-selection.json" target="_blank" rel="noopener noreferrer">Vollständige Auswahl mit Rang und Gewichts-Näherung ↗</a><p class="muted">SHA256 ${esc(meta.sourceSha256)}</p></details>`;
 }
 const previousUniverseRender=lmRender;lmRender=function(){previousUniverseRender();renderUniverseSelection();};renderUniverseSelection();
 const root=document.documentElement;let themePreference;try{themePreference=localStorage.getItem('cockpit-theme');}catch{};
 const system=window.matchMedia('(prefers-color-scheme: light)');
 const toggle=$('themeToggle');
 function setTheme(theme,save){root.dataset.theme=theme;if(save){themePreference=theme;try{localStorage.setItem('cockpit-theme',theme);}catch{}}toggle.setAttribute('aria-pressed',String(theme==='light'));toggle.setAttribute('aria-label',theme==='light'?'Dunklen Modus aktivieren':'Hellen Modus aktivieren');toggle.innerHTML=(theme==='light'?'☾':'☀')+' <span>'+(theme==='light'?'Dark Mode':'Light Mode')+'</span>';}
 setTheme(themePreference==='light'||themePreference==='dark'?themePreference:system.matches?'light':'dark',false);toggle.onclick=()=>setTheme(root.dataset.theme==='light'?'dark':'light',true);system.addEventListener?.('change',e=>{if(!themePreference)setTheme(e.matches?'light':'dark',false);});
 document.querySelector('.brand-subtitle').textContent='Aktien verstehen. Entwicklungen vergleichen.';
 const info=document.createElement('dialog');info.id='infoDialog';info.className='cockpit-dialog';info.setAttribute('aria-labelledby','infoTitle');info.innerHTML='<header><h2 id="infoTitle"></h2><button type="button" class="dialog-close" aria-label="Information schließen">✕</button></header><div id="infoBody"></div>';
 document.body.append(info);let opener=null;
 openInfo=(title,node,trigger)=>{opener=trigger||document.activeElement;$('infoTitle').textContent=title;$('infoBody').replaceChildren();const copy=node.cloneNode(true);copy.hidden=false;copy.removeAttribute('id');copy.querySelectorAll('[id]').forEach(n=>n.removeAttribute('id'));if(copy.tagName==='DETAILS'){copy.open=true;copy.querySelector(':scope > summary')?.remove();}$('infoBody').append(copy);info.showModal();info.querySelector('.dialog-close').focus();};
 info.querySelector('.dialog-close').onclick=()=>info.close();info.addEventListener('close',()=>opener?.isConnected&&opener.focus());info.addEventListener('click',e=>{const r=info.getBoundingClientRect();if(e.target===info&&(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom))info.close();});
 const method=document.querySelector('.research-note');$('headerMethod').onclick=e=>openInfo('Methodik & Datenqualität',method.querySelector('details')||method,e.currentTarget);method.hidden=true;
 const nav=document.createElement('dialog');nav.id='mobileMenu';nav.className='cockpit-dialog menu-dialog';nav.setAttribute('aria-labelledby','menuTitle');nav.innerHTML='<header><h2 id="menuTitle">Navigation</h2><button type="button" class="dialog-close" aria-label="Menü schließen">✕</button></header><nav aria-label="Mobile Navigation" id="mobileMenuLinks"></nav>';document.body.append(nav);
 function closeMenu(){nav.close();$('menuToggle').setAttribute('aria-expanded','false');}
 function menu(){const out=$('mobileMenuLinks');out.replaceChildren();document.querySelectorAll('#primaryNav button').forEach(button=>{const group=button.dataset.group;const section=document.createElement('section');const title=document.createElement('h3');title.textContent=button.textContent.trim();section.append(title);for(const id of NAV_GROUPS[group]||[]){const source=document.querySelector('#tabs [data-v="'+id+'"]');const link=document.createElement('button');link.type='button';link.textContent=source?.textContent||title.textContent;link.className='menu-item';link.setAttribute('aria-current',$(id)?.classList.contains('active')?'page':'false');link.onclick=()=>{closeMenu();show(id);window.scrollTo({top:0,behavior:'instant'});};section.append(link);}out.append(section);});nav.showModal();$('menuToggle').setAttribute('aria-expanded','true');nav.querySelector('[aria-current="page"]')?.focus();}
 $('menuToggle').onclick=menu;nav.querySelector('.dialog-close').onclick=closeMenu;nav.addEventListener('close',()=>{$('menuToggle').setAttribute('aria-expanded','false');$('menuToggle').focus();});nav.addEventListener('click',e=>{const r=nav.getBoundingClientRect();if(e.target===nav&&(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom))closeMenu();});
 const quick=document.createElement('nav');quick.className='mobile-quicknav';quick.setAttribute('aria-label','Schnellnavigation');quick.innerHTML='<button data-quick="overview">Übersicht</button><button data-quick="company">Aktien</button><button data-quick="reconstruction">Verlauf</button><button data-menu-open>☰ Menü</button>';document.body.append(quick);quick.querySelector('[data-menu-open]').onclick=menu;quick.querySelectorAll('[data-quick]').forEach(b=>b.onclick=()=>{show(b.dataset.quick);window.scrollTo({top:0,behavior:'instant'});});
 const scopeButtons=new WeakMap();
 function compact(){
  document.querySelectorAll('[data-model-scope]').forEach(original=>{original.hidden=true;if(scopeButtons.has(original))return;const button=document.createElement('button');button.type='button';button.className='info-button scope-info';button.textContent='ⓘ Datenstand & Modell';button.setAttribute('aria-haspopup','dialog');button.onclick=()=>openInfo('Datenstand & Modell',original,button);scopeButtons.set(original,button);original.after(button);});
  for(const id of ['reconNotice','evaluationNotice','historyNotice','r71CompareNotice']){const original=$(id);if(!original||!original.textContent.trim())continue;original.hidden=true;let box=$(id+'Compact');if(!box){box=document.createElement('div');box.id=id+'Compact';box.className='dashboard-note compact-notice';const text=document.createElement('strong'),button=document.createElement('button');button.type='button';button.className='info-button';button.textContent='ⓘ Details';button.setAttribute('aria-haspopup','dialog');button.onclick=()=>openInfo('Einordnung & Datenbasis',original,button);box.append(text,button);original.after(box);}const label=id==='reconNotice'?'Teilbewertung · Quellenabdeckung & Datenlücken':original.querySelector('strong')?.textContent||original.textContent.trim().slice(0,140);if(box.firstChild.textContent!==label)box.firstChild.textContent=label;}
  document.querySelectorAll('.view details:not([data-info-ready])').forEach(details=>{const summary=details.querySelector(':scope > summary');if(!summary||!/(Methodik|Grenzen|Quellen|Eingaben und|Prüfprotokoll|technische|Zusätzliche Anbieter|Regeln.*Begründungen)/i.test(summary.textContent)||details.querySelector('input,select'))return;details.dataset.infoReady='true';details.open=false;summary.classList.add('info-summary');summary.onclick=e=>{e.preventDefault();openInfo(summary.textContent.trim(),details,summary);};summary.setAttribute('role','button');summary.setAttribute('aria-haspopup','dialog');});
  document.querySelectorAll('.view p:not([id]):not([data-compact]), .view p.compact-candidate:not([data-compact])').forEach(p=>{
   if(p.closest('details,.driver-summary,table,.mobile-table-cards')||p.querySelector('input,select,button')||p.textContent.trim().length<210)return;p.dataset.compact='true';p.hidden=true;const box=document.createElement('div');box.className='compact-copy';const text=document.createElement('span');const original=p.textContent.trim();text.textContent=original.match(/^.{20,145}?[.!?](?:\s|$)/)?.[0]?.trim()||'Details zu Methode und Datenbasis';const button=document.createElement('button');button.type='button';button.className='info-button';button.textContent='ⓘ Details';button.setAttribute('aria-haspopup','dialog');button.onclick=()=>openInfo(p.closest('.panel,.next-hero,.evidence-details')?.querySelector('h2,h3')?.textContent||'Methode & Datenbasis',p,button);box.append(text,button);p.after(box);
  });
  document.querySelectorAll('.company-part:not([data-compact])').forEach(part=>{const explanation=part.querySelectorAll('p')[1],source=part.querySelector('small');if(!explanation)return;part.dataset.compact='true';const detail=document.createElement('div');detail.append(explanation.cloneNode(true));if(source)detail.append(source.cloneNode(true));explanation.hidden=true;if(source)source.hidden=true;const b=document.createElement('button');b.className='info-button';b.textContent='ⓘ Berechnung & Quelle';b.setAttribute('aria-haspopup','dialog');b.onclick=()=>openInfo(part.querySelector('b')?.textContent||'Berechnung',detail,b);part.append(b);});
  document.querySelectorAll('.tbl:not([data-scroll-ready])').forEach(t=>{t.dataset.scrollReady='true';t.setAttribute('tabindex','0');t.setAttribute('role','region');t.setAttribute('aria-label',(t.closest('.panel')?.querySelector('h2,h3')?.textContent||'Datentabelle')+' · horizontal scrollbar');});
 }
 const cardRoots=['r71CompareRows','reconRows','deltaRows','r71ScoreRows'];
 function cardValue(cell){
  const clone=cell.cloneNode(true);clone.querySelectorAll('button,details').forEach(n=>n.remove());
  clone.querySelectorAll('small,strong,div,br').forEach(n=>n.before(document.createTextNode(' · ')));
  return clone.textContent.replace(/\s+/g,' ').replace(/(?:\s*·\s*)+/g,' · ').replace(/^[\s·]+|[\s·]+$/g,'');
 }
 function cards(id){
  const tbody=$(id);if(!tbody)return;const wrap=tbody.closest('.tbl');let target=$(id+'Mobile');
  if(!target){target=document.createElement('div');target.id=id+'Mobile';target.className='mobile-table-cards';wrap.classList.add('has-mobile-cards');wrap.after(target);}
  const headings=[...tbody.closest('table').querySelectorAll('thead th')].map(n=>n.textContent.trim());target.replaceChildren();
  [...tbody.rows].forEach(row=>{
   const cells=[...row.cells];if(cells.length<2){target.textContent=row.textContent;return;}
   const card=document.createElement('article');card.className='mobile-data-card';const title=document.createElement('h3');title.textContent=cells[0].querySelector('b')?.textContent||cells[0].textContent.trim();card.append(title);
   const list=document.createElement('dl');cells.slice(1).forEach((cell,i)=>{const val=cardValue(cell);if(!val)return;const field=document.createElement('div'),label=document.createElement('dt'),value=document.createElement('dd');label.textContent=headings[i+1]||'';value.textContent=val;field.append(label,value);list.append(field);});card.append(list);
   if(id==='r71CompareRows'){
    const evidence=document.createElement('div');cells.forEach((cell,i)=>{const heading=document.createElement('h3');heading.textContent=headings[i];const content=cell.cloneNode(true);content.querySelectorAll('button').forEach(n=>n.remove());const section=document.createElement('div');section.append(...content.childNodes);evidence.append(heading,section);});
    const help=document.createElement('button');help.type='button';help.className='info-button';help.textContent='ⓘ Kennzahlen & Quellen';help.onclick=()=>openInfo(title.textContent,evidence,help);card.append(help);
   }
   cells.forEach(cell=>cell.querySelectorAll('button:not([data-hub-star])').forEach(source=>{const b=document.createElement('button');b.type='button';b.textContent=source.textContent;b.onclick=()=>source.click();card.append(b);}));target.append(card);
  });
 }
 cardRoots.forEach(id=>{if($(id))new MutationObserver(()=>cards(id)).observe($(id),{childList:true});cards(id);});
 const tableStates=new WeakMap(),pendingTables=new Set();let tableQueue=false;
 const SORT_KEY='cockpit-table-sorts-v1';let savedSorts={version:1,tables:Object.create(null)};
 try{const raw=localStorage.getItem(SORT_KEY);if(raw)savedSorts=validateTableSorts(JSON.parse(raw));}catch(e){/* Sorting remains usable if browser preferences cannot be read. */}
 function tablePreferenceKey(table,state){const body=table.tBodies[0];if(body?.id)return 'body:'+body.id;if(table.id)return 'table:'+table.id;const owner=table.parentElement.closest('[id]');if(!owner)return null;const siblings=[...owner.querySelectorAll('table')];return 'view:'+owner.id+':'+state.headers.map(h=>h.label).join('|')+':'+Math.max(0,siblings.indexOf(table));}
 function persistTableSort(table,state){
  const header=state.headers.find(h=>h.column===state.column);if(!state.preferenceKey||!header)return;
  let latest=savedSorts;try{const raw=localStorage.getItem(SORT_KEY);if(raw)latest=validateTableSorts(JSON.parse(raw));}catch(e){}
  const next={version:1,tables:{...latest.tables,[state.preferenceKey]:{column:header.label,direction:state.direction}}};
  try{const clean=validateTableSorts(next);localStorage.setItem(SORT_KEY,JSON.stringify(clean));savedSorts=clean;if(state.feedback)state.feedback.hidden=true;}
  catch(e){if(!state.feedback){state.feedback=document.createElement('p');state.feedback.className='hub-status';state.feedback.setAttribute('role','status');(table.closest('.tbl')||table).before(state.feedback);}state.feedback.textContent='Sortierwahl konnte nicht gespeichert werden. Die Sortierung gilt für diesen Seitenaufruf.';state.feedback.hidden=false;}
 }
 const tableStyle=document.createElement('style');tableStyle.textContent=`button.table-sort-header{display:inline-flex;align-items:center;gap:7px;min-height:36px;min-width:0!important;padding:4px 0!important;border:0!important;border-radius:0;background:transparent!important;color:inherit;font:inherit;letter-spacing:inherit;text-transform:inherit;text-align:left;white-space:normal}button.table-sort-header::after{content:'↕';font-size:12px;opacity:.65}th[aria-sort=ascending]>.table-sort-header::after{content:'↑';opacity:1}th[aria-sort=descending]>.table-sort-header::after{content:'↓';opacity:1}.table-sort-mobile{display:none}.table-sort-mobile label{display:flex;align-items:center;gap:8px;min-width:0;flex:1;flex-wrap:wrap}.table-sort-mobile select{max-width:100%;min-width:0;min-height:44px;font-size:16px}.table-sort-mobile button{min-height:44px}@media(max-width:760px){.table-sort-mobile{display:flex;align-items:flex-end;gap:8px;flex-wrap:wrap;margin:14px 0}html[data-table-sort-ready] #overviewSort{display:none}}`;document.head.append(tableStyle);
 const categoricalHeader=label=>/^(?:aktie|unternehmen|name|ticker|kategorie|komponente|faktor|strategie|profil|branche|modell$|quelle$|endpunkt|status|basis\s*\/|datencheck|feld$|xbrl|accession|währung|income$|bilanz$|freigabe)/i.test(label);
 function cellSortValue(cell,header){
  if(cell.hasAttribute('data-sort-value'))return tableSortValue(cell.dataset.sortValue,cell.dataset.sortType==='text');
  const copy=cell.cloneNode(true);copy.querySelectorAll('button,details,svg,progress,.universe-rank,[aria-hidden=true]').forEach(e=>e.remove());
  const walker=document.createTreeWalker(copy,NodeFilter.SHOW_TEXT),texts=[];while(walker.nextNode()){const t=walker.currentNode.textContent.trim();if(t)texts.push(t);}
  if(categoricalHeader(header))return tableSortValue(texts[0]||'',true);
  // Ignore secondary footnotes; metric tables may put a label before the value.
  const primary=copy.cloneNode(true);primary.querySelectorAll('small,.r71-caption,.muted').forEach(e=>e.remove());
  const nodes=document.createTreeWalker(primary,NodeFilter.SHOW_TEXT),values=[];while(nodes.nextNode()){const t=nodes.currentNode.textContent.trim();if(t)values.push(t);}
  const candidates=values.length?values:texts;for(const text of candidates){const value=tableSortValue(text);if(value===null)return null;if(value.type==='number')return value;}
  return tableSortValue(candidates[0]||'');
 }
 function tableIndicators(table,state){
  state.headers.forEach(h=>{const current=state.column===h.column;h.cell.setAttribute('aria-sort',current?(state.direction===1?'ascending':'descending'):'none');h.button.setAttribute('aria-label',h.label+' · '+(current?(state.direction===1?'aufsteigend':'absteigend')+' sortiert · ':'')+(current&&state.direction===1?'Absteigend':'Aufsteigend')+' sortieren');});
  if(state.select){state.select.value=state.column==null?'':String(state.column);state.directionButton.textContent=state.direction===1?'↑ Aufsteigend':'↓ Absteigend';}
  if(table.tBodies[0]?.id==='overviewRows'&&state.column!=null){const select=$('overviewSort');let option=select.querySelector('[data-header-sort-option]');if(!option){option=document.createElement('option');option.value='header';option.disabled=true;option.dataset.headerSortOption='';select.append(option);}const label=state.headers.find(h=>h.column===state.column)?.label;const text=label+' '+(state.direction===1?'↑':'↓')+' · Spaltenkopf';if(option.textContent!==text)option.textContent=text;select.value='header';}
 }
 function sortTableRows(table,state){
  if(state.column==null)return;const header=state.headers.find(h=>h.column===state.column);if(!header)return;
  for(const body of table.tBodies){const before=[...body.rows],after=[];let group=[];const flush=()=>{after.push(...group.map((row,index)=>({row,index,key:cellSortValue(row.cells[state.column],header.label)})).sort((a,b)=>compareTableValues(a.key,b.key,state.direction)||a.index-b.index).map(x=>x.row));group=[];};
   for(const row of before){if(row.cells.length>state.column&&[...row.cells].every(c=>c.colSpan===1&&c.rowSpan===1)&&!row.querySelector('th'))group.push(row);else{flush();after.push(row);}}flush();
   if(after.some((row,i)=>row!==before[i]))body.replaceChildren(...after);
  }
  tableIndicators(table,state);
 }
 function chooseTableSort(table,state,column){state.direction=state.column===column?-state.direction:1;state.column=column;sortTableRows(table,state);persistTableSort(table,state);}
 function enhanceTable(table){
  let state=tableStates.get(table);if(state){sortTableRows(table,state);return;}
  const row=table.tHead?.rows[table.tHead.rows.length-1];if(!row)return;state={headers:[],column:null,direction:1};tableStates.set(table,state);
  let column=0;for(const cell of row.cells){const index=column;column+=cell.colSpan;const label=cell.textContent.trim();if(cell.tagName!=='TH'||cell.colSpan!==1||!label||/^(?:Details|Aktion(?:en)?)$/i.test(label))continue;
   const button=document.createElement('button');button.type='button';button.className='table-sort-header';button.textContent=label;button.onclick=e=>{e.stopPropagation();chooseTableSort(table,state,index);};cell.replaceChildren(button);cell.scope='col';state.headers.push({cell,button,label,column:index});
  }
  const body=table.tBodies[0],mobile=body&&(body.id==='overviewRows'||cardRoots.includes(body.id));
  if(mobile&&state.headers.length){const controls=document.createElement('div');controls.className='table-sort-mobile';const label=document.createElement('label'),select=document.createElement('select'),button=document.createElement('button'),empty=document.createElement('option');label.append(document.createTextNode('Sortieren nach '));select.setAttribute('aria-label','Spalte zum Sortieren · '+(table.closest('.panel')?.querySelector('h2,h3')?.textContent||'Tabelle'));empty.value='';empty.disabled=true;empty.textContent='Aktuelle Reihenfolge';select.append(empty);for(const h of state.headers){const option=document.createElement('option');option.value=h.column;option.textContent=h.label;select.append(option);}select.onchange=()=>{if(select.value===''){state.column=null;tableIndicators(table,state);return;}state.column=Number(select.value);state.direction=1;sortTableRows(table,state);persistTableSort(table,state);};button.type='button';button.className='secondary';button.onclick=()=>{if(state.column==null){state.column=state.headers[0].column;state.direction=1;}else state.direction=-state.direction;sortTableRows(table,state);persistTableSort(table,state);};label.append(select);controls.append(label,button);table.closest('.tbl')?.before(controls);state.select=select;state.directionButton=button;}
  state.preferenceKey=tablePreferenceKey(table,state);const preference=savedSorts.tables[state.preferenceKey],restored=preference&&state.headers.find(h=>h.label===preference.column);if(restored){state.column=restored.column;state.direction=preference.direction;sortTableRows(table,state);}tableIndicators(table,state);document.documentElement.dataset.tableSortReady='';
 }
 function scheduleTable(table){pendingTables.add(table);if(tableQueue)return;tableQueue=true;queueMicrotask(()=>{tableQueue=false;const tables=[...pendingTables];pendingTables.clear();tables.forEach(t=>{if(t.isConnected)enhanceTable(t);});});}
 new MutationObserver(changes=>{for(const change of changes){const table=change.target.closest?.('table');if(table)scheduleTable(table);for(const node of change.addedNodes)if(node.nodeType===1){if(node.matches('table'))scheduleTable(node);node.querySelectorAll('table').forEach(scheduleTable);}}}).observe(document.body,{childList:true,subtree:true});
 document.querySelectorAll('table').forEach(enhanceTable);
 if($('overviewSort'))$('overviewSort').querySelector('option[value=score]').textContent='Score / Teilpunkte absteigend';
 $('overviewSort')?.addEventListener('change',()=>{const table=$('overviewRows').closest('table'),state=tableStates.get(table),choice={name:[0,1],score:[5,-1],ytd:[2,-1],pe:[3,1]}[$('overviewSort').value];if(state&&choice){[state.column,state.direction]=choice;sortTableRows(table,state);persistTableSort(table,state);}});
 let queued=false;new MutationObserver(()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;compact();});}).observe(document.querySelector('.app'),{subtree:true,childList:true});
 const oldShow=show;show=function(view,hash=true){oldShow(view,hash);document.title='Investment Cockpit · '+(document.querySelector('#tabs button.active')?.textContent||'Übersicht');quick.querySelectorAll('[data-quick]').forEach(b=>b.setAttribute('aria-current',b.dataset.quick===view?'page':'false'));compact();requestAnimationFrame(()=>{const tabs=$('tabs'),active=tabs.querySelector('button.active');if(active&&active.offsetParent){const left=active.getBoundingClientRect().left-tabs.getBoundingClientRect().left+tabs.scrollLeft,right=left+active.offsetWidth;const target=left<tabs.scrollLeft?left:right>tabs.scrollLeft+tabs.clientWidth?right-tabs.clientWidth:tabs.scrollLeft;tabs.scrollTo?.({left:Math.max(0,target),behavior:'instant'});}redraw();});};
 let lastWidth=0,timer;function redraw(){const view=document.querySelector('.view.active')?.id;const ids={company:'companyTicker',compare:'r71CompareTickers',reconstruction:'reconMetric',scoreHistory:'historyMetric',scoreEvaluation:'evaluationSegment',live:'lmTicker'};let control=$(ids[view]);if(control?.tagName!=='SELECT')control=control?.querySelector('select');control?.dispatchEvent(new Event('change'));window.dispatchEvent(new Event('cockpitresize'));}
 if(window.ResizeObserver)new ResizeObserver(entries=>{const width=Math.round(entries[0].contentRect.width);if(width===lastWidth)return;lastWidth=width;clearTimeout(timer);timer=setTimeout(redraw,100);}).observe(document.querySelector('.app'));
 compact();show(document.querySelector('.view.active')?.id||'overview',false);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
// A small task-based navigation; legacy calculations are kept out of the UI.
function simplifyWorkspace(){
 if(document.documentElement.dataset.cockpitUx)return;
 document.documentElement.dataset.cockpitUx='current';
 const groups={overview:['overview'],analyse:['company','liveScore','live','opportunityScanner'],watch:['watchlists'],compare:['compare','benchmarkCompare','comparisonWorkspace','sectorPeers'],zeit:['reconstruction','scoreHistory','scoreChanges','financialHistory','scoreEvaluation'],daten:['evidence','validation','reportMonitor','researchGaps','audit','profiles']};
 const titles={overview:'Übersicht',analyse:'Aktien',watch:'Watchlists',compare:'Vergleichen',zeit:'Verlauf',daten:'Daten'};
 const views={overview:'Übersicht',company:'Einzelaktie',liveScore:'Scores & Kategorien',live:'Kurse & Kennzahlen',opportunityScanner:'Chancen suchen',watchlists:'Meine Watchlists',compare:'Aktien vergleichen',benchmarkCompare:'Mit Index vergleichen',comparisonWorkspace:'Score-Verläufe vergleichen',sectorPeers:'Branchenvergleich',reconstruction:'Historischer Score · 5 Jahre',scoreHistory:'Täglich erfasste Scores',scoreChanges:'Score-Änderungen',financialHistory:'Historische Kennzahlen',scoreEvaluation:'Score-Auswertung',evidence:'Datenqualität',validation:'Konsistenzprüfung',reportMonitor:'Quartalsberichte',researchGaps:'Offene Datenprüfungen',audit:'Quellen & Aktualisierung',profiles:'Score-Methodik'};
 const subtitles={analyse:'Eine Aktie untersuchen oder das gesamte Universum durchsuchen.',compare:'Aktuelle Kennzahlen, Kursrenditen oder historische Scores vergleichen.',zeit:'Historische Entwicklung im aktuellen Modell · Datenlücken bleiben sichtbar.',daten:'Quellen prüfen, Datenlücken verstehen und die aktuelle Methodik nachlesen.'};
 const aliases={stocks:'liveScore',history:'financialHistory',fund:'financialHistory',quantum:'company',combined:'liveScore',partial:'liveScore',weights:'profiles',universe:'scoreEvaluation',backtest:'scoreEvaluation',integrity:'validation',pit:'validation'};
 Object.keys(NAV_GROUPS).forEach(k=>delete NAV_GROUPS[k]);Object.assign(NAV_GROUPS,groups);
 Object.keys(NAV_FOR_VIEW).forEach(k=>delete NAV_FOR_VIEW[k]);
 for(const [g,ids] of Object.entries(groups)){ids.forEach(id=>NAV_FOR_VIEW[id]=g);NAV_DEFAULT[g]=ids[0];NAV_LAST[g]=ids[0];NAV_META[g]=[titles[g],subtitles[g]||''];}
 const tabs=$('tabs');
 tabs.querySelectorAll('button').forEach(b=>{if(!NAV_FOR_VIEW[b.dataset.v])b.remove();});
 for(const ids of Object.values(groups))for(const id of ids){let b=tabs.querySelector('[data-v="'+id+'"]');if(!b){b=document.createElement('button');b.type='button';b.dataset.v=id;b.onclick=()=>show(id);tabs.append(b);}b.textContent=views[id];tabs.append(b);}
 const primary=$('primaryNav');primary.replaceChildren();
 for(const g of Object.keys(groups)){const b=document.createElement('button');b.type='button';b.dataset.group=g;b.textContent=titles[g];b.onclick=()=>show(NAV_DEFAULT[g]);primary.append(b);}
 for(const id of Object.keys(aliases)){const section=$(id);if(section){section.hidden=true;section.setAttribute('inert','');}}
 // One overview entry point, rather than multiple launch strips above the title.
 const overview=$('overview');overview.querySelectorAll('.wb-launch,.hub-launch').forEach(e=>e.remove());
 const universe=$('universeSelectionPanel');if(universe)$('validation').append(universe);
 const hero=overview.querySelector('.dashboard-hero');hero.querySelector('h2').textContent='Deine Aktien im Überblick.';hero.querySelector('p').textContent='Aktien finden, Scores prüfen und Entwicklungen vergleichen.';hero.querySelector('.dashboard-eyebrow').textContent='Dein Research-Arbeitsplatz';
 const find=document.createElement('button');find.type='button';find.id='uxFindStocks';find.textContent='Aktie suchen';find.onclick=()=>{$('overviewSearch').focus();$('overviewSearch').scrollIntoView({block:'center',behavior:'smooth'});};
 hero.querySelector('.dashboard-actions').prepend(find);$('overviewHistory').textContent='Score-Verlauf ansehen';$('overviewHistory').classList.add('secondary');$('overviewValidation').hidden=true;if($('overviewChanges'))$('overviewChanges').hidden=true;
 const stockPanel=$('overviewRows').closest('.panel');stockPanel.id='overviewStocksPanel';stockPanel.querySelector('h3').textContent='Aktien entdecken';$('overviewPrices').textContent='Aktien vergleichen →';
 const controls=$('overviewSearch').closest('.dashboard-controls');controls.classList.add('ux-stock-filters');
 function field(input,title){const label=document.createElement('label');label.textContent=title;input.before(label);label.append(input);return label;}
 const searchLabel=field($('overviewSearch'),'Suche');searchLabel.className='ux-search';controls.prepend(searchLabel);field($('overviewSort'),'Sortierung');
 const reset=document.createElement('button');reset.type='button';reset.id='overviewResetFilters';reset.className='dashboard-link';reset.textContent='Filter zurücksetzen';reset.onclick=()=>{$('overviewSearch').value='';controls.querySelector('[aria-label="Aktienuniversum overviewSearch"]').value='all';controls.querySelector('[aria-label="Aktienuniversum overviewSearch"]').dispatchEvent(new Event('change'));$('overviewWatchlist').value='all';$('overviewWatchlist').dispatchEvent(new Event('change'));$('overviewSearch').dispatchEvent(new Event('input'));$('overviewSearch').focus();};$('overviewWatchlistCount').after(reset);
 const help=document.createElement('button');help.type='button';help.className='info-button';help.textContent='ⓘ Score & Datencheck';help.setAttribute('aria-haspopup','dialog');help.onclick=()=>{const content=document.createElement('div');content.innerHTML='<p><b>Score:</b> Heuristische Bewertung mit bis zu 100 Punkten. Ein Gesamtwert erscheint nur bei vollständiger Modellabdeckung. Teilpunkte werden nicht hochgerechnet.</p><p><b>Abdeckung:</b> Anteil der berechenbaren Modellkategorien. 100% bedeutet keine unabhängige Bestätigung der Daten.</p><p><b>Datencheck:</b> Zeigt Primärabgleich, offene Prüfungen oder Abweichungen. Vergleiche möglichst ähnliche Branchen und Profile.</p><p>YTD ist die Kursveränderung seit Jahresbeginn. Kurse in verschiedenen Währungen sind nicht direkt vergleichbar.</p>';openInfo('Scores richtig lesen',content,help);};reset.after(help);
 const extras=document.createElement('details');extras.id='overviewInsights';extras.className='panel ux-insights';extras.dataset.infoReady='';const summary=document.createElement('summary');summary.textContent='Marktüberblick & aktuelle Änderungen';extras.append(summary);
 const grid=overview.querySelector('.dashboard-grid'),feed=overview.querySelector('.change-feed'),monitor=$('monitorOverviewStrip');for(const node of [feed,grid,monitor])if(node)extras.append(node);
 const footer=overview.querySelector('.dashboard-footer');overview.insertBefore(extras,footer);$('overviewStats').after(stockPanel);
 // The model choice is fixed to the current model, dates remain selectable.
 $('historyModel')?.closest('label')?.setAttribute('hidden','');
 const style=document.createElement('style');style.id='taskNavigationStyle';style.textContent=`
 html[data-theme] .primary-navigation{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:5px;overflow:visible}
 html[data-theme] .primary-navigation button{min-width:0;min-height:46px;justify-content:center;font-size:14px;padding:10px 12px}
 html[data-theme] .navigation-panel{padding:6px;margin-bottom:22px;background:var(--surface);border:1px solid var(--line)}
 html[data-theme] .subnav-shell{padding:0 0 16px;margin:0 0 20px;display:block}
 html[data-theme] .subnav-description{max-width:none}.subnav-title{font-size:19px!important}
 html[data-theme] #tabs{display:flex;flex-wrap:wrap;overflow:visible;gap:6px;margin-top:12px}
 html[data-theme] #tabs button{min-height:42px;padding:9px 12px;white-space:normal}
 #overview>.scope-info{display:none!important}#overview .overview-ring{display:none}
 html[data-theme] #overview .dashboard-hero{margin:10px 0 16px}html[data-theme] #overview .dashboard-hero h2{font-size:clamp(26px,3.1vw,38px);max-width:none;margin:8px 0}
 #overview .dashboard-hero p{margin:8px 0}#overview .dashboard-actions{margin-top:14px}
 html[data-theme] #overview .dashboard-stat{padding:14px 16px}#overview .dashboard-stat strong{font-size:26px;margin:7px 0}
 .ux-stock-filters{display:grid!important;grid-template-columns:minmax(200px,2fr) repeat(3,minmax(145px,1fr));align-items:end}
 .ux-stock-filters label{display:flex;flex-direction:column;gap:6px;min-width:0;font-size:12px;color:var(--muted)}
 .ux-stock-filters :is(input,select){width:100%;min-width:0;min-height:44px}
 #overviewResetFilters{min-height:40px;margin:0 12px 8px 0}#overviewWatchlistCount{margin-bottom:4px}
 .ux-insights{margin-top:20px}.ux-insights>summary{cursor:pointer;font-size:16px;font-weight:650;min-height:36px;padding:5px 0}.ux-insights[open]>summary{margin-bottom:20px}.ux-insights .change-feed{margin:0 0 20px}
 .history-controls{grid-template-columns:1fr 1fr!important}#overview .dashboard-footer{margin:20px 0}
 @media(max-width:1000px){.ux-stock-filters{grid-template-columns:1fr 1fr}}
 @media(max-width:760px){html[data-theme] .primary-navigation{display:none}html[data-theme] .navigation-panel{display:none}html[data-theme] #secondaryNav{margin-top:4px}html[data-theme] #tabs{display:grid;grid-template-columns:1fr 1fr;width:100%}html[data-theme] #tabs button{font-size:12px;min-width:0}html[data-theme] .ux-stock-filters{grid-template-columns:1fr 1fr}html[data-theme] .ux-stock-filters .ux-search{grid-column:1/-1}html[data-theme] #overview .dashboard-hero h2{font-size:28px}html[data-theme] #overview .dashboard-hero{margin-top:0}html[data-theme] .menu-toggle{display:inline-flex!important}.menu-dialog #mobileMenuLinks{display:grid;grid-template-columns:1fr;gap:18px}.menu-dialog section{border-bottom:1px solid var(--line);padding-bottom:12px}.menu-dialog h3{margin:0 0 6px}.menu-dialog .menu-item{min-height:44px}}
 `;document.head.append(style);
 const quick=document.querySelector('.mobile-quicknav');if(quick){quick.innerHTML='<button data-quick="overview">Übersicht</button><button data-quick="watchlists">Watchlists</button><button data-quick="compare">Vergleichen</button><button data-menu-open>☰ Menü</button>';quick.querySelectorAll('[data-quick]').forEach(b=>b.onclick=()=>show(b.dataset.quick));quick.querySelector('[data-menu-open]').onclick=()=>$('menuToggle').click();}
 const previousShow=show;
 show=function(view,writeHash=true){const target=aliases[view]|| (NAV_FOR_VIEW[view]?view:'overview'),before=document.querySelector('.view.active')?.id;previousShow(target,writeHash);$('secondaryNav').hidden=groups[NAV_FOR_VIEW[target]].length===1;
  if(target!==view)history.replaceState(null,'','#'+target);
  quick?.querySelectorAll('[data-quick]').forEach(b=>b.setAttribute('aria-current',b.dataset.quick===target?'page':'false'));
  if(before!==target){window.scrollTo({top:0,behavior:'instant'});const heading=$(target)?.querySelector('h2,h3');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}}
 };
 window.addEventListener('hashchange',()=>{const route=location.hash.slice(1);if(!NAV_FOR_VIEW[route])show(route,false);});
 show(location.hash.slice(1)||'overview',false);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(simplifyWorkspace,0),{once:true});else setTimeout(simplifyWorkspace,0);

})();
