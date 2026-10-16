/* Real browser interaction checks on public frozen examples; no data upload. */
import fs from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const output=process.argv[2];if(!output)throw Error('Choose a fresh check directory');await fs.mkdir(output,{recursive:false});
const root=process.cwd(),types={'.html':'text/html; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.json':'application/json','.pdf':'application/pdf'};
const server=http.createServer(async(req,res)=>{try{const file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local.invalid').pathname));if(!file.startsWith(root+path.sep)||!(await fs.stat(file)).isFile())throw Error('outside selected tree');res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');createReadStream(file).pipe(res)}catch{res.writeHead(404);res.end()}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base='http://127.0.0.1:'+server.address().port;
const modulePath=process.env.FIGURE_PLAYWRIGHT_MODULE,{chromium}=modulePath?await import(pathToFileURL(modulePath)):await import('playwright');let browser;
try{
 const options={headless:true};if(process.env.FIGURE_BROWSER_EXECUTABLE)options.executablePath=process.env.FIGURE_BROWSER_EXECUTABLE;else if(process.platform==='win32')options.channel='msedge';
 browser=await chromium.launch(options);const context=await browser.newContext({viewport:{width:1440,height:1050}}),page=await context.newPage(),errors=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>{if(r.request().url().startsWith(base+'/'))return r.continue();external.push(r.request().url());return r.abort()});
 await page.goto(base+'/examples/forms-v080/index.html');await page.locator('#filter').selectOption('all');assert.equal(await page.locator('article').count(),90);
 await page.screenshot({path:path.join(output,'gallery-desktop.png')});
 await page.locator('#search').fill('heatmap');assert.equal(await page.locator('article').count(),1);const heat=page.locator('[data-form="heatmap"]');
 assert.equal(await heat.locator('select').first().locator('option').count(),9);assert.equal(await heat.locator('details').evaluate(e=>e.open),false);
 const before=await heat.locator('img').getAttribute('src');await heat.locator('select').first().selectOption({label:'转置'});assert.notEqual(await heat.locator('img').getAttribute('src'),before);await heat.locator('img').evaluate(e=>e.decode());
 await heat.locator('button').first().click();await page.locator('#before').click();assert.match(await page.locator('#imageview img').getAttribute('src'),/publication-v030/);await page.locator('#native').click();assert.equal(await page.locator('#imageview').evaluate(e=>e.classList.contains('native')),true);await page.locator('#close').click();
 await page.goto(base+'/examples/forms-v080/index.html#PKG22');assert.match(await page.locator('#title').innerText(),/PKG22/);await page.locator('#imageview img').evaluate(e=>e.decode());await page.locator('#close').click();
 await page.goto(base+'/skills/transcriptomics-figure-workbench/assets/forms-gallery/index.html');await page.locator('#filter').selectOption('all');assert.equal(await page.locator('article').count(),90);
 for(const card of await page.locator('article').all()){await card.scrollIntoViewIfNeeded();await card.locator('img').evaluate(e=>e.decode());}
 await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(output,'gallery-narrow.png')});
 await page.goto(base+'/skills/transcriptomics-figure-workbench/assets/figure-studio.html');
 const svg=await fs.readFile(path.join(root,'examples/forms-v080/PKG01/PKG01.svg'),'utf8');
 await page.locator('#svg-file').setInputFiles({name:'selected.svg',mimeType:'image/svg+xml',buffer:Buffer.from(svg)});await page.locator('#form-polish').click();
 assert.equal(await page.locator('#preview-state').innerText(),'SAME_FORM_PREVIEW_UNREVIEWED');
 const texts=await page.frameLocator('#preview-content iframe').locator('body').textContent();assert.match(texts,/NES/);assert.match(texts,/FDR/);assert.match(texts,/leading edge/);assert.match(texts,/FROZEN RESULT/);
 assert.equal(await page.evaluate(()=>{try{FigureStudioCore.safeSVG('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>');return false}catch{return true}}),true);
 await page.setViewportSize({width:1440,height:1050});await page.locator('[data-tab="board"]').click();
 const fixtureFiles=['P09','PKG14','REF01'].map(k=>path.join(root,'examples/forms-v080',k,k+'.svg'));await page.locator('#board-svg-files').setInputFiles(fixtureFiles);await page.waitForFunction(()=>document.querySelectorAll('.board-panel').length===3&&!document.getElementById('board-svg-files').value);
 await page.locator('#board-columns').selectOption('custom');await page.locator('#board-custom-columns').fill('5');await page.locator('#board-custom-columns').dispatchEvent('change');
 await page.locator('#board-weights').fill('2,1,1,1,1');await page.locator('#board-weights').dispatchEvent('change');
 await page.getByRole('spinbutton',{name:'Panel_1 跨列',exact:true}).fill('2');await page.getByRole('spinbutton',{name:'Panel_1 跨列',exact:true}).dispatchEvent('change');
 await page.getByRole('spinbutton',{name:'Panel_1 跨行',exact:true}).fill('2');await page.getByRole('spinbutton',{name:'Panel_1 跨行',exact:true}).dispatchEvent('change');
 const request=await page.evaluate(()=>FigureStudioCore.boardRequest());assert.equal(request.columns,5);assert.equal(request.panels[0].column_span,2);assert.equal(request.panels[0].row_span,2);assert.equal(request.source_files_selected,true);assert.ok(request.panels.every(p=>/^[a-f0-9]{64}$/.test(p.sha256)));assert.deepEqual(request.column_weights,[2,1,1,1,1]);
 await page.screenshot({path:path.join(output,'flexible-board.png')});
 await page.goto(base+'/examples/layout-v080/index.html');assert.equal(await page.locator('article').count(),3);for(const img of await page.locator('article img').all())await img.evaluate(e=>e.decode());
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 await page.screenshot({path:path.join(output,'studio.png')});
 const result={status:'FORMS_BROWSER_PASS',base_entries:90,examples:458,external_requests:0,checks:['one heatmap card and nine nested extensions','old/current toggle and native zoom','legacy ID deep link','all portable default previews decode','narrow gallery','same-form preview retains GSEA labels','active SVG rejected','five custom columns with unequal weights and spans','local SVG hashes bound to request','all three actual flexible SVG pages load'],visual_acceptance:false};await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve))}
