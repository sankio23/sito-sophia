# -*- coding: utf-8 -*-
"""Indirizzo canonico e og:url per ogni pagina.

Il guscio delle pagine viene copiato da index.html: senza questa correzione
ogni pagina dichiarava «l'originale di questo contenuto è la home», e un
motore di ricerca smetterebbe di indicizzarle tutte tranne la home.
"""
import re

SITO = 'https://www.sophiauniversity.org/'

def indirizzo(percorso):
    p = percorso.replace('\\', '/')
    return SITO if p == 'index.html' else SITO + p

def sistema(html, percorso):
    """Riscrive canonical e og:url in base alla posizione reale del file.
    Le versioni per la stampa puntano alla pagina normale e restano fuori
    dagli indici."""
    p = percorso.replace('\\', '/')
    if p.startswith('stampa/'):
        url = indirizzo(p[len('stampa/'):])
        if 'name="robots"' not in html:
            html = html.replace('<meta name="viewport"',
                                '<meta name="robots" content="noindex, follow">\n<meta name="viewport"', 1)
    else:
        url = indirizzo(p)
    html = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), html, count=1)
    html = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), html, count=1)
    return html
