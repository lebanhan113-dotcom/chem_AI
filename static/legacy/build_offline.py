from pathlib import Path
p=Path(__file__).parent
html=(p/'index.html').read_text(encoding='utf8')
css=(p/'assets/style.css').read_text(encoding='utf8')
html=html.replace('  <link rel="stylesheet" href="assets/style.css" />','  <style>\n'+css.replace('</style>','<\/style>')+'\n  </style>')
html=html.replace('  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml" />','')
for x in ('bank.js','engine.js','jszip.min.js','jigsaw.js','app.js'):
    script=(p/'assets'/x).read_text(encoding='utf8')
    html=html.replace(f'  <script src="assets/{x}"></script>', '  <script>\n'+script.replace('</script>','<\/script>')+'\n  </script>')
out=p/'CHEM_MAP_TUTOR_AI_2_1_Offline.html'
out.write_text(html,encoding='utf8')
print('Built',out,out.stat().st_size)
