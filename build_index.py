#!/usr/bin/env python3
"""Build the canonical root index.html from the editable static sources.
Run after editing static/index.html, static/style.css or static/app.js.
The generated index.html contains the entire frontend but depends on backend for AI.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
html=(ROOT/'static/index.html').read_text(encoding='utf-8')
css=(ROOT/'static/style.css').read_text(encoding='utf-8')
js=(ROOT/'static/app.js').read_text(encoding='utf-8')
guides=(ROOT/'static/guides.js').read_text(encoding='utf-8')
assert '</style' not in css.lower() and '</script' not in js.lower() and '</script' not in guides.lower()
html=html.replace('<link rel="stylesheet" href="/static/style.css">','<style>\n'+css+'\n</style>')
html=html.replace('<script src="/static/guides.js" defer></script>', '<script>\n'+guides+'\n</script>')
html=html.replace('<script src="/static/app.js" defer></script>', '<script>\n'+js+'\nif(location.protocol === "file:"){document.getElementById("fileModeWarning").classList.remove("hidden");document.getElementById("createBtn").disabled = true;document.getElementById("serverStatus").textContent = "Cần khởi động máy chủ";}\n</script>')
assert '<style>' in html and '<script>' in html and 'Tác giả giải pháp: Lê Bá Nhẫn – Trường THPT Hòn Đất' in html
(ROOT/'index.html').write_text(html,encoding='utf-8')
print('Created',ROOT/'index.html')
