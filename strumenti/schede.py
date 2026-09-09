# -*- coding: utf-8 -*-
"""Aggiunge alle pagine scritte a mano le schede schema.org che genera.py
mette da sé su quelle generate: le briciole di pane e, dove c'è, la FAQ.
    python3 strumenti/schede.py
"""
import os, re, json, glob, html as H, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canonici import SITO

SALTA = ('_da_cancellare', 'stampa/', 'sostieni.html')

def testo(s):
    return H.unescape(re.sub(r'<[^>]+>', '', s)).strip()

def briciole(h, cartella):
    m = re.search(r'<nav class="breadcrumb"[^>]*>(.*?)</nav>', h, re.S)
    if not m: return None
    voci, n = [], 0
    for pezzo in re.findall(r'<(a|span)\b([^>]*)>(.*?)</\1>', m.group(1), re.S):
        tag, attr, dentro = pezzo
        nome = testo(dentro)
        if not nome or nome == '·': continue
        n += 1
        v = {'@type': 'ListItem', 'position': n, 'name': nome}
        u = re.search(r'href="([^"]+)"', attr)
        if u:
            url = u.group(1).split('#')[0]
            if url and not url.startswith(('http', 'mailto:')):
                p = os.path.normpath(os.path.join(cartella, url)).replace('\\', '/')
                v['item'] = SITO + ('' if p == 'index.html' else p)
        voci.append(v)
    if len(voci) < 2: return None
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': voci}

def faq(h):
    """Domande e risposte marcate con <details><summary>…"""
    coppie = re.findall(r'<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>', h, re.S)
    if len(coppie) < 2: return None
    return {'@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': testo(d),
                            'acceptedAnswer': {'@type': 'Answer', 'text': testo(r)[:900]}}
                           for d, r in coppie]}

def main():
    os.chdir(BASE)
    fatte = 0
    for f in sorted(glob.glob('**/*.html', recursive=True)):
        f = f.replace('\\', '/')
        if f.startswith(SALTA) or f in SALTA: continue
        h = open(f, encoding='utf-8').read()
        # una pagina può già avere una sua scheda scritta a mano: in quel caso
        # aggiungo solo i tipi che mancano, in un secondo blocco (è consentito).
        schede = [x for x in (briciole(h, os.path.dirname(f)), faq(h)) if x]
        schede = [x for x in schede if '"%s"' % x['@type'] not in h]
        if not schede: continue
        dati = schede[0] if len(schede) == 1 else schede
        testo_json = json.dumps(dati, ensure_ascii=False).replace('</', '<\\/')
        h = h.replace('</head>', '<script type="application/ld+json">%s</script>\n</head>' % testo_json, 1)
        open(f, 'w', encoding='utf-8').write(h)
        fatte += 1
    print('schede aggiunte a', fatte, 'pagine scritte a mano')

if __name__ == '__main__':
    main()
