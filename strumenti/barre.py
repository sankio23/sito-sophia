# -*- coding: utf-8 -*-
"""Barre di sezione: nome della sezione + le sue pagine, sotto l'intestazione.
Le definizioni stanno qui e sono usate sia da questo inseritore (pagine
scritte a mano) sia da genera.py (pagine generate)."""

SEZIONI = {
 'istituto': ("L'Istituto", [
    ('Chi siamo', 'istituto.html'),
    ('Vision e mission', 'istituto.html#vision'),
    ('La nostra storia', 'istituto.html#storia'),
    ('Vita del campus', 'campus.html'),
    ('Docenti', 'docenti.html'),
    ('Staff', 'staff.html'),
    ('Organi di ateneo', 'staff.html#organi'),
 ]),
 'studiare': ("Studiare", [
    ('Studiare a Sophia', 'studiare.html'),
    ('Ammissione', 'ammissione.html'),
    ('Prima di candidarti', 'candidatura.html'),
    ('Rette e residenze', 'studiare.html#rette'),
    ('Offerta formativa', 'offerta.html'),
    ('Piano Baccalaureato', 'piano-baccalaureato.html'),
    ('Piano Licenza', 'piano-licenza.html'),
    ('Dottorato', 'dottorato.html'),
    ('Insegnamenti', 'corsi/index.html'),
 ]),
 'ricerca': ("Ricerca", [
    ('Panoramica', 'ricerca.html'),
    ('Centri di ricerca', 'ricerca.html#centri'),
    ('Linee di ricerca', 'ricerca.html#linee'),
    ('Pubblicazioni e rivista', 'ricerca.html#pubblicazioni'),
 ]),
 'dialogo': ("Dialogo", [
    ('Il dialogo a Sophia', 'dialogo.html'),
    ('Cattedre tematiche', 'dialogo.html#cattedre-tematiche'),
    ('Cattedre di Sophia', 'dialogo.html#cattedre-sophia'),
    ('Formazione insegnanti', 'dialogo.html#formazione'),
    ('Sophia Web Academy', 'dialogo.html#webacademy'),
 ]),
}

def barra(chiave, corrente='', su=''):
    titolo, voci = SEZIONI[chiave]
    pezzi = []
    for testo, url in voci:
        attivo = ' aria-current="page"' if url == corrente else ''
        pezzi.append('<a href="%s%s"%s>%s</a>' % (su, url, attivo, testo))
    return ('<nav class="sez-nav" aria-label="Sezione %s">\n  <div class="wrap">\n'
            '    <span class="sez-titolo">%s</span>\n'
            '    <div class="sez-voci">%s</div>\n  </div>\n</nav>'
            % (titolo, titolo, ''.join(pezzi)))
