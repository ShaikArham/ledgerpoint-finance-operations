from playwright.sync_api import sync_playwright
from pathlib import Path
import json,hashlib
import os
BASE=os.environ.get("LEDGERPOINT_QA_URL","http://127.0.0.1:8001").rstrip("/")
ROOT=Path(__file__).resolve().parents[1]
results=[];errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(BASE+'/')
 page.locator('#intro-play').click()
 page.wait_for_function('document.querySelector("video").currentTime > 0.2')
 results.append({'playback':page.locator('video').evaluate('(v)=>({duration:v.duration,width:v.videoWidth,audio:v.webkitAudioDecodedByteCount,captions:v.textTracks.length,cues:v.textTracks[0].cues.length})')})
 page.locator('video').evaluate('(v)=>v.pause()');assert page.locator('video').evaluate('(v)=>v.paused')
 page.wait_for_function('document.querySelector("video").buffered.length && document.querySelector("video").buffered.end(0)>89');page.locator('video').evaluate('(v)=>{v.currentTime=89;return v.play()}');page.wait_for_function('document.querySelector("video").ended',timeout=10000)
 page.locator('video').evaluate('(v)=>{v.currentTime=0;return v.play()}');page.wait_for_function('document.querySelector("video").currentTime > 0.1')
 page.locator('#intro-enter').click();assert page.locator('#film-gate').is_hidden()
 for transaction in ['receipt','supplier','unknown']:
  page.locator('[data-txn="'+transaction+'"]').click()
  for hypothesis in ['unknown','fee','supplier','duplicate']:
   for proof in [False,True]:
    page.locator('#lab-type').select_option(hypothesis);page.locator('#lab-proof').set_checked(proof);page.locator('#lab-preview').click()
    assert page.locator('#lab-profit').inner_text()=='€700';assert page.locator('#lab-cash').inner_text()=='€131';assert page.locator('#lab-open').inner_text()=='1'
    if transaction=='unknown' and hypothesis=='fee':assert '€688' in page.locator('#lab-scenario-profit').inner_text()
    if transaction=='unknown' and hypothesis=='supplier':assert '€688 or €700' in page.locator('#lab-scenario-profit').inner_text()
 page.locator('#lab-hold').click();page.locator('#lab-reset').click();assert page.locator('#lab-type').input_value()=='unknown';assert not page.locator('#lab-proof').is_checked()
 results.append({'investigation_combinations':24,'hold_reset':'passed'})
 with page.expect_download() as d:page.locator('a[download]').click()
 path=d.value.path();expected=(ROOT/'assets/Shaik_Arham_Saquib_DataPoint.pdf').read_bytes();assert Path(path).read_bytes()==expected
 results.append({'cv_download_sha256':hashlib.sha256(expected).hexdigest()})
 views=['guide','overview','investigation-lab','reconciliation','invoices','performance','case-study','portfolio','about']
 for w in [320,375,390,430,768,1024,1440,1920]:
  page.set_viewport_size({'width':w,'height':1000});overflows=[]
  for view in views:
   page.goto(BASE+'/#'+view);page.wait_for_timeout(80)
   if page.evaluate('document.documentElement.scrollWidth > innerWidth'):overflows.append(view)
  results.append({'width':w,'overflow':overflows})
 page.set_viewport_size({'width':1440,'height':1000});page.goto(BASE+'/#overview');page.locator('.sidebar a[href="#invoices"]').click();page.go_back();assert page.url.endswith('#overview');page.go_forward();assert page.url.endswith('#invoices');page.reload();assert page.locator('#film-gate').is_hidden()
 page.screenshot(path='/tmp/ledgerpoint-desktop.png',full_page=True)
 page.context.clear_cookies();fresh=browser.new_page(viewport={'width':390,'height':844});fresh.goto(BASE+'/');fresh.screenshot(path='/tmp/ledgerpoint-mobile.png');assert fresh.evaluate('document.documentElement.scrollWidth <= innerWidth')
 results.append({'history_deeplinks':'passed','browser_errors':errors});browser.close()
Path('/tmp/ledgerpoint-browser-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
