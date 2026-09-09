# -*- coding: utf-8 -*-
"""Scrive sitemap.xml e robots.txt. Da rilanciare quando si aggiungono pagine:
    python3 strumenti/mappa.py
"""
import os, glob, datetime, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canonici import SITO, indirizzo

ESCLUSE = ('stampa/', '_da_cancellare/')
PRIORITA = {'index.html':'1.0', 'offerta.html':'0.9', 'ammissione.html':'0.9',
            'piano-baccalaureato.html':'0.9', 'piano-licenza.html':'0.9',
            'studiare.html':'0.8', 'istituto.html':'0.8', 'docenti.html':'0.8',
            'ricerca.html':'0.8', 'fondazione/index.html':'0.7'}

def main():
    os.chdir(BASE)
    pagine = []
    for f in sorted(glob.glob('**/*.html', recursive=True)):
        f = f.replace('\\', '/')
        if f.startswith(ESCLUSE): continue
        if f in ('sostieni.html', '404.html'): continue   # rimando e pagina d'errore
        data = datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat()
        pagine.append((f, data))

    righe = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for f, data in pagine:
        righe.append('  <url>')
        righe.append('    <loc>%s</loc>' % indirizzo(f))
        righe.append('    <lastmod>%s</lastmod>' % data)
        if f in PRIORITA:
            righe.append('    <priority>%s</priority>' % PRIORITA[f])
        righe.append('  </url>')
    righe.append('</urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write('\n'.join(righe) + '\n')

    open('robots.txt', 'w', encoding='utf-8').write(
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /stampa/\n'
        '\n'
        'Sitemap: %ssitemap.xml\n' % SITO)
    print('sitemap.xml:', len(pagine), 'pagine · robots.txt scritto')

if __name__ == '__main__':
    main()
