// Owned local gallery only; no external browser traffic or automatic installation.
import fs from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const output=process.argv[2];if(!output)throw Error('Choose a fresh check directory');await fs.mkdir(output,{recursive:false});
const root=process.cwd(),types={'.html':'text/html; charset=utf-8','.png':'image/png','.svg':'image/svg+xml','.json':'application/json','.pdf':'application/pdf'};
const server=http.createServer(async(req,res)=>{try{const file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local.invalid').pathname));if(!file.startsWith(root+path.sep)||!(await fs.stat(file)).isFile())throw Error('outside selected tree');res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');createReadStream(file).pipe(res)}catch{res.writeHead(404);res.end()}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base='http://127.0.0.1:'+server.address().port;
const modulePath=process.env.FIGURE_PLAYWRIGHT_MODULE,{chromium}=modulePath?await import(pathToFileURL(modulePath)):await import('playwright');let browser;
try{
 const options={headless:true};if(process.env.FIGURE_BROWSER_EXECUTABLE)options.executablePath=process.env.FIGURE_BROWSER_EXECUTABLE;else if(process.platform==='win32')options.channel='msedge';
 browser=await chromium.launch(options);const context=await browser.newContext({viewport:{width:1440,height:1050}}),page=await context.newPage(),errors=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>{if(r.request().url().startsWith(base+'/'))return r.continue();external.push(r.request().url());return r.abort()});
 await page.goto(base+'/examples/clarity-v070/index.html');assert.equal(await page.locator('article').count(),15);
 for(const key of [...Array.from({length:11},(_,i)=>'CLR'+String(i+1).padStart(2,'0')),...Array.from({length:4},(_,i)=>'EXT'+String(i+1).padStart(2,'0'))]){
  const article=page.locator('#'+key);await article.scrollIntoViewIfNeeded();await article.locator('img').evaluate(e=>e.decode());
  for(const href of await article.locator('a').evaluateAll(as=>as.map(a=>a.href))){assert.ok(href.startsWith(base+'/'));const response=await context.request.get(href);assert.equal(response.status(),200);await response.dispose()}
 }
 await page.goto(base+'/examples/review-v070/index.html');await page.locator('#filter').selectOption('all');assert.equal(await page.locator('article').count(),458);await page.locator('#filter').selectOption('size');assert.equal(await page.locator('article').count(),140);
 await page.locator('#filter').selectOption('all');await page.locator('#search').fill('CLR03');await page.getByRole('button',{name:'检查 CLR03',exact:true}).click();assert.match(await page.locator('#viewport img').getAttribute('src'),/clarity-v070/);await page.locator('#before').click();assert.match(await page.locator('#viewport img').getAttribute('src'),/R11/);await page.locator('#close').click();
 await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 const result={status:'CLARITY_BROWSER_PASS',examples:15,exports:458,old_size_warnings:140,external_requests:0,checks:['all fifteen image loads and source/export links','source overview toggle','458-entry current browser and 140 retained flags','narrow layout'],visual_acceptance:false};await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve))}
