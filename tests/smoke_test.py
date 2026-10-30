"""Smoke tests for 8 authored self-contained game examples.
Usage: pip install playwright && playwright install chromium
       python tests/smoke_test.py
This test uses set_content because some sandboxed environments block file://.
"""
from pathlib import Path
from shutil import which
from playwright.sync_api import sync_playwright
base=Path(__file__).resolve().parents[1]
files=list((base/'examples').glob('*.html'))
assert len(files)==8, f'Expected 8 examples, found {len(files)}'
errors=[]
with sync_playwright() as p:
    browser_path=which('chromium') or which('google-chrome')
    browser=p.chromium.launch(headless=True, executable_path=browser_path, args=['--no-sandbox'] if browser_path else [])
    context=browser.new_context()
    for file in files:
        page=context.new_page()
        page.on('pageerror',lambda e,filename=file.name:errors.append(f'{filename}: {e}'))
        page.set_content(file.read_text(encoding='utf-8'))
        page.locator('#start-btn').click()
        page.wait_for_timeout(200)
        assert page.locator('.stage').count()==1, f'No stage: {file.name}'
        print('PASS',file.name)
        page.close()
    browser.close()
assert not errors, '\n'.join(errors)
print('8/8 exported games: smoke test passed')
