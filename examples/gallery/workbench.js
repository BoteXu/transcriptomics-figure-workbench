// The primary list contains one entry per drawing grammar, not every source ID.
const byId = new Map(items.map(x => [x.id, x]));
const methodById = new Map(methods.map(x => [x.id, x]));
const methodByExample = new Map(methods.flatMap(m => m.members.map(id => [id, m])));
const key = 'figure-workbench-public-v0.1-notes';
const $ = s => document.querySelector(s);
const labels = ['配色', '字体', '布局与留白', '点线与图例', '其他要求'];
let notes = {}, selected = null, backupUrl;
try { notes = JSON.parse(localStorage.getItem(key) || '{}'); } catch {}

function resolveToken(token) {
  if (byId.has(token)) return byId.get(token);
  if (methodById.has(token)) return byId.get(methodById.get(token).default);
  const group = groups.find(g => g.id === (groupAliases[token] || token));
  return group && byId.get(group.default);
}
function collect() {
  if (!selected) return;
  const n = { image_sha256: selected.png_sha256 };
  labels.forEach((k, i) => n[k] = $('#n' + i).value);
  notes[selected.id] = n;
}
function persist() {
  try { localStorage.setItem(key, JSON.stringify(notes)); $('#status').textContent = '已保存在本机浏览器；导出 JSON 可以备份。'; }
  catch { $('#status').textContent = '当前浏览器无法保存；请导出意见备份。'; }
}
function renderList() {
  const q = $('#search').value.toLowerCase(), type = $('#filter').value;
  const visible = methods.filter(m => (type === 'all' || type === m.role) &&
    JSON.stringify([m.id, m.title, m.grammar, m.contracts]).toLowerCase().includes(q));
  $('nav').replaceChildren();
  visible.forEach(m => {
    const b = document.createElement('button');
    b.textContent = m.title;
    b.className = m.members.includes(selected?.id) ? 'active' : '';
    b.onclick = () => { collect(); show(byId.get(m.default)); };
    $('nav').append(b);
  });
  $('#count').textContent = visible.length + ' 个去重入口；模式与来源在入口内查看';
}
function addLink(label, url) {
  const a = document.createElement('a'); a.textContent = label; a.href = url;
  if (!url.startsWith('#')) a.target = '_blank';
  $('#links').append(a);
}
function show(x) {
  selected = x;
  const m = methodByExample.get(x.id);
  $('#title').textContent = m.title;
  $('#shape').textContent = m.id + ' · 当前示意 ' + x.id + ' · 数据形状：' + x.input_shape;
  $('#mode').replaceChildren();
  m.modes.forEach(p => {
    const o = document.createElement('option'); o.value = p.example; o.textContent = p.label;
    o.selected = p.example === x.id; $('#mode').append(o);
  });
  if (!m.modes.some(p => p.example === x.id)) {
    const o = document.createElement('option'); o.value = x.id; o.textContent = '已保存来源 ' + x.id;
    o.selected = true; $('#mode').append(o);
  }
  $('#variants').replaceChildren();
  m.members.forEach(id => {
    const o = document.createElement('option'); o.value = id; o.textContent = id + ' · ' + byId.get(id).title;
    o.selected = id === x.id; $('#variants').append(o);
  });
  $('#source-options').classList.toggle('hidden', !$('#archive').checked);
  $('#curation').replaceChildren();
  $('#curation').textContent = '同一画法只设一个主入口。各模式保留自己的单位、尺度、区间和数据契约；当前图片是已保存的示例。';
  if (x.id !== m.default) {
    const a = document.createElement('a'); a.href = '#' + m.id; a.textContent = ' 返回主示意'; $('#curation').append(a);
  }
  $('#links').replaceChildren();
  for (const [field, label] of [['pdf','PDF'],['svg','SVG'],['png','PNG'],['tsv','示例数据'],['style','绘图参数'],['meta','来源与设置']])
    if (x[field]) addLink(label, x[field]);
  (x.component_links || []).forEach(c => addLink('单独 ' + c.label, c.url));
  (x.component_tables || []).forEach((url, i) => addLink('Panel ' + String.fromCharCode(65+i) + ' 数据', url));
  if (['T08','T15','T24','T31','T34','T36','N01','N04','N05','N06','N07','N08','N09','N10','N11'].includes(x.id))
    addLink('同数据：更换色卡与字体', 'theme_alternative/' + x.id + '/' + x.id + '.pdf');
  $('#reference').classList.toggle('hidden', !x.reference);
  $('.images').classList.toggle('solo', !x.reference);
  if (x.reference) { $('#refimage').src = x.reference; $('#refimage').alt = x.id + ' 用户参考'; }
  $('#outputimage').src = x.png; $('#outputimage').alt = x.id + ' ' + x.title;
  $('#outputcaption').textContent = x.role === 'protein' ? '真实公共坐标 · 原生渲染示例' : x.role === 'palette' ? '准确色值 · 纯色卡' : '已保存的绘图示意 · 合成数据；课题图按统一主题重绘';
  $('#facts').replaceChildren();
  for (const [field, label] of [['data_required','需要的数据'],['expression','能表达什么'],['how_to_draw','怎么画'],['aesthetic_controls','可以调整'],['limitations','使用边界']]) {
    const dt = document.createElement('dt'), dd = document.createElement('dd');
    dt.textContent = label; dd.textContent = x[field]; $('#facts').append(dt, dd);
  }
  $('#swatches').replaceChildren();
  (x.colors || []).forEach(c => { const d = document.createElement('div'); d.style.background = c; d.textContent = c; $('#swatches').append(d); });
  $('#notegrid').replaceChildren();
  labels.forEach((k, i) => { const l = document.createElement('label'), t = document.createElement('textarea');
    l.textContent = k; t.id = 'n'+i; t.value = notes[x.id]?.[k] || ''; l.append(t); $('#notegrid').append(l); });
  $('#status').textContent = notes[x.id]?.image_sha256 && notes[x.id].image_sha256 !== x.png_sha256 ? '此条意见关联旧版本图片，请重新核对。' : '';
  renderList(); history.replaceState(null, '', '#' + x.id);
}
$('#mode').onchange = () => { collect(); show(byId.get($('#mode').value)); };
$('#variants').onchange = () => { collect(); show(byId.get($('#variants').value)); };
window.addEventListener('hashchange', () => { const x = resolveToken(location.hash.slice(1)); if (x) { collect(); show(x); } });
$('#archive').onchange = () => $('#source-options').classList.toggle('hidden', !$('#archive').checked);
$('#search').oninput = renderList; $('#filter').onchange = renderList;
$('#save').onclick = () => { collect(); persist(); };
$('#export').onclick = () => {
  collect(); persist(); $('#backupcontent').value = JSON.stringify({ version:1, notes }, null, 2);
  if (backupUrl) URL.revokeObjectURL(backupUrl);
  backupUrl = URL.createObjectURL(new Blob([$('#backupcontent').value], { type:'application/json' }));
  $('#backupdownload').href = backupUrl; $('#backupstatus').textContent = '按原编号和图片哈希保留意见；下载或复制完整 JSON 备份。'; $('#backup').showModal();
};
$('#closebackup').onclick = () => $('#backup').close();
$('#copybackup').onclick = async () => {
  try { await navigator.clipboard.writeText($('#backupcontent').value); $('#backupstatus').textContent = '完整 JSON 已复制。'; }
  catch { $('#backupcontent').focus(); $('#backupcontent').select(); $('#backupstatus').textContent = '内容已选中，可按 Ctrl+C 复制。'; }
};
$('#import').onclick = () => $('#importfile').click();
$('#importfile').onchange = async e => {
  try {
    if (e.target.files[0].size > 2000000) throw Error('文件过大');
    const obj = JSON.parse(await e.target.files[0].text());
    if (obj.version !== 1 || !obj.notes || Array.isArray(obj.notes)) throw Error('格式不符');
    const clean = {};
    for (const [id, n] of Object.entries(obj.notes)) {
      if (!byId.has(id) || !n || typeof n !== 'object') throw Error('编号不符');
      if (typeof n.image_sha256 !== 'string' || n.image_sha256.length !== 64) throw Error('缺少图片版本');
      clean[id] = { image_sha256:n.image_sha256 };
      for (const k of labels) { if (typeof n[k] !== 'string' || n[k].length > 10000) throw Error('意见字段不符'); clean[id][k] = n[k]; }
    }
    notes = { ...notes, ...clean }; persist(); show(selected); $('#status').textContent = '导入成功；图片版本差异会在各项提示。';
  } catch (err) { $('#status').textContent = '未导入：' + err.message; }
};
for (const img of [$('#refimage'),$('#outputimage')]) img.onclick = () => {
  $('#large img').src = img.src; $('#large img').style.width = '100%'; $('#zoom').value = '100'; $('#large').showModal();
};
$('#zoom').onchange = () => $('#large img').style.width = $('#zoom').value + '%';
$('#close').onclick = () => $('#large').close();
show(resolveToken(location.hash.slice(1)) || byId.get('K38'));
