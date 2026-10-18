/* Offline canonical entries. Source IDs and exact downloadable assets survive. */
const rows=DATA.rows,chapters=DATA.chapters;
let NAV=DATA.default_mode==='analysis'?DATA.navigation:DATA.forms;
const stageNames={qc:'设计与质控',network:'建网与模块',interpretation:'关联与解释',function:'功能与支持基因',validation:'验证与稳定性',extension:'拓展分析',chapter:'章节主图',layout:'配套组图与布局'};
const byId=new Map(rows.map(r=>[r.id,r]));
const $=x=>document.getElementById(x);const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n};
let filtered=[],current=0,selectedMember='';
$('browseMode').value=DATA.default_mode||'forms';
$('scope').textContent=DATA.scope+' · '+DATA.forms.navigation_entries+' 个可复用画法族；每个画法内切换分析示例。';
for(const c of [{id:'',label:'全部分析章节'},...chapters]){const o=el('option',c.label+(c.id?' · '+c.id:''));o.value=c.id;$('chapter').append(o)}
function memberLabel(r,e){return (r.variant?'布局／替代 · ':'分析示例 · ')+r.title+' ['+r.id+']'}
function eligible(e){const chapter=$('chapter').value,query=$('search').value.trim().toLowerCase();return e.member_ids.map(id=>byId.get(id)).filter(r=>(!chapter||r.chapters.includes(chapter))&&($('variants').checked||!r.variant)&&(!query||JSON.stringify([r.id,r.title,r.chapters,r.keywords,e.title]).toLowerCase().includes(query)))}
function draw(preferred){
 const e=filtered[current];$('empty').hidden=!!e;$('content').hidden=!e;$('counter').textContent=e?`${current+1} / ${filtered.length}`:'';
 $('prev').disabled=current<=0;$('next').disabled=current>=filtered.length-1;
 for(const b of $('menu').querySelectorAll('button'))b.classList.toggle('active',Number(b.dataset.index)===current);
 if(!e)return;
 let available=eligible(e);
 const r=available.find(r=>r.id===preferred)||available.find(r=>r.id===selectedMember)||available.find(r=>r.id===e.default_id)||available[0];selectedMember=r.id;
 $('edition').replaceChildren();for(const v of available){const o=el('option',memberLabel(v,e));o.value=v.id;$('edition').append(o)}$('edition').value=r.id;
 $('editionLine').hidden=available.length<=1;$('title').textContent=r.title;
 $('meta').textContent=(stageNames[r.stage]||stageNames.chapter)+' · '+r.chapters.join(' / ')+' · 当前画法内 '+available.length+' 个分析示例／布局。各示例的输入和统计含义分别保留。';
 $('art').src=r.assets.png;$('art').alt=r.title;$('art').classList.remove('native');$('definition').textContent=r.definition;
 $('compare').hidden=!r.before_png;$('compare').textContent='查看前版';$('compare').dataset.before='false';
 $('links').replaceChildren();for(const k of ['png','svg','pdf','tsv','spec']){if(!r.assets[k])continue;const a=el('a',k.toUpperCase());a.href=r.assets[k];a.target='_blank';a.rel='noopener';$('links').append(a)}
 $('parameters').textContent=JSON.stringify({canonical_entry:e.id,selected_id:r.id,all_extensions:e.member_ids,view_ids:r.view_ids||[r.id],renderer:r.renderer,parameters:r.parameters,input_requirements:r.requirements,review:r.review},null,2);
 history.replaceState(null,'','#'+encodeURIComponent(r.id));
}
function filter(preferred=filtered[current]?.id,member=selectedMember){
 const query=$('search').value.trim().toLowerCase(),chapter=$('chapter').value;
 filtered=NAV.entries.filter(e=>eligible(e).length);
 current=Math.max(0,filtered.findIndex(e=>e.id===preferred));$('menu').replaceChildren();let last='';
 for(const[e,i]of filtered.map((e,i)=>[e,i])){
  const c=chapter||e.chapters[0];const heading=$('browseMode').value==='forms'?'可复用画法':(chapter?'':(chapters.find(x=>x.id===c)?.label||c)+' · ')+(stageNames[e.stage]||stageNames.chapter);
  if(heading!==last){$('menu').append(el('h3',heading));last=heading}
  const n=eligible(e).length;const label=$('browseMode').value==='analysis'?(eligible(e).find(r=>r.id===e.default_id)||eligible(e)[0]).title:e.title;
  const b=el('button',label+(n>1?'  · '+n+'例':''));b.dataset.index=i;b.dataset.entry=e.id;b.onclick=()=>{current=i;selectedMember='';draw()};$('menu').append(b);
 }
 const examples=filtered.reduce((n,e)=>n+eligible(e).length,0);$('summary').textContent=filtered.length+($('browseMode').value==='forms'?' 个画法族，':' 个分析问题，')+examples+' 个来源示例；示例和布局在图内切换。';draw(member);
}
function sourceFromHash(){const raw=decodeURIComponent(location.hash.slice(1));return byId.has(raw)?raw:(/^\d+$/.test(raw)&&Number(raw)>0&&Number(raw)<=rows.length?rows[Number(raw)-1].id:raw)}
const initial=sourceFromHash();const initialRow=byId.get(initial);const initialEntry=NAV.aliases[initial]||initial;
$('chapter').value=DATA.initial_chapter!==null&&DATA.initial_chapter!==undefined?DATA.initial_chapter:(initialRow?initialRow.chapters[0]:(chapters.some(c=>c.id==='bulk.wgcna')?'bulk.wgcna':''));
if(initialRow?.variant)$('variants').checked=true;
filter(initialEntry,initial);
$('search').oninput=()=>{if($('search').value)$('chapter').value='';filter()};$('chapter').onchange=()=>{$('search').value='';selectedMember='';filter()};$('variants').onchange=()=>filter();
$('edition').onchange=()=>draw($('edition').value);$('prev').onclick=()=>{if(current>0){current--;selectedMember='';draw()}};$('next').onclick=()=>{if(current<filtered.length-1){current++;selectedMember='';draw()}};
$('compare').onclick=()=>{const r=byId.get(selectedMember),before=$('compare').dataset.before!=='true';$('art').src=before?r.before_png:r.assets.png;$('compare').dataset.before=String(before);$('compare').textContent=before?'返回本版':'查看前版'};
$('browseMode').onchange=()=>{NAV=$('browseMode').value==='forms'?DATA.forms:DATA.navigation;filter(NAV.aliases[selectedMember],selectedMember)};
window.addEventListener('hashchange',()=>{const id=sourceFromHash(),r=byId.get(id);if(!r)return;$('search').value='';if($('chapter').value&&!r.chapters.includes($('chapter').value))$('chapter').value=r.chapters[0];if(r.variant)$('variants').checked=true;filter(NAV.aliases[id],id)});
$('zoom').onclick=()=>$('art').classList.toggle('native');document.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName))return;if(e.key==='ArrowRight')$('next').click();if(e.key==='ArrowLeft')$('prev').click()});
