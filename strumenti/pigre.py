# -*- coding: utf-8 -*-
"""Le immagini sotto la piega si caricano solo quando servono.
Restano immediate quelle dell'intestazione e la copertina dell'hero, che
compaiono subito: rimandarle rallenterebbe la prima impressione.
    python3 strumenti/pigre.py
"""
import os, re, glob
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    os.chdir(BASE)
    tocchi = imgs = 0
    for f in sorted(glob.glob('**/*.html', recursive=True)):
        if f.startswith(('_da_cancellare', 'stampa/')): continue
        h = open(f, encoding='utf-8').read()
        fine_testa = h.find('</header>')
        nuovo, pos, cambiata = [], 0, False
        for m in re.finditer(r'<img\b[^>]*>', h):
            tag = m.group(0)
            imgs += 1
            if (m.start() < fine_testa or 'loading=' in tag
                    or 'fetchpriority' in tag or 'hero-poster' in tag):
                continue
            nuovo.append((m.start(), m.end(), tag[:-1].rstrip() + ' loading="lazy" decoding="async">'))
            cambiata = True
        if cambiata:
            for a, b, t in reversed(nuovo):
                h = h[:a] + t + h[b:]
            open(f, 'w', encoding='utf-8').write(h)
            tocchi += 1
    print('immagini viste:', imgs, '· pagine ritoccate:', tocchi)

if __name__ == '__main__':
    main()
