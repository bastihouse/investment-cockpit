/* Investment Cockpit V7.1 — dated source data, explicit periods and coverage. */
(function () {
  'use strict';
  const periods = ['1M', '6M', 'YTD', '1J', '5J'];
  const palette = ['#8eb8ff', '#62d6b5', '#f2c778', '#df9bf3'];
  function cutoff(end, period) {
    const d = new Date(end + 'T12:00:00Z');
    if (period === 'YTD') return `${d.getUTCFullYear() - 1}-12-31`;
    if (period === '1M' || period === '6M') {
      const day = d.getUTCDate(); d.setUTCDate(1);
      d.setUTCMonth(d.getUTCMonth() - (period === '1M' ? 1 : 6));
      const last = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 0)).getUTCDate();
      d.setUTCDate(Math.min(day, last));
    } else d.setUTCFullYear(d.getUTCFullYear() - (period === '5J' ? 5 : 1));
    return d.toISOString().slice(0, 10);
  }
  function windowPoints(points, period, end) {
    const valid = points.filter(p => p && Number.isFinite(p.close) && p.close > 0 && /^\d{4}-\d{2}-\d{2}$/.test(p.date)).sort((a,b) => a.date.localeCompare(b.date));
    if (!valid.length) return [];
    end = end || valid.at(-1).date;
    const start = cutoff(end, period);
    const anchor = valid.filter(p => p.date <= start).at(-1);
    return valid.filter(p => p.date >= (anchor?.date || start) && p.date <= end);
  }
  function comparison(series, period) {
    if (!series.length || series.some(s => !s.data.length)) return [];
    const maps = series.map(s => new Map(s.data.filter(p => Number.isFinite(p.close) && p.close > 0).map(p => [p.date, p.close])));
    const common = [...maps[0].keys()].filter(d => maps.every(m => m.has(d))).sort();
    if (common.length < 2) return [];
    const dates = windowPoints(common.map(d => ({date: d, close: 1})), period).map(p => p.date);
    if (dates.length < 2) return [];
    return series.map((s,i) => ({ticker:s.ticker, currency:s.currency, data:dates.map(d => ({date:d, close:(maps[i].get(d)/maps[i].get(dates[0])-1)*100}))}));
  }
  function expire(snapshot, now=Date.now()) {
    if(!snapshot?.quotes)return snapshot;
    const expired=s=>!s||!Number.isFinite(Date.parse(s))||now-Date.parse(s)>7*86400000||Date.parse(s)>now+86400000;
    return {...snapshot, quotes:snapshot.quotes.map(q=>{
      const priceOld=expired(q.marketDate), fundamentalOld=expired(q.fundamentals?.fetchedAt);
      if(!priceOld&&!fundamentalOld)return q;
      const r=q.researchScore||{},parts={...(r.parts||{})},reasons={...(r.missingReasons||{})};
      Object.keys(parts).forEach(k=>{if(priceOld||k!=='risk'){parts[k]=null;reasons[k]='Veröffentlichte Eingaben sind älter als sieben Tage oder haben keinen gültigen Zeitstempel.';}});
      const max={valuation:30,growth:25,quality:20,revisions:15,risk:10};
      return {...q,status:priceOld&&q.price!=null?'stale':q.status,peTTM:null,forwardPE:null,
        fundamentals:{...(q.fundamentals||{}),status:'stale'},researchScore:{...r,parts,missingReasons:reasons,complete:false,total:null,
          partialPoints:Math.round(Object.values(parts).reduce((n,v)=>n+(v??0),0)*100)/100,
          coveragePoints:Object.entries(parts).reduce((n,[k,v])=>n+(v==null?0:max[k]),0)}};
    })};
  }
  const core = {cutoff, windowPoints, comparison, expire};
  if (typeof module !== 'undefined' && module.exports) module.exports = core;
  if (typeof document === 'undefined') return;
  const el = id => document.getElementById(id);
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const num = (v,d=2) => Number.isFinite(v) ? v.toLocaleString('de-DE',{maximumFractionDigits:d}) : '—';
  const date = s => s ? new Date(s).toLocaleString('de-AT',{timeZone:'Europe/Vienna'}) : '—';
  const previousMarketRender=lmRender;
  lmRender=function(){lmState.data=expire(lmState.data);previousMarketRender();};
  lmState.data=expire(lmState.data);
  const quotes = () => lmState.data?.quotes || [];
  const find = ticker => quotes().find(q => q.ticker === ticker);
  const cache = new Map();
  let activePeriod = 'YTD', comparePeriod = 'YTD', sequence = 0, compareSequence = 0;
  async function history(ticker) {
    if (!cache.has(ticker)) cache.set(ticker, fetch('./data/history/'+encodeURIComponent(ticker)+'.json',{cache:'no-store'}).then(r => {if(!r.ok)throw Error('HTTP '+r.status);return r.json();}).catch(e=>{cache.delete(ticker);throw e;}));
    return cache.get(ticker);
  }
  function chart(svg, series, percent) {
    const W=900,H=300,L=70,R=22,T=22,B=40;
    const values=series.flatMap(s=>s.data.map(p=>p.close));
    if (!values.length) {svg.innerHTML='';return;}
    let lo=Math.min(...values),hi=Math.max(...values);
    const pad=(hi-lo||Math.max(1,hi*.02))*.09;lo-=pad;hi+=pad;
    const dates=series[0].data.map(p=>p.date),t0=Date.parse(dates[0]),span=Date.parse(dates.at(-1))-t0||1;
    const x=d=>L+(Date.parse(d)-t0)/span*(W-L-R), y=v=>T+(hi-v)/(hi-lo)*(H-T-B);
    let html=Array.from({length:5},(_,i)=>{const v=lo+(hi-lo)*i/4;return `<line x1="${L}" x2="${W-R}" y1="${y(v)}" y2="${y(v)}" stroke="#344052"/><text x="${L-10}" y="${y(v)+4}" text-anchor="end" fill="#b1bfd2" font-size="12">${num(v,percent?1:2)}${percent?'%':''}</text>`;}).join('');
    if(percent&&lo<0&&hi>0)html+=`<line x1="${L}" x2="${W-R}" y1="${y(0)}" y2="${y(0)}" stroke="#93a2b7" stroke-dasharray="5 4"/>`;
    html+=series.map((s,i)=>`<path d="${s.data.map((p,k)=>(k?'L':'M')+x(p.date).toFixed(2)+' '+y(p.close).toFixed(2)).join(' ')}" fill="none" stroke="${palette[i]}" stroke-width="2.5"><title>${esc(s.ticker)}</title></path>`).join('');
    [dates[0],dates[Math.floor(dates.length/2)],dates.at(-1)].forEach((d,i)=>{html+=`<text x="${x(d)}" y="${H-12}" text-anchor="${i===0?'start':i===2?'end':'middle'}" fill="#b1bfd2" font-size="12">${esc(d)}</text>`;});
    svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.innerHTML=html;
  }
  const style=document.createElement('style');style.textContent=`
  .periods{display:flex;gap:6px;flex-wrap:wrap;margin:14px 0}.periods button[aria-pressed=true]{background:#36547c;border-color:#87adff;color:#fff}.r71-note{font-size:13px;color:#b9c6d8;line-height:1.6}.r71-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:14px 0}.r71-metric{background:#101a28;padding:14px;border-radius:12px;border:1px solid #304058}.r71-metric strong{display:block;font-size:23px;margin:7px 0}.r71-line{display:flex;align-items:center;justify-content:space-between;gap:15px;padding:10px 0;border-bottom:1px solid #2d3848}.r71-bar{display:flex;gap:2px;height:16px;width:100%;margin:9px 0}.r71-bar span{border:1px solid #50617a;background:#1a2637;border-radius:3px;position:relative;overflow:hidden}.r71-bar i{display:block;height:100%;background:#8eb8ff}.r71-bar span[data-missing=true]{background:repeating-linear-gradient(135deg,#263242,#263242 4px,#17202c 4px,#17202c 8px)}.r71-tickers{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:16px 0}.r71-table th{text-align:left;white-space:nowrap}.r71-table button{padding:5px 7px;min-width:55px}.r71-legend{display:flex;gap:18px;flex-wrap:wrap;margin:14px 0}.r71-legend span{border-left:4px solid;padding-left:8px}.r71-grid{display:grid;grid-template-columns:1.2fr 1fr;gap:16px}.r71-caption{font-size:12px;color:#aab8cc;margin-top:8px}@media(max-width:760px){.r71-tickers,.r71-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.r71-grid{grid-template-columns:1fr}}@media(max-width:440px){.r71-metrics{grid-template-columns:1fr}}`;
  document.head.appendChild(style);
  function periodControls(id, change) {
    const root=el(id);root.className='periods';
    root.innerHTML=periods.map(p=>`<button type="button" data-period="${p}" aria-pressed="${p==='YTD'}">${p}</button>`).join('');
    root.addEventListener('click',e=>{const b=e.target.closest('button[data-period]');if(!b)return;root.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));change(b.dataset.period);});
  }
  el('lmTicker').insertAdjacentHTML('afterend','<div id="r71Periods"></div>');
  periodControls('r71Periods',p=>{activePeriod=p;lmChart();});
  lmChart=async function(){
    const ticket=++sequence,ticker=lmState.selected;
    el('lmChartStatus').textContent='Lade veröffentlichte Kursreihe …';
    try {
      const j=await history(ticker);if(ticket!==sequence||ticker!==lmState.selected)return;
      const points=windowPoints(j.data||[],activePeriod);
      if(points.length<2)throw Error('Zu wenige veröffentlichte Handelstage im gewählten Zeitraum.');
      chart(el('lmChart'),[{ticker,data:points}],false);
      const ret=(points.at(-1).close/points[0].close-1)*100;
      el('lmChartStatus').textContent=`${activePeriod} · ${num(ret)}% Kursrendite · ${points[0].date} bis ${points.at(-1).date} · ${points.length} Handelstage · ${find(ticker)?.currency||j.currency||''}. ${j.source||'Yahoo Chart'}. Ohne Dividenden und Währungsumrechnung. ${activePeriod==='5J'&&points.length<1200?'Kürzere verfügbare Historie; keine vollen fünf Jahre.':''}`;
    }catch(e){if(ticket!==sequence)return;el('lmChart').innerHTML='';el('lmChartStatus').textContent='Kursverlauf nicht verfügbar: '+e.message;}
  };
  lmDetail=function(){
    const q=find(lmState.selected);if(!q){el('lmDetail').textContent='Noch keine Daten.';return;}
    const f=q.fundamentals||{}, r=q.researchScore||{};
    el('lmDetail').innerHTML=`<h3>${esc(q.name)} · ${esc(q.ticker)}</h3><div class="r71-metrics"><div class="r71-metric">Letzter Schlusskurs<strong>${num(q.price)}</strong>${esc(q.currency)} · ${esc(q.marketDate||'—')}</div><div class="r71-metric">P/E TTM<strong>${num(q.peTTM)}${q.peTTM!=null?'×':''}</strong>${q.peTTM==null?'Fehlt oder nicht sinnvoll (z. B. Verlust)':'Direkter Anbieterwert'}</div><div class="r71-metric">Forward-P/E<strong>${num(q.forwardPE)}${q.forwardPE!=null?'×':''}</strong>FY1/NTM nicht bestätigt</div></div><p class="r71-note">Kurse abgerufen: ${date(q.cachedAt)} · Kennzahlen abgerufen: ${date(f.fetchedAt)}<br>Jüngster Bericht laut Anbieter: ${esc(f.reportDate||'unbekannt')} · Kennzahlenstatus: ${esc(f.status||'missing')}<br>Branche: ${esc(f.industry||'—')} · Profil: ${esc(q.sectorLabel||'—')}</p><p class="r71-note">Forward-P/E ist die direkt gelieferte Anbieterkennzahl. Das zugrunde liegende Gewinnjahr und die Aktualität einzelner Analystenschätzungen sind nicht unabhängig bestätigt; daher keine Umdeutung zu FY1 oder NTM.</p><p>${r.complete?'Research-Score: <b>'+num(r.total)+' / 100</b>':'Teilbewertung: <b>'+num(r.partialPoints)+' / '+num(r.coveragePoints)+' belegbare Punkte</b>'} · <button type="button" id="r71GoScore">Berechnung ansehen</button></p><p class="r71-note">${Object.entries(q.attempts||{}).filter(([,a])=>a.status==='error').map(([k,a])=>esc(k+': '+a.error)).join('<br>')||'Keine protokollierten Abruffehler.'}<br>Quelle: <a target="_blank" rel="noopener noreferrer" href="${esc(f.sourceUrl||'https://finance.yahoo.com/')}">Yahoo Finance – Kennzahlen</a></p>`;
    el('r71GoScore').onclick=()=>{lsSelected=q.ticker;show('liveScore');lsRender();};
  };
  // Add comparison to existing navigation, preserving archive routes and deep links.
  NAV_GROUPS.analyse.push('compare'); NAV_FOR_VIEW.compare='analyse';
  const tab=document.createElement('button');tab.type='button';tab.dataset.v='compare';tab.textContent='Aktienvergleich';tab.hidden=true;tab.onclick=()=>show('compare');el('tabs').appendChild(tab);
  const compare=document.createElement('section');compare.id='compare';compare.className='view';
  compare.innerHTML=`<div class="panel"><h2>Aktien direkt vergleichen</h2><p class="r71-note">Bis zu vier Aktien · Kursentwicklung ab gemeinsamem Start = 0%. Alle Linien verwenden dieselben gemeinsamen Handelstage. Renditen in der jeweiligen Handelswährung, ohne Dividenden und ohne Währungsumrechnung.</p><div id="r71CompareTickers" class="r71-tickers"></div><div id="r71ComparePeriods"></div><p id="r71CompareStatus" role="status">Lade Aktienauswahl …</p><svg id="r71CompareChart" role="img" aria-label="Vergleich der prozentualen Kursentwicklung" viewBox="0 0 900 300" style="display:block;width:100%;min-height:220px"></svg><div id="r71CompareLegend" class="r71-legend"></div><div class="tbl"><table class="r71-table"><thead><tr><th>Aktie</th><th>Kurs</th><th>P/E TTM</th><th>Forward-P/E</th><th>Umsatzwachstum</th><th>Operative Marge</th><th>Score / Abdeckung</th></tr></thead><tbody id="r71CompareRows"></tbody></table></div></div>`;
  el('live').insertAdjacentElement('afterend',compare);
  periodControls('r71ComparePeriods',p=>{comparePeriod=p;renderComparison();});
  async function renderComparison(){
    const ticket=++compareSequence;
    const tickers=[...new Set([...el('r71CompareTickers').querySelectorAll('select')].map(s=>s.value).filter(Boolean))];
    el('r71CompareStatus').textContent='Lade und gleiche Handelstage ab …';
    el('r71CompareRows').innerHTML=tickers.map(t=>{const q=find(t),f=q?.fundamentals||{},r=q?.researchScore||{};if(!q)return '';return `<tr><td>${esc(q.name)}<div class="muted">${esc(t)} · ${esc(f.sector||q.sectorLabel)}</div></td><td>${num(q.price)} ${esc(q.currency)}</td><td>${num(q.peTTM)}</td><td>${num(q.forwardPE)}</td><td>${num(Number.isFinite(f.revenueGrowth)?f.revenueGrowth*100:null)}%</td><td>${num(Number.isFinite(f.operatingMargins)?f.operatingMargins*100:null)}%</td><td>${r.complete?num(r.total)+'/100':num(r.partialPoints)+'/'+num(r.coveragePoints)+' P.'}<div class="muted">${esc(q.sectorLabel)} · ${esc(f.status||'missing')}</div></td></tr>`;}).join('');
    if(tickers.length<2){el('r71CompareStatus').textContent='Wähle mindestens zwei unterschiedliche Aktien.';el('r71CompareChart').innerHTML='';el('r71CompareLegend').innerHTML='';return;}
    const loaded=await Promise.all(tickers.map(async t=>{try{return{ticker:t,currency:find(t)?.currency,data:(await history(t)).data||[]};}catch(e){return{ticker:t,data:[],error:e.message};}}));
    if(ticket!==compareSequence)return;
    const failed=loaded.filter(s=>!s.data.length);
    if(failed.length){el('r71CompareChart').innerHTML='';el('r71CompareLegend').innerHTML='';el('r71CompareStatus').textContent='Keine vergleichbaren Kursdaten für '+failed.map(s=>s.ticker).join(', ')+'. Passe die Auswahl an.';return;}
    const aligned=comparison(loaded,comparePeriod);
    if(!aligned.length){el('r71CompareChart').innerHTML='';el('r71CompareLegend').innerHTML='';el('r71CompareStatus').textContent='Keine ausreichenden gemeinsamen Handelstage.';return;}
    chart(el('r71CompareChart'),aligned,true);
    el('r71CompareLegend').innerHTML=aligned.map((s,i)=>`<span style="border-color:${palette[i]}">${esc(s.ticker)} (${esc(s.currency)}) <b>${num(s.data.at(-1).close)}%</b></span>`).join('');
    const a=aligned[0].data;
    el('r71CompareStatus').textContent=`${comparePeriod} · gemeinsamer Start ${a[0].date} · letzter gemeinsamer Tag ${a.at(-1).date} · ${a.length} gemeinsame Handelstage. ${comparePeriod==='5J'&&a.length<1150?'Die gemeinsame Historie ist kürzer als fünf Jahre.':''} Bewertungen nur innerhalb ähnlicher Branchen und Profile vergleichen.`;
  }
  const scoreRoot=el('liveScore');
  scoreRoot.innerHTML=`<div class="panel"><h2>Nachvollziehbarer Research-Score</h2><p class="r71-note">Fünf Kategorien, 100 mögliche Punkte. Fehlende Kategorien bleiben offen: Eine Teilbewertung wird niemals auf 100 hochgerechnet. Feste heuristische Schwellen sind keine faire Unternehmensbewertung und kein validiertes Handelssignal. Nur ähnliche Branchen und gleiche Profile vergleichen.</p><div id="r71ScoreKpis" class="r71-metrics"></div><div class="controls" style="grid-template-columns:2fr 1fr"><input id="r71ScoreSearch" type="search" placeholder="Unternehmen oder Ticker" aria-label="Score-Aktien durchsuchen"><select id="r71ScoreProfile" aria-label="Score-Profil"><option value="all">Alle Profile</option><option value="operating">Operativ</option><option value="bank">Banken</option><option value="insurance">Versicherer</option><option value="reit">REIT</option><option value="bdc">BDC</option><option value="holding">Holding</option><option value="royalty">Royalty</option></select></div><p id="r71ScoreStatus" role="status"></p><div class="tbl"><table class="r71-table"><thead><tr><th>Aktie / Profil</th><th>Score</th><th>Abdeckung</th><th>Bewertung /30</th><th>Wachstum /25</th><th>Qualität /20</th><th>Revision /15</th><th>Risiko /10</th><th>Details</th></tr></thead><tbody id="r71ScoreRows"></tbody></table></div></div><div id="r71ScoreDetail" class="panel"></div><div class="panel"><h3>Regeln und Grenzen · V7.1</h3><div class="tbl"><table><thead><tr><th>Kategorie</th><th>Messwert</th><th>0 Punkte</th><th>Maximale Punkte</th></tr></thead><tbody><tr><td>Bewertung · 30</td><td>Positives TTM-P/E</td><td>≥40×</td><td>≤10×</td></tr><tr><td>Wachstum · 25</td><td>Umsatzwachstum ggü. Vorjahr, Anbieterwert</td><td>≤−5%</td><td>≥25%</td></tr><tr><td>Qualität · 20</td><td>Operative Marge, Anbieterwert</td><td>≤0%</td><td>≥30%</td></tr><tr><td>Revisionen · 15</td><td>EPS-Konsens +1y heute / vor 30 Tagen, ≥3 Analysten</td><td>≤−10%</td><td>≥+10%</td></tr><tr><td>Risiko · 10</td><td>Annualisierte Volatilität, max. 252 tägliche Log-Renditen</td><td>≥60%</td><td>≤15%</td></tr></tbody></table></div><p class="r71-note">Dazwischen linear, an den Grenzen gedeckelt. Fundamentale Score-Punkte erfordern ein bekanntes jüngstes Berichtsdatum ≤210 Tage und einen erfolgreichen aktuellen Abruf. Kursdaten müssen innerhalb der letzten sieben Kalendertage liegen. Risiko benötigt mindestens 201 adjustierte Schlusskurse. Sonderprofile erhalten nur den belegbaren Risikobaustein; die übrigen Kategorien sind gesperrt. Forward-P/E fließt wegen des nicht unabhängig bestätigten Gewinnzeitraums nicht in den Score ein. Abrufzeit ist kein Nachweis für das Aktualisierungsdatum jeder Schätzung. Historische Archiv-Scores sind ein anderes Modell.</p></div>`;
  const labels={valuation:'Bewertung',growth:'Wachstum',quality:'Qualität',revisions:'Revisionen',risk:'Risiko'};
  const weights={valuation:30,growth:25,quality:20,revisions:15,risk:10};
  lsRender=function(){
    const all=quotes(),term=el('r71ScoreSearch').value.toLowerCase(),profile=el('r71ScoreProfile').value;
    const complete=all.filter(q=>q.researchScore?.complete).length;
    el('r71ScoreKpis').innerHTML=[['Vollständige Scores',complete+' / '+all.length],['Mit belegbaren Teilpunkten',all.filter(q=>q.researchScore?.coveragePoints>0&&!q.researchScore.complete).length],['P/E / Forward-P/E vorhanden',all.filter(q=>q.peTTM!=null).length+' / '+all.filter(q=>q.forwardPE!=null).length]].map(([l,v])=>`<div class="r71-metric">${l}<strong>${v}</strong></div>`).join('');
    const rows=all.filter(q=>(!term||`${q.name} ${q.ticker}`.toLowerCase().includes(term))&&(profile==='all'||q.sector===profile));
    el('r71ScoreStatus').textContent=`${rows.length} von ${all.length} Aktien · Stand ${date(lmState.data?.generatedAt)} · Keine Hochrechnung fehlender Daten.`;
    el('r71ScoreRows').innerHTML=rows.map(q=>{const r=q.researchScore||{};return `<tr><td><b>${esc(q.name)}</b><div class="muted">${esc(q.ticker)} · ${esc(q.sectorLabel||'—')}</div></td><td>${r.complete?'<b>'+num(r.total)+'/100</b>':'Teilbewertung'}</td><td>${num(r.partialPoints)} / ${num(r.coveragePoints)} P.<div class="r71-caption">${num(r.coveragePoints)}% Datenabdeckung</div></td>${Object.keys(weights).map(k=>`<td>${num(r.parts?.[k])}</td>`).join('')}<td><button type="button" data-score="${esc(q.ticker)}" aria-label="Score-Details ${esc(q.name)}">Details</button></td></tr>`;}).join('')||'<tr><td colspan="9">Keine Aktien für diese Auswahl.</td></tr>';
    el('r71ScoreRows').querySelectorAll('button[data-score]').forEach(b=>b.onclick=()=>{lsSelected=b.dataset.score;lsDetails();el('r71ScoreDetail').scrollIntoView({behavior:'smooth',block:'start'});});
    if(!rows.some(q=>q.ticker===lsSelected)&&rows.length)lsSelected=rows[0].ticker;
    lsDetails();syncCompare();
  };
  lsDetails=function(){
    const q=find(lsSelected);if(!q){el('r71ScoreDetail').textContent='Lade veröffentlichte Bewertungsdaten …';return;}
    const r=q.researchScore||{},f=q.fundamentals||{};
    el('r71ScoreDetail').innerHTML=`<h3>${esc(q.name)} · ${esc(q.ticker)}</h3><p>${r.complete?'<b>'+num(r.total)+' / 100 Punkte</b>':'<b>'+num(r.partialPoints)+' von '+num(r.coveragePoints)+' belegbaren Punkten</b>'} · Profil: ${esc(q.sectorLabel||'—')} · ${esc(f.industry||'Branche unbekannt')}</p><div class="r71-bar" role="img" aria-label="Score-Anteile; schraffiert sind fehlende Kategorien">${Object.entries(weights).map(([k,max])=>`<span style="width:${max}%" data-missing="${r.parts?.[k]==null}" title="${labels[k]}: ${num(r.parts?.[k])}/${max}"><i style="width:${(r.parts?.[k]??0)/max*100}%"></i></span>`).join('')}</div><p class="r71-caption">Blau: erreichte Punkte · Dunkel: nicht erreichte Punkte · Schraffiert: fehlende oder gesperrte Kategorie.</p>${Object.keys(weights).map(k=>`<div class="r71-line"><div><b>${labels[k]}</b><div class="r71-note">${esc(r.explanation?.[k]||r.missingReasons?.[k]||'Noch kein erweiterter Datenlauf vorhanden.')}</div></div><b style="white-space:nowrap">${num(r.parts?.[k])} / ${weights[k]}</b></div>`).join('')}<p class="r71-note">Quelle: ${esc(f.source||'Yahoo Finance Chart')} · Abruf ${date(f.fetchedAt||q.cachedAt)} · Jüngster Bericht ${esc(f.reportDate||'nicht bestätigt')} · Währung des Berichts ${esc(f.financialCurrency||'—')}. Keine Kauf-/Verkaufsempfehlung. Die Punkteschwellen sind transparente Modellannahmen.</p>`;
  };
  function syncCompare(){
    const all=quotes(),root=el('r71CompareTickers');if(!all.length)return;
    if(!root.querySelector('select')){
      root.innerHTML=[0,1,2,3].map(i=>`<label>Aktie ${i+1}<select id="r71Cmp${i}" aria-label="Vergleich Aktie ${i+1}"><option value="">${i<2?'Bitte wählen':'Keine weitere Aktie'}</option>${all.map(q=>`<option value="${esc(q.ticker)}">${esc(q.name)} (${esc(q.ticker)})</option>`).join('')}</select></label>`).join('');
      el('r71Cmp0').value='MSFT';el('r71Cmp1').value='NVDA';
      root.querySelectorAll('select').forEach(s=>s.onchange=renderComparison);
      renderComparison();
    }
  }
  el('r71ScoreSearch').oninput=lsRender;el('r71ScoreProfile').onchange=lsRender;
  const observer=new MutationObserver(()=>{if(compare.classList.contains('active')){syncCompare();renderComparison();}});observer.observe(compare,{attributes:true,attributeFilter:['class']});
  const initialView=location.hash.slice(1);
  if(NAV_FOR_VIEW[initialView])show(initialView,false);
  lsRender();
  if(lmState.data){lmRender();lmDetail();lmChart();}
})();
