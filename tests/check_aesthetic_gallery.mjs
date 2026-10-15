// Actual isolated browser check of candidate previews and local feedback.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const [url,output]=process.argv.slice(2);
if(!url||!output)throw Error('Supply selected candidate gallery URL and a new result directory');
await fs.mkdir(output,{recursive:false});
const modulePath=process.env.FIGURE_PLAYWRIGHT_MODULE;
const {chromium}=modulePath?await import(pathToFileURL(modulePath)):await import('playwright');
const options={headless:true};
if(process.env.FIGURE_BROWSER_EXECUTABLE)options.executablePath=process.env.FIGURE_BROWSER_EXECUTABLE;
else if(process.platform==='win32')options.channel='msedge';
const browser=await chromium.launch(options);
const context=await browser.newContext({viewport:{width:1440,height:1050},acceptDownloads:true});
const page=await context.newPage(),errors=[],external=[];
page.on('pageerror',e=>errors.push(e.message));
await page.route('**/*',route=>{
  const value=route.request().url();
  if(value.startsWith(new URL(url).origin+'/')||value.startsWith('data:')||value.startsWith('blob:'))return route.continue();
  external.push(value);return route.abort();
});
const checks=[];
try{
  await page.goto(url,{waitUntil:'networkidle'});assert.equal(await page.locator('article').count(),12);
  for(const article of await page.locator('article').all()){
    await article.scrollIntoViewIfNeeded();
    await article.locator('img').evaluate(img=>img.decode());
    assert.ok(await article.locator('img').evaluate(img=>img.naturalWidth>500));
  }
  checks.push('All 12 actual PNG previews decode successfully');
  await page.locator('#search').fill('基因组');assert.equal(await page.locator('article:visible').count(),1);
  assert.equal(await page.locator('article:visible').getAttribute('id'),'B06');
  await page.locator('#search').fill('');
  const value='SYNTHETIC UI TEST: refine spacing';
  await page.locator('textarea[data-id=B04]').fill(value);await page.reload({waitUntil:'networkidle'});
  assert.equal(await page.locator('textarea[data-id=B04]').inputValue(),value);
  const pending=page.waitForEvent('download');await page.locator('#export').click();const download=await pending;
  await download.saveAs(path.join(output,'feedback-test.json'));
  const exported=JSON.parse(await fs.readFile(path.join(output,'feedback-test.json'),'utf8'));
  assert.equal(exported.notes.B04,value);checks.push('Search, scoped local feedback persistence and explicit export');
  await page.locator('header').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(output,'aesthetic-gallery-desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.screenshot({path:path.join(output,'aesthetic-gallery-narrow.png'),fullPage:true});
  checks.push('Desktop and narrow gallery layouts have no horizontal overflow');
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const receipt={status:'AESTHETIC_GALLERY_BROWSER_PASS',checks,page_errors:errors,external_requests:external,
    scientific_acceptance:false,visual_opinions_are_local:true};
  await fs.writeFile(path.join(output,'browser-validation.json'),JSON.stringify(receipt,null,2)+'\n');
  process.stdout.write(JSON.stringify(receipt)+'\n');
}finally{await context.close();await browser.close();}
