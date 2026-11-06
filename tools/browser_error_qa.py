from playwright.sync_api import sync_playwright
import os
BASE=os.environ.get("LEDGERPOINT_QA_URL","http://127.0.0.1:8001").rstrip("/")
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context();page=c.new_page();page.route('**/*.mp4',lambda route:route.abort());page.goto(BASE+'/');page.locator('#intro-play').click();page.get_by_role('button',name='Retry film').wait_for(timeout=20000);assert page.locator('#intro-poster').is_visible();page.unroute('**/*.mp4');page.locator('#intro-play').click();page.wait_for_function('document.querySelector("video").currentTime>0');page.keyboard.press('Escape');assert page.locator('#film-gate').is_hidden();assert page.locator('#main').evaluate('(el)=>el===document.activeElement');page.locator('[data-replay-film]').click();assert page.locator('#film-gate').is_visible();page.keyboard.press('Escape');print('Missing media, retry recovery, Escape, focus and replay: passed')

 c2=b.new_context(java_script_enabled=False);pg=c2.new_page();pg.goto(BASE);assert pg.locator('#film-gate').is_hidden();assert pg.locator('#overview').is_visible();print('JavaScript-disabled main access: passed')
 c3=b.new_context(viewport={'width':320,'height':640},has_touch=True,is_mobile=True);pg=c3.new_page();pg.goto(BASE+'/#investigation-lab');pg.locator('[data-txn="unknown"]').tap();pg.locator('#lab-preview').tap();assert pg.locator('#lab-profit').inner_text()=='€700';print('320px emulated touch lab: passed')
 b.close()
