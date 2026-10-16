// Bounded offline UI and inert-SVG acceptance with an ephemeral owned HTTP server.
import fs from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
const output=process.argv[2];if(!output)throw Error('Supply fresh private test output');
const studioPath=process.argv[3]||'examples/studio/index.html';
await fs.mkdir(output,{recursive:false});
const root=process.cwd(),types={'.html':'text/html; charset=utf-8','.js':'text/javascript','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.css':'text/css'};
const server=http.createServer(async(req,res)=>{
  try{const name=decodeURIComponent(new URL(req.url,'http://local.invalid').pathname),file=path.resolve(root,'.'+name);
    if(!file.startsWith(root+path.sep))throw Error('outside root');
    const stat=await fs.stat(file);if(!stat.isFile())throw Error('not a file');
    res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');createReadStream(file).pipe(res);
  }catch{res.writeHead(404);res.end()}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base='http://127.0.0.1:'+server.address().port;
const modulePath=process.env.FIGURE_PLAYWRIGHT_MODULE;const {chromium}=modulePath?await import(pathToFileURL(modulePath)):await import('playwright');
const opts={headless:true};if(process.env.FIGURE_BROWSER_EXECUTABLE)opts.executablePath=process.env.FIGURE_BROWSER_EXECUTABLE;else if(process.platform==='win32')opts.channel='msedge';
let browser;const checks=[],external=[],errors=[];
try{
  // Run the established Studio interaction gates against the rebuilt full Studio first.
  await promisify(execFile)(process.execPath,['tests/check_studio.mjs',base+'/'+studioPath,path.join(output,'studio'),'examples/workbench-v030/inputs/ma.spec.json'],{timeout:180000});
  checks.push('established Studio search/import/hash mismatch/drag/export/narrow-layout tests pass');
  await promisify(execFile)(process.execPath,['tests/check_aesthetic_gallery.mjs',base+'/examples/aesthetic-v030/index.html',path.join(output,'aesthetic')],{timeout:180000});
  checks.push('established aesthetic gallery opinion and export interactions pass');
  browser=await chromium.launch(opts);const context=await browser.newContext({viewport:{width:1440,height:1050}}),page=await context.newPage();
  page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',route=>{const u=route.request().url();if(u.startsWith(base+'/')||u.startsWith('blob:')||u.startsWith('data:'))return route.continue();external.push(u);return route.abort()});
  await page.goto(base+'/'+studioPath);await page.locator('#publication-finish').click();
  await page.waitForFunction(()=>document.getElementById('preview-state').textContent==='PUBLICATION_PREVIEW_UNREVIEWED');
  assert.equal(await page.frameLocator('#before-view iframe').locator('svg').count(),1);
  assert.equal(await page.frameLocator('#after-view iframe').locator('svg').count(),1);checks.push('actual publication finisher and before/after preview execute');
  const refused=await page.evaluate(()=>['<script/>','<foreignObject/>','<image href="https://example.invalid/private.png"/>','<rect onload="alert(1)"/>','<animate/>','<svg xmlns="urn:unknown"/>','<style>@import "https://example.invalid/x";</style>','<rect style="fill:url(https://example.invalid/x)"/>','<rect style="width:expression(alert(1))"/>'].map(x=>{try{window.FigurePublication.safeParse('<svg xmlns="http://www.w3.org/2000/svg">'+x+'</svg>');return false}catch{return true}}));
  assert.ok(refused.every(Boolean));checks.push('nine active/external/foreign-namespace finisher inputs refused');
  await page.locator('#catalog-mode').selectOption('method');assert.equal(await page.locator('#catalog-count').innerText(),'25');
  await page.locator('#search').fill('GSEA');assert.ok(await page.locator('#catalog-list button').count()>=6);await page.locator('#catalog-list button').first().click();
  assert.match(await page.locator('#renderer-detail').textContent(),/ranked universe|gene-effect|set-size/);checks.push('25 dedicated method entries searchable with explicit input context');
  await page.locator('#search').fill('');
  for(let i=0;i<25;i++){
    await page.locator('#catalog-list button').nth(i).click();
    const key='PKG'+String(i+1).padStart(2,'0');
    await page.waitForFunction(k=>{const im=document.getElementById('method-example');return im?.src.includes(k+'/'+k+'.png')&&im.complete&&im.naturalWidth>1200},key);
    assert.equal(await page.locator('#preview-state').innerText(),'PACKAGE_EXAMPLE_SYNTHETIC');
    assert.equal(await page.locator('#renderer-detail a').count(),5);
    const spec=await page.locator('#renderer-detail a').filter({hasText:'SPEC'}).getAttribute('href');assert.ok(spec.endsWith(key+'.spec.json'));
  }
  checks.push('all 25 package selections show their actual image and exact source/spec/export links');
  await page.goto(base+'/examples/package-v040/index.html');assert.equal(await page.locator('article').count(),25);checks.push('all 25 new package examples accessible offline');
  await page.goto(base+'/examples/gallery/publication-v030/index.html');assert.equal(await page.locator('article').count(),400);
  await page.locator('#q').fill('ALT_K22_horizontal');assert.equal(await page.locator('article').count(),1);
  await page.locator('article img').waitFor();await page.waitForFunction(()=>document.querySelector('article img').naturalWidth>16000);checks.push('complete 400-entry atlas and extreme-wide final PNG load');
  await page.screenshot({path:path.join(output,'atlas-wide.png'),fullPage:true});
  await page.goto(base+'/examples/gallery/index.html#K42');await page.waitForFunction(()=>document.getElementById('outputimage').getAttribute('src').includes('publication-v030/K42'));
  assert.ok(await page.locator('#outputimage').getAttribute('src'));checks.push('primary gallery opens reviewed current preview with stable ID');
  await page.goto(base+'/examples/method-v030/index.html');assert.equal(await page.locator('article').count(),8);checks.push('eight dedicated GSEA/ORA examples accessible');
  await page.goto(base+'/examples/review-v050/index.html');
  assert.match(await page.locator('#count').innerText(),/\/ 438/);
  await page.locator('#filter').selectOption('all');assert.equal(await page.locator('article').count(),438);
  await page.locator('#search').fill('R03');await page.getByRole('button',{name:'检查 R03',exact:true}).click();
  assert.match(await page.locator('#viewport img').getAttribute('src'),/repairs-v050/);
  await page.locator('#before').click();assert.match(await page.locator('#viewport img').getAttribute('src'),/publication-v030/);
  await page.locator('#native').click();assert.match(await page.locator('#viewport').getAttribute('class'),/native/);
  await page.locator('#close').click();await page.locator('#search').fill('');await page.locator('#filter').selectOption('size');assert.equal(await page.locator('article').count(),139);
  await page.locator('#filter').selectOption('composition');assert.equal(await page.locator('article').count(),126);
  await page.getByRole('button',{name:'检查 K01',exact:true}).click();await page.locator('#parts').click();assert.ok(await page.locator('.component').count()>=2);
  await page.locator('#close').click();await page.setViewportSize({width:390,height:844});await page.locator('#filter').selectOption('preferred');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
  await page.screenshot({path:path.join(output,'review-narrow.png'),fullPage:false});
  checks.push('438-entry review browser: search, 139 size flags, 126 component readings, original/revised toggle, native zoom and narrow layout');
  await page.setViewportSize({width:850,height:1100});
  for(let i=1;i<=5;i++){
    const key='VIS'+String(i).padStart(2,'0');
    await page.setContent('<!doctype html><meta charset="utf-8"><style>body{margin:24px;background:#edf1f3;font:14px system-ui}img{display:block;width:178mm;height:auto;background:white}</style><p>'+key+' · nominal CSS 178 mm screen proof (not calibrated paper)</p><img src="'+base+'/examples/design-v050/'+key+'/'+key+'.png" alt="'+key+'">');
    await page.waitForFunction(()=>document.querySelector('img').complete&&document.querySelector('img').naturalWidth>1000);
    await page.screenshot({path:path.join(output,key+'-178mm-screen.png'),fullPage:true});
  }
  checks.push('five individual nominal CSS 178mm screenshots saved for separate human inspection; automation is not visual acceptance');
  await page.goto(base+'/examples/review-v060/index.html');await page.locator('#filter').selectOption('all');
  assert.equal(await page.locator('article').count(),443);assert.equal(await page.locator('article .reading-link').count(),443);
  await page.locator('#search').fill('P10');await page.getByRole('button',{name:'检查 P10',exact:true}).click();
  assert.match(await page.locator('#viewport img').getAttribute('src'),/repairs-v060/);
  const reading=await page.locator('#detail .reading-link').getAttribute('href');assert.match(reading,/reading-volume-\d\d\.pdf#page=\d+/);
  const response=await context.request.get(base+'/'+new URL(reading,base+'/examples/review-v060/index.html').pathname.replace(/^\//,''));assert.equal(response.status(),200);await response.dispose();
  await page.locator('#before').click();assert.match(await page.locator('#viewport img').getAttribute('src'),/publication-v030/);await page.locator('#close').click();
  await page.locator('#search').fill('');await page.locator('#filter').selectOption('composition');assert.equal(await page.locator('article').count(),126);
  await page.getByRole('button',{name:'检查 K09',exact:true}).click();await page.locator('#parts').click();assert.ok(await page.locator('.component img[src*="repairs-v060"]').count()>=1);await page.locator('#close').click();
  await page.setViewportSize({width:390,height:844});await page.locator('#filter').selectOption('preferred');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
  checks.push('443-entry current browser, bound PDF reading links, revised raster scatter, component version and narrow layout verified');
  await page.setViewportSize({width:850,height:1100});
  for(let i=1;i<=5;i++){
    const key='REF'+String(i).padStart(2,'0');
    await page.setContent('<!doctype html><meta charset="utf-8"><style>body{margin:24px;background:#edf1f3;font:14px system-ui}img{display:block;width:178mm;height:auto;background:white}</style><p>'+key+' · nominal CSS 178 mm screen proof (not calibrated paper)</p><img src="'+base+'/examples/refined-v060/'+key+'/'+key+'.png" alt="'+key+'">');
    await page.waitForFunction(()=>document.querySelector('img').complete&&document.querySelector('img').naturalWidth>1000);
    await page.screenshot({path:path.join(output,key+'-178mm-screen.png'),fullPage:true});
  }
  checks.push('five community-informed nominal CSS 178mm screenshots prepared, requiring separate actual inspection');
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const result={status:'PUBLICATION_BROWSER_PASS',checks,external_requests:0,scientific_acceptance:false};
  await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve))}
