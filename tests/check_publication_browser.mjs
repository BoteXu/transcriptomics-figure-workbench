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
  await promisify(execFile)(process.execPath,['tests/check_studio.mjs',base+'/examples/studio/index.html',path.join(output,'studio'),'examples/workbench-v030/inputs/ma.spec.json'],{timeout:180000});
  checks.push('established Studio search/import/hash mismatch/drag/export/narrow-layout tests pass');
  browser=await chromium.launch(opts);const context=await browser.newContext({viewport:{width:1440,height:1050}}),page=await context.newPage();
  page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',route=>{const u=route.request().url();if(u.startsWith(base+'/')||u.startsWith('blob:')||u.startsWith('data:'))return route.continue();external.push(u);return route.abort()});
  await page.goto(base+'/examples/studio/index.html');await page.locator('#publication-finish').click();
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
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const result={status:'PUBLICATION_BROWSER_PASS',checks,external_requests:0,scientific_acceptance:false};
  await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve))}
