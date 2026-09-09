#!/usr/bin/env python3
"""
Genera le pagine dell'offerta formativa a partire da dati/*.json.

Perché un generatore e non pagine scritte a mano: il piano di studi, le schede
dei corsi e le schede dei docenti dicono le stesse cose da tre punti di vista
diversi. Tenuti a mano divergerebbero al primo aggiornamento — è già successo
con header e footer. Qui la sorgente è una sola: si modifica il JSON e si
rilancia questo script.

    python3 genera.py

Produce:
    piano-baccalaureato.html
    corsi/index.html      corsi/<slug>.html
    docenti/index.html    docenti/<slug>.html
"""
import json, re, os, sys, unicodedata, html
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, 'strumenti'))
from barre import barra          # la barra di sezione sotto l'intestazione
from canonici import sistema     # indirizzo canonico giusto per ogni pagina
DATI = os.path.join(BASE, 'dati')

# ---------------------------------------------------------------- utilità

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r"[^a-zA-Z0-9]+", '-', s).strip('-').lower()
    return s

def esc(s):
    return html.escape(s or '', quote=True)

def iniziali(nome):
    p = [x for x in re.split(r"[\s']+", nome) if x]
    return (p[0][0] + (p[-1][0] if len(p) > 1 else '')).upper()

ROMANI = {1: 'I', 2: 'II', 3: 'III'}

DESCR_DOPPIO = ("In convenzione con l'Università degli Studi di Perugia: "
                "il terzo anno si svolge presso l'ateneo convenzionato.")
DESCR_INTERNO = ("Percorso interamente svolto a Sophia, con un terzo anno "
                 "di approfondimento filosofico e teologico.")

# aree disciplinari, per raggruppare i settori scientifico-disciplinari
AREE = [
    ('M-PSI', 'Psicologia'),
    ('M-FIL', 'Filosofia'),
    ('SPS',   'Scienze politiche e sociali'),
    ('TH',    'Teologia'),
    ('BIB',   'Studi biblici'),
]

def area(ssd):
    for pref, nome in AREE:
        if ssd.startswith(pref):
            return nome
    return 'Altro'

# ------------------------------------------------------- guscio della pagina

def guscio(profondita):
    """Header e footer, con i percorsi relativi corretti per la profondità."""
    su = '../' * profondita
    sorgente = open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
    testa = re.search(r'^.*?</header>', sorgente, re.S).group(0)
    piede = re.search(r'<footer class="site".*?</footer>', sorgente, re.S).group(0)
    if profondita:
        def rialza(m):
            v = m.group(2)
            if v.startswith(('http', '#', 'mailto:', 'tel:', '../')):
                return m.group(0)
            return f'{m.group(1)}="{su}{v}"'
        testa = re.sub(r'(href|src)="([^"]+)"', rialza, testa)
        piede = re.sub(r'(href|src)="([^"]+)"', rialza, piede)
        testa = re.sub(r'<script[^>]*></script>', '', testa)
    testa = re.sub(r'<script type="application/ld\+json">.*?</script>', '', testa, flags=re.S)
    return testa, piede, su


# ------------------------------------------------------- dati strutturati
# Google legge queste schede per capire che cosa è una pagina: un corso, una
# persona, un percorso di laurea. Senza, deve indovinare dal testo.

SITO_URL = 'https://www.sophiauniversity.org/'

ENTE = {
    '@type': 'CollegeOrUniversity',
    'name': 'Istituto Universitario Sophia',
    'alternateName': 'Sophia University Institute',
    'url': SITO_URL,
}


def schede_json(blocchi):
    """Una o più schede schema.org, pronte da infilare nel <head>."""
    blocchi = [b for b in blocchi if b]
    if not blocchi:
        return ''
    dati = blocchi[0] if len(blocchi) == 1 else blocchi
    testo = json.dumps(dati, ensure_ascii=False, indent=None)
    testo = testo.replace('</', '<\\/')      # non deve chiudere lo <script>
    return '<script type="application/ld+json">%s</script>\n' % testo


def briciole_json(briciole, su):
    voci = []
    for n, (titolo, url) in enumerate(briciole, 1):
        v = {'@type': 'ListItem', 'position': n, 'name': titolo}
        if url:
            v['item'] = SITO_URL + ('' if url == 'index.html' else url)
        voci.append(v)
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': voci}


def pagina(profondita, titolo, descrizione, briciole, corpo, classe='',
           sezione=None, corrente='', titolo_pagina=None, schema=None):
    testa, piede, su = guscio(profondita)
    t_scheda = titolo_pagina or f'{titolo} — Istituto Universitario Sophia'
    testa = re.sub(r'<title>.*?</title>', f'<title>{esc(t_scheda)}</title>',
                   testa, flags=re.S)
    testa = re.sub(r'(name="description" content=")[^"]*(")',
                   lambda m: m.group(1) + esc(descrizione) + m.group(2), testa, count=1)
    testa = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                   lambda m: m.group(1) + esc(titolo) + m.group(2), testa)
    # l'anteprima social deve descrivere questa pagina, non sempre la home
    testa = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
                   lambda m: m.group(1) + esc(descrizione) + m.group(2), testa, count=1)
    # le versioni in altra lingua esistono solo per la home: altrove l'hreflang
    # dichiarava il falso, dicendo che l'originale italiano è la home
    testa = re.sub(r'\n<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', testa)
    bric = ' <span aria-hidden="true">·</span> '.join(
        (f'<a href="{su}{u}">{esc(t)}</a>' if u else f'<span aria-current="page">{esc(t)}</span>')
        for t, u in briciole)
    # Il guscio si ferma a </header> e riparte da <footer>: la chiusura del
    # documento e lo script del sito vanno riaggiunti qui, o le pagine
    # generate resterebbero senza menu mobile, senza aria-current e senza
    # i ripieghi delle immagini.
    schede = [briciole_json(briciole, su)] + list(schema or [])
    testa = testa.replace('</head>', schede_json(schede) + '</head>', 1)
    barra_html = ('\n\n' + barra(sezione, corrente, su)) if sezione else ''
    return f'''{testa}{barra_html}

<main id="contenuto" class="{classe}">
{corpo}
</main>

{piede}

<script src="{su}sophia-site.js"></script>
</body>
</html>
'''.replace('%%BRICIOLE%%', bric)


def intestazione(titolo, occhiello, sommario, briciole_html):
    return f'''<section class="page-hero">
  <div class="rombo pr1"></div><div class="rombo pr2"></div>
  <div class="wrap">
    <nav class="breadcrumb" aria-label="Percorso di navigazione">%%BRICIOLE%%</nav>
    <p class="eyebrow light">{esc(occhiello)}</p>
    <h1>{esc(titolo)}</h1>
    {f'<p>{esc(sommario)}</p>' if sommario else ''}
  </div>
</section>'''

# ------------------------------------------------------------- modello dati

PIANI = [
    {'chiave': 'baccalaureato', 'file': 'piano-baccalaureato.json',
     'corso_di_studi': 'Baccalaureato in Filosofia e Scienze Umane',
     'breve': 'Baccalaureato', 'pagina': 'piano-baccalaureato.html',
     'pdf': 'media/Piano-di-studi-Baccalaureato.pdf'},
    {'chiave': 'licenza', 'file': 'piano-licenza.json',
     'corso_di_studi': 'Licenza Magistrale in Filosofia, Economia di Comunione e Ambiente',
     'breve': 'Licenza magistrale', 'pagina': 'piano-licenza.html',
     'pdf': 'media/Piano-di-studi-Licenza-magistrale.pdf'},
]

# non sono persone: sono titolarità ancora da assegnare
NON_PERSONE = {'Docente di Economia', 'Contrattista', 'Docente da assegnare'}


def carica():
    def _leggi(nome, chiave, vuoto):
        try:
            return json.load(open(os.path.join(DATI, nome), encoding='utf-8'))[chiave]
        except FileNotFoundError:
            return vuoto
    try:
        _reg = json.load(open(os.path.join(DATI, 'docenti.json'), encoding='utf-8'))
        anagrafica, categorie = _reg['docenti'], _reg['categorie']
    except FileNotFoundError:
        anagrafica, categorie = [], []
    staff = _leggi('staff.json', 'staff', [])
    organi = _leggi('organi.json', 'gruppi', [])

    piani = []
    corsi = {}
    docenti = defaultdict(lambda: {'nome': '', 'corsi': []})

    for meta in PIANI:
        percorso = os.path.join(DATI, meta['file'])
        if not os.path.exists(percorso):
            continue
        piano = json.load(open(percorso, encoding='utf-8'))
        piano['meta'] = meta
        for ind in piano['indirizzi']:
            ind['slug'] = slug(meta['chiave'] + '-' + ind['nome'] +
                               ('-doppio-titolo' if ind['doppio_titolo'] else ''))
            ind['totale_ects'] = sum(int(a['totale_ects']) for a in ind['anni'])
            for n, anno in enumerate(ind['anni'], 1):
                for c in anno['corsi']:
                    c['slug'] = slug(c['corso'])
                    c['esterno'] = c['docente'].startswith('Esame sostenuto')
                    c['anno'] = n
                    sch = corsi.setdefault(c['slug'], {
                        'nome': c['corso'], 'slug': c['slug'], 'ects': c['ects'],
                        'semestre': c['semestre'], 'ssd': c['ssd'], 'esterno': c['esterno'],
                        'docenti': [], 'da_assegnare': [], 'presenze': []})
                    sch['presenze'].append({
                        'indirizzo': ind['nome'], 'slug_ind': ind['slug'],
                        'doppio': bool(ind['doppio_titolo']), 'anno': n,
                        'corso_di_studi': meta['corso_di_studi'], 'pagina': meta['pagina'],
                        'breve': meta['breve']})
                    if not c['esterno'] and c['docente']:
                        for nome in [x.strip() for x in c['docente'].split(';')]:
                            if not nome:
                                continue
                            if nome in NON_PERSONE:
                                if nome not in sch['da_assegnare']:
                                    sch['da_assegnare'].append(nome)
                                continue
                            if nome not in sch['docenti']:
                                sch['docenti'].append(nome)
                            d = docenti[slug(nome)]
                            d['nome'] = nome
                            if c['slug'] not in [x['slug'] for x in d['corsi']]:
                                d['corsi'].append(sch)
        piani.append(piano)

    for a in anagrafica:
        docenti[slug(a['nome'])]['nome'] = a['nome']
    reg = {a['nome']: a for a in anagrafica}
    for s, d in docenti.items():
        d['slug'] = s
        a = reg.get(d['nome'], {})
        d['ruolo'] = a.get('ruolo', '')
        d['dip'] = a.get('dipartimento', '')
        d['foto'] = a.get('foto', '')
        d['profilo'] = a.get('profilo', '')
        d['stato'] = a.get('stato', 'da_confermare')
        d['categoria'] = a.get('categoria', 'contratto')
        d['qualifica'] = a.get('qualifica', '')
        d['iniziali'] = iniziali(d['nome'])
        d['ects'] = sum(int(c['ects']) for c in d['corsi'] if c['ects'].isdigit())
    return piani, corsi, dict(docenti), categorie, staff, organi


# ------------------------------------------------------------ frammenti HTML

def chip_semestre(s):
    if not s:
        return ''
    if 'anno' in s:
        return f'<span class="sem sem-annuale">{esc(s)}</span>'
    return f'<span class="sem sem-{esc(s.lower())}">{esc(s)} semestre</span>'


def riga_corso(c, su, con_docente=True):
    nome = f'<a href="{su}corsi/{c["slug"]}.html">{esc(c["corso"])}</a>'
    if c['esterno']:
        doc = '<span class="esterno">Esame sostenuto a UniPg</span>'
    elif c['docente']:
        # le titolarità non ancora assegnate ("Docente di Economia",
        # "Contrattista") non sono persone: niente collegamento
        pezzi = []
        for n in c['docente'].split(';'):
            n = n.strip()
            if not n:
                continue
            if n in NON_PERSONE:
                pezzi.append(f'<span class="esterno">{esc(n)}</span>')
            else:
                pezzi.append(f'<a href="{su}docenti/{slug(n)}.html">{esc(n)}</a>')
        doc = ' · '.join(pezzi)
    elif c['docente']:
        doc = f'<span class="esterno">{esc(c["docente"])}</span>'
    else:
        doc = '<span class="esterno">—</span>'
    return f'''      <li class="corso-riga">
        <span class="ects"><b>{esc(c["ects"])}</b><small>ECTS</small></span>
        <span class="nome">{nome}{f'<span class="ssd">{esc(c["ssd"])}</span>' if c["ssd"] else ''}</span>
        <span class="doc">{doc if con_docente else ''}</span>
        <span class="sem-cell">{chip_semestre(c["semestre"])}</span>
      </li>'''

# ------------------------------------------------------------------ pagine

# Atenei convenzionati per il doppio titolo. Il logo è opzionale: se il
# file non c'è, sophia-site.js lo nasconde e resta la sola dicitura testuale.
PARTNER = {
    'Università degli Studi di Perugia': {
        'url':    'https://fissuf.unipg.it/',
        'logo':   'loghi/logo-unipg.png',
        'sigla':  'Dipartimento FISSUF',
    },
}


def partner(ateneo, su=''):
    """Marchio dell'ateneo convenzionato, o dicitura di percorso interno."""
    if not ateneo:
        return '<span class="badge">Percorso interno a Sophia</span>'
    p = PARTNER.get(ateneo)
    if not p:
        return f'<span class="badge badge-oro">Doppio titolo con l\'{esc(ateneo)}</span>'
    logo = (f'<img src="{su}{p["logo"]}" alt="" width="52" height="52" decoding="async">'
            if p.get('logo') else '')
    dip = f'<span class="partner-dip">{esc(p["sigla"])}</span>' if p.get('sigla') else ''
    return (f'<a class="partner" href="{p["url"]}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="Doppio titolo con l\'{esc(ateneo)} — vai al sito del dipartimento">'
            f'{logo}<span class="partner-testo">'
            f'<span class="partner-k">Doppio titolo con</span>'
            f'{esc(ateneo)}{dip}</span>'
            f'<span class="partner-freccia" aria-hidden="true">↗</span></a>')


def genera_piano(piano, corsi, docenti):
    meta = piano['meta']
    su = ''
    schede = ''
    for ind in piano['indirizzi']:
        anni = ''
        for n, anno in enumerate(ind['anni'], 1):
            righe = '\n'.join(riga_corso(c, su) for c in anno['corsi'])
            anni += f'''
    <section class="anno" aria-labelledby="{ind['slug']}-{n}">
      <div class="anno-testa">
        <h3 id="{ind['slug']}-{n}">{ROMANI[n]} anno</h3>
        <p class="anno-tot"><b>{anno['totale_ects']}</b> ECTS · {len(anno['corsi'])} insegnament{'o' if len(anno['corsi'])==1 else 'i'}</p>
      </div>
      <ol class="corso-lista">
{righe}
      </ol>
    </section>'''
        badge = partner(ind['doppio_titolo'], su)
        scopri = ''
        if ind['nome'] in INDIRIZZI_PAGINA:
            scopri = ('<p class="scarica-pdf" style="margin-top:22px">'
                      '<a class="btn btn-navy" href="%s%s">Scopri questo indirizzo →</a></p>'
                      % (su, INDIRIZZI_PAGINA[ind['nome']]['file']))
        schede += f'''
  <section class="indirizzo" id="{ind['slug']}">
    <div class="wrap">
      <div class="indirizzo-testa">
        <div>
          <p class="eyebrow">Indirizzo</p>
          <h2>{esc(ind['nome'])}</h2>
          {badge}
        </div>
        <p class="grande-num"><b>{ind['totale_ects']}</b><small>ECTS complessivi</small></p>
      </div>
      {anni}
      {scopri}
    </div>
  </section>'''

    sommari = '\n'.join(f'''      <a class="card" href="#{i['slug']}">
        <span class="tag">{'Doppio titolo' if i['doppio_titolo'] else 'Solo Sophia'}</span>
        <h3>{esc(i['nome'])}</h3>
        <p>{esc(i.get('descrizione') or (DESCR_DOPPIO if i['doppio_titolo'] else DESCR_INTERNO))}</p>
        <span class="more">{i['totale_ects']} ECTS · {len(i['anni'])} anni →</span>
      </a>''' for i in piano['indirizzi'])

    corpo = f'''{intestazione(piano['titolo'], 'Offerta formativa · ' + meta['breve'], piano['premessa'], None)}

<section class="stampa-solo">
  <div class="wrap"><p>Istituto Universitario Sophia · {esc(piano['titolo'])} · {esc(piano['sottotitolo'])}</p></div>
</section>

<section class="sommario-indirizzi">
  <div class="wrap">
    <div class="cards c{len(piano['indirizzi'])}">
{sommari}
    </div>
    <p class="scarica-pdf"><a class="btn btn-navy" href="{meta['pdf']}" download>Scarica il piano in PDF</a></p>
  </div>
</section>
{schede}

<section class="band">
  <div class="wrap">
    <h2>Vuoi parlarne con qualcuno?</h2>
    <p>I referenti per i futuri studenti rispondono a domande su piano di studi, riconoscimento dei crediti e doppio titolo.</p>
    <a class="btn btn-navy" href="ammissione.html">Ammissione e iscrizione</a>
  </div>
</section>'''
    briciole = [('Home', 'index.html'), ('Offerta formativa', 'offerta.html'),
                (meta['breve'], None)]
    scheda_piano = {
        '@context': 'https://schema.org', '@type': 'EducationalOccupationalProgram',
        'name': piano['titolo'], 'description': piano['premessa'],
        'url': SITO_URL + meta['pagina'], 'provider': ENTE, 'inLanguage': 'it',
        'educationalProgramMode': 'full-time',
        'timeToComplete': 'P3Y' if meta['chiave'] == 'baccalaureato' else 'P2Y',
    }
    tot = piano['indirizzi'][0]['totale_ects']
    return pagina(0, piano['titolo'],
                  f"Piano degli studi: {len(piano['indirizzi'])} percorsi, {tot} ECTS, con doppio titolo in convenzione con l'Università degli Studi di Perugia.",
                  briciole, corpo, 'piano',
                  sezione='studiare', corrente=piano['meta']['pagina'],
                  schema=[scheda_piano])


# ---------------------------------------------------------- pagine indirizzo
# Un indirizzo non aveva una pagina propria: viveva come paragrafo dentro il
# piano di studi. Chi cerca «studiare psicologia a Firenze» non poteva
# trovarci, perché la pagina che risponde a quella domanda non esisteva.

INDIRIZZI_PAGINA = {
    'Indirizzo in Psicologia': {
        'file': 'indirizzo-psicologia.html',
        'h1': 'Studiare Psicologia a Firenze',
        'titolo_scheda': 'Studiare Psicologia a Firenze — Istituto Universitario Sophia',
        'descrizione': ('Il Baccalaureato con indirizzo in Psicologia a Firenze: doppio titolo con '
                        "l'Università degli Studi di Perugia, 180 ECTS in tre anni, classi ridotte."),
        'sommario': ('Tre anni a Firenze, con il doppio titolo dell\u2019Università degli Studi di '
                     'Perugia: una formazione psicologica costruita dentro una domanda più ampia '
                     'sulla persona.'),
    },
    'Indirizzo in Filosofia': {
        'file': 'indirizzo-filosofia.html',
        'h1': 'Studiare Filosofia a Firenze',
        'titolo_scheda': 'Studiare Filosofia a Firenze — Istituto Universitario Sophia',
        'descrizione': ('Il Baccalaureato con indirizzo in Filosofia a Firenze: doppio titolo con '
                        "l'Università degli Studi di Perugia, 180 ECTS in tre anni, classi ridotte."),
        'sommario': ('Tre anni a Firenze, con il doppio titolo dell\u2019Università degli Studi di '
                     'Perugia: la filosofia come esercizio del pensiero e come pratica di dialogo.'),
    },
    'Indirizzo in Filosofia — percorso Sophia': {
        'file': 'indirizzo-filosofia-sophia.html',
        'h1': 'Filosofia e teologia: il percorso Sophia',
        'titolo_scheda': 'Filosofia e teologia, il percorso Sophia — Istituto Universitario Sophia',
        'descrizione': ('Il Baccalaureato interamente svolto a Sophia, con prevalenza di crediti in '
                        'ambito filosofico-teologico: 180 ECTS in tre anni, a Firenze e a Loppiano.'),
        'sommario': ('Un percorso interamente interno a Sophia, dove la filosofia si intreccia con '
                     'la teologia e con la vita della comunità accademica.'),
    },
}


def blocco_dove():
    # NOTA INTERNA: da confermare con la Segreteria come si distribuiscono le
    # lezioni fra la sede di Firenze e il campus di Loppiano, e correggere qui.
    return '''
<section class="stats">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Dove si studia</p><h2>A Firenze, dentro una comunità</h2></div>
    <div class="cards c2" style="margin-top:30px">
      <div class="card">
        <h3 style="font-size:20px">La sede di Firenze</h3>
        <p>Dall\u2019anno accademico 2026/2027 il Baccalaureato si tiene nella sede di Firenze,
        in Piazza Tasso 1/A, a pochi passi dal centro.</p>
      </div>
      <div class="card">
        <h3 style="font-size:20px">Il campus di Loppiano</h3>
        <p>A trenta chilometri dalla città, nella cittadella internazionale di Loppiano
        (Figline e Incisa Valdarno), ci sono le residenze, la biblioteca e la vita accademica
        quotidiana.</p>
      </div>
    </div>
  </div>
</section>'''


def blocco_titolo(ind):
    if not ind['doppio_titolo']:
        return '''
<section>
  <div class="wrap narrow prose">
    <p class="eyebrow">Il titolo</p>
    <h2 style="margin-top:8px">Un Baccalaureato interamente a Sophia</h2>
    <p>Il percorso si conclude con il Baccalaureato in Filosofia e Scienze Umane, titolo
    accademico pontificio rilasciato dall\u2019Istituto Universitario Sophia, eretto dalla
    Santa Sede. Tutti gli esami si sostengono a Sophia.</p>
  </div>
</section>'''
    # NOTA INTERNA: la frase sull'accesso all'albo va confermata dalla Segreteria
    # prima del lancio (classe L-24, esame di Stato, sezione dell'albo).
    albo = ('''<p>La laurea statale in classe L-24 è il titolo che apre il percorso professionale
    in psicologia: dà accesso alle lauree magistrali in Psicologia e, superato l\u2019esame di
    Stato, all\u2019albo degli psicologi.</p>'''
            if 'Psicologia' in ind['nome'] else '')
    return f'''
<section>
  <div class="wrap narrow prose">
    <p class="eyebrow">Il titolo</p>
    <h2 style="margin-top:8px">Due lauree in tre anni</h2>
    <p>Il percorso rilascia due titoli: il <b>Baccalaureato in Filosofia e Scienze Umane</b>,
    titolo accademico pontificio dell\u2019Istituto Universitario Sophia, e la <b>laurea statale
    italiana</b> dell\u2019<a href="https://fissuf.unipg.it/" target="_blank" rel="noopener">Università
    degli Studi di Perugia</a>, nel corso interclasse L-5 e L-24 «Filosofia e Scienze e Tecniche
    Psicologiche». Alcuni esami si sostengono a Perugia: nel piano che segue sono segnalati uno
    per uno.</p>
    {albo}
  </div>
</section>'''


def genera_indirizzo(piano, ind, corsi, docenti):
    meta = piano['meta']
    conf = INDIRIZZI_PAGINA[ind['nome']]
    su = ''

    anni = ''
    for n, anno in enumerate(ind['anni'], 1):
        righe = '\n'.join(riga_corso(c, su) for c in anno['corsi'])
        anni += f'''
    <section class="anno" aria-labelledby="anno-{n}">
      <div class="anno-testa">
        <h3 id="anno-{n}">{ROMANI[n]} anno</h3>
        <p class="anno-tot"><b>{anno['totale_ects']}</b> ECTS · {len(anno['corsi'])} insegnament{'o' if len(anno['corsi'])==1 else 'i'}</p>
      </div>
      <ol class="corso-lista">
{righe}
      </ol>
    </section>'''

    # i nomi vanno letti come li legge il resto del sito: separati da «;»,
    # saltando gli esami sostenuti a Perugia e le titolarità non ancora assegnate
    nomi = []
    for anno in ind['anni']:
        for c in anno['corsi']:
            if c.get('esterno') or not c.get('docente'):
                continue
            for n in [x.strip() for x in c['docente'].split(';')]:
                if n and n not in NON_PERSONE and n not in nomi:
                    nomi.append(n)
    schede_doc = '\n'.join(
        f'''<a class="mini" href="{su}docenti/{slug(n)}.html">'''
        f'''<span class="avatar">{esc(iniziali(n))}</span><span>{esc(n)}</span></a>'''
        for n in nomi[:14])

    corpo = f'''{intestazione(conf['h1'], 'Baccalaureato in Filosofia e Scienze Umane · ' + ind['nome'], conf['sommario'], None)}

<section>
  <div class="wrap narrow prose">
    <p class="lead">{esc(ind.get('descrizione') or '')}</p>
    <p>Il percorso dura tre anni per un totale di {ind['totale_ects']} ECTS, con un rapporto fra
    docenti e studenti di circa uno a cinque. Qui sotto trovi il piano completo, insegnamento per
    insegnamento, con i docenti che li tengono.</p>
    <p><a href="{su}ammissione.html">Come si entra a Sophia →</a></p>
  </div>
</section>
{blocco_titolo(ind)}
{blocco_dove()}

<section class="piano">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Il piano degli studi</p><h2>Tre anni, {ind['totale_ects']} ECTS</h2></div>
    {anni}
    <p class="scarica-pdf" style="margin-top:26px"><a class="btn btn-navy" href="{su}{meta['pdf']}" download>Scarica il piano in PDF</a>
    &nbsp;<a class="btn btn-ghost" href="{su}{meta['pagina']}">Confronta i tre indirizzi</a></p>
  </div>
</section>

<section class="stats">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Chi insegna</p><h2>I docenti di questo indirizzo</h2></div>
    <div class="docenti-mini" style="margin-top:26px">{schede_doc}</div>
    <p style="margin-top:22px"><a href="{su}docenti.html">Tutti i docenti dell\u2019Istituto →</a></p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2>Vuoi parlarne con qualcuno?</h2>
    <p>I referenti per i futuri studenti rispondono a domande su piano di studi, riconoscimento
    dei crediti, doppio titolo e residenze.</p>
    <a class="btn btn-navy" href="{su}ammissione.html">Ammissione e iscrizione</a>
    &nbsp;<a class="btn btn-ghost" href="{su}contatti.html">Richiedi informazioni</a>
  </div>
</section>'''

    briciole = [('Home', 'index.html'), ('Offerta formativa', 'offerta.html'),
                (meta['breve'], meta['pagina']), (ind['nome'], None)]
    scheda = {
        '@context': 'https://schema.org', '@type': 'EducationalOccupationalProgram',
        'name': f"{meta['corso_di_studi']} — {ind['nome']}",
        'description': conf['descrizione'],
        'url': SITO_URL + conf['file'],
        'provider': ENTE,
        'educationalProgramMode': 'full-time',
        'timeToComplete': 'P3Y',
        'numberOfCredits': {'@type': 'StructuredValue', 'value': ind['totale_ects'],
                            'unitText': 'ECTS'},
        'educationalCredentialAwarded': (
            'Baccalaureato in Filosofia e Scienze Umane (titolo pontificio) e laurea statale '
            "dell'Università degli Studi di Perugia, classe interclasse L-5 e L-24"
            if ind['doppio_titolo'] else
            'Baccalaureato in Filosofia e Scienze Umane (titolo pontificio)'),
        'inLanguage': 'it',
        'occupationalCategory': ('Psicologo' if 'Psicologia' in ind['nome'] else None),
    }
    scheda = {k: v for k, v in scheda.items() if v is not None}
    return pagina(0, conf['h1'], conf['descrizione'], briciole, corpo, 'indirizzo',
                  sezione='studiare', corrente=conf['file'],
                  titolo_pagina=conf['titolo_scheda'], schema=[scheda])


def genera_corso(c, su='../'):
    presenze = '\n'.join(
        f'''        <li><b><a href="{su}{p['pagina']}">{esc(p['breve'])}</a> · {esc(p['indirizzo'])}</b>'''
        f'''<span>{ROMANI[p['anno']]} anno</span></li>''' for p in c['presenze'])
    if c['esterno']:
        doc_html = '''<p class="esterno-nota">L'esame si sostiene presso l'Università degli Studi di Perugia,
        nell'ambito della convenzione di doppio titolo. La docenza è affidata all'ateneo convenzionato.</p>'''
    elif c['da_assegnare'] and not c['docenti']:
        doc_html = ('<p class="esterno-nota">Titolarità indicata nel piano come '
                    f'«{esc(c["da_assegnare"][0])}»: il docente non è ancora stato assegnato.</p>')
    elif c['docenti']:
        doc_html = '<div class="docenti-mini">' + ''.join(
            f'''<a class="mini" href="{su}docenti/{slug(n)}.html">
              <span class="avatar">{esc(iniziali(n))}</span><span>{esc(n)}</span></a>''' for n in c['docenti']) + '</div>'
    else:
        doc_html = '<p class="esterno-nota">Docenza non ancora assegnata.</p>'

    vuoto = lambda t, n: f'''    <section class="da-compilare">
      <h2>{t}</h2>
      <p>Questa sezione non è ancora stata compilata.</p>
    </section>'''

    corpo = f'''{intestazione(c['nome'], f"Insegnamento · {area(c['ssd'])}", '', None)}

<section>
  <div class="wrap cols2">
    <div class="prose">
      {doc_html}
      <h2>Nel piano di studi</h2>
      <ul class="presenze">
{presenze}
      </ul>
      <p style="margin-top:26px"><a class="btn btn-ghost" href="{su}{c['presenze'][0]['pagina']}">Torna al piano degli studi</a></p>
    </div>
    <div class="panel">
      <ul class="deflist">
        <li><b>Crediti</b><span>{esc(c['ects'])} ECTS</span></li>
        <li><b>Semestre</b><span>{esc(c['semestre']) or '—'}</span></li>
        <li><b>Settore</b><span>{esc(c['ssd']) or '—'}</span></li>
        <li><b>Area</b><span>{esc(area(c['ssd']))}</span></li>
        <li><b>Corso di studi</b><span>{esc(' · '.join(sorted({p['breve'] for p in c['presenze']})))}</span></li>
      </ul>
    </div>
  </div>
</section>

<section style="padding-top:0">
  <div class="narrow prose">
{vuoto('Obiettivi formativi', 'Va redatta dal docente titolare.')}
{vuoto('Contenuti del corso', 'Va redatta dal docente titolare.')}
{vuoto('Modalità di verifica', 'Va redatta dal docente titolare.')}
{vuoto('Bibliografia', 'Va redatta dal docente titolare.')}
  </div>
</section>'''
    briciole = [('Home', 'index.html'), ('Offerta formativa', 'offerta.html'),
                (c['presenze'][0]['breve'], c['presenze'][0]['pagina']), (c['nome'], None)]
    scheda = {
        '@context': 'https://schema.org', '@type': 'Course',
        'name': c['nome'],
        'description': f"{c['nome']}: insegnamento da {c['ects']} ECTS del "
                       f"Baccalaureato in Filosofia e Scienze Umane dell'Istituto Universitario Sophia.",
        'url': SITO_URL + f"corsi/{c['slug']}.html",
        'provider': ENTE, 'inLanguage': 'it',
        'educationalCredentialAwarded': 'ECTS',
        'numberOfCredits': c['ects'],
        'courseCode': c['ssd'] or None,
        'hasCourseInstance': {
            '@type': 'CourseInstance',
            'courseMode': 'onsite',
            'location': {'@type': 'Place', 'name': 'Istituto Universitario Sophia',
                         'address': {'@type': 'PostalAddress', 'addressLocality': 'Firenze',
                                     'addressCountry': 'IT'}},
            'instructor': [{'@type': 'Person', 'name': n} for n in c['docenti']] or None,
        },
    }
    scheda = {k: v for k, v in scheda.items() if v is not None}
    scheda['hasCourseInstance'] = {k: v for k, v in scheda['hasCourseInstance'].items() if v is not None}
    return pagina(1, c['nome'],
                  f"{c['nome']}: {c['ects']} ECTS, settore {c['ssd'] or 'non assegnato'}, Istituto Universitario Sophia.",
                  briciole, corpo, 'scheda-corso', sezione='studiare', schema=[scheda])


def genera_docente(d, su='../'):
    corsi = ''.join(f'''      <li class="corso-riga">
        <span class="ects"><b>{esc(c['ects'])}</b><small>ECTS</small></span>
        <span class="nome"><a href="{su}corsi/{c['slug']}.html">{esc(c['nome'])}</a>
          {f'<span class="ssd">{esc(c["ssd"])}</span>' if c['ssd'] else ''}</span>
        <span class="doc">{esc(area(c['ssd']))}</span>
        <span class="sem-cell">{chip_semestre(c['semestre'])}</span>
      </li>''' for c in sorted(d['corsi'], key=lambda x: (-int(x['ects']) if x['ects'].isdigit() else 0, x['nome'])))

    ritratto = (f'<img src="{esc(d["foto"])}" alt="{esc(d["nome"])}" loading="lazy" data-initials="{esc(d["iniziali"])}">'
                if d['foto'] else f'<span class="avatar-fallback" aria-hidden="true">{esc(d["iniziali"])}</span>')
    aree = sorted({area(c['ssd']) for c in d['corsi'] if c['ssd']})

    _cds = sorted({p['breve'] for c in d['corsi'] for p in c['presenze']})
    _dove = ('In ' + ' e '.join(_cds)) if _cds else ''
    if d['corsi']:
        blocco_corsi = f'''      <h2>Insegnamenti</h2>
      <p>{esc(_dove)}, per un totale di <b>{d['ects']} ECTS</b>.</p>
      <ol class="corso-lista compatta" style="margin-top:20px">
{corsi}
      </ol>
      {'<div class="chips">' + ''.join(f'<span class="chip">{esc(a)}</span>' for a in aree) + '</div>' if aree else ''}'''
    else:
        blocco_corsi = '''      <h2>Insegnamenti</h2>
      <p class="esterno-nota">Non risultano insegnamenti nei piani di studio del
      Baccalaureato e della Licenza magistrale.</p>'''

    avviso = ''

    voci = []
    if d['qualifica']: voci.append(f'<li><b>Qualifica</b><span>{esc(d["qualifica"])}</span></li>')
    _extra = d['ruolo'].split(' · ')[0] if ' · ' in d['ruolo'] else ''
    if _extra: voci.append(f'<li><b>Incarico</b><span>{esc(_extra)}</span></li>')
    if d['dip']:   voci.append(f'<li><b>Dipartimento</b><span>{esc(d["dip"])}</span></li>')
    n_ins = len(d['corsi'])
    voci.append(f'<li><b>Insegnamenti</b><span>{n_ins} · {d["ects"]} ECTS</span></li>')
    if d['profilo']:
        voci.append(f'<li><b>Scheda ufficiale</b><span><a href="{esc(d["profilo"])}" target="_blank" rel="noopener">sophiauniversity.org</a></span></li>')
    scheda = '<ul class="deflist">' + ''.join(voci) + '</ul>'

    corpo = f'''{intestazione(d['nome'], d['ruolo'] or 'Docente', '', None)}

<section>
  <div class="wrap cols2 alto">
    <div>
      <div class="ritratto">{ritratto}</div>
      <div class="panel" style="margin-top:24px;padding:24px">{scheda}</div>
    </div>
    <div class="prose">
      {avviso}
{blocco_corsi}
      <section class="da-compilare" style="margin-top:32px">
        <h2>Profilo</h2>
        <p>Questa sezione non è ancora stata compilata.</p>
      </section>
      <section class="da-compilare">
        <h2>Ricerca</h2>
        <p>Questa sezione non è ancora stata compilata.</p>
      </section>
      <section class="da-compilare">
        <h2>Pubblicazioni principali</h2>
        <p>Questa sezione non è ancora stata compilata.</p>
      </section>
      <section class="da-compilare">
        <h2>Contatti e ricevimento</h2>
        <p>Questa sezione non è ancora stata compilata.</p>
      </section>
      <p style="margin-top:26px"><a class="btn btn-ghost" href="{su}docenti.html">Tutti i docenti</a></p>
    </div>
  </div>
</section>'''
    briciole = [('Home', 'index.html'), ('Docenti', 'docenti.html'), (d['nome'], None)]
    scheda = {
        '@context': 'https://schema.org', '@type': 'Person',
        'name': d['nome'],
        'url': SITO_URL + f"docenti/{d['slug']}.html",
        'jobTitle': d.get('qualifica') or d.get('ruolo') or None,
        'affiliation': ENTE, 'worksFor': ENTE,
    }
    scheda = {k: v for k, v in scheda.items() if v is not None}
    return pagina(1, d['nome'],
                  f"{d['nome']}: profilo e insegnamenti presso l'Istituto Universitario Sophia.",
                  briciole, corpo, 'scheda-docente', sezione='istituto', schema=[scheda])


def genera_indice_corsi(corsi):
    per_area = defaultdict(list)
    for c in corsi.values():
        per_area[area(c['ssd'])].append(c)
    sezioni = ''
    for a in sorted(per_area, key=lambda x: (x == 'Altro', x)):
        righe = ''.join(f'''      <li class="corso-riga">
        <span class="ects"><b>{esc(c['ects'])}</b><small>ECTS</small></span>
        <span class="nome"><a href="{c['slug']}.html">{esc(c['nome'])}</a>
          {f'<span class="ssd">{esc(c["ssd"])}</span>' if c['ssd'] else ''}</span>
        <span class="doc">{' · '.join(esc(n) for n in c['docenti']) or '<span class="esterno">UniPg</span>'}</span>
        <span class="sem-cell">{chip_semestre(c['semestre'])}</span>
      </li>''' for c in sorted(per_area[a], key=lambda x: x['nome']))
        sezioni += f'''
    <section class="anno">
      <div class="anno-testa"><h2>{esc(a)}</h2><p class="anno-tot"><b>{len(per_area[a])}</b> insegnament{'o' if len(per_area[a])==1 else 'i'}</p></div>
      <ol class="corso-lista">{righe}</ol>
    </section>'''
    corpo = f'''{intestazione('Insegnamenti', 'Baccalaureato in Filosofia e Scienze Umane',
        f'{len(corsi)} insegnamenti, raggruppati per area disciplinare.', None)}
<section><div class="wrap">{sezioni}</div></section>'''
    return pagina(1, 'Insegnamenti',
                  'Tutti gli insegnamenti del Baccalaureato in Filosofia e Scienze Umane dell\'Istituto Universitario Sophia.',
                  [('Home', 'index.html'), ('Offerta formativa', 'offerta.html'), ('Insegnamenti', None)], corpo,
                  sezione='studiare', corrente='corsi/index.html')


def genera_indice_docenti(docenti, categorie, profondita=0):
    def scheda(d):
        foto = (f'<img src="{esc(d["foto"])}" alt="{esc(d["nome"])}" loading="lazy" data-initials="{esc(d["iniziali"])}">'
                if d['foto'] else f'<span class="avatar-fallback" aria-hidden="true">{esc(d["iniziali"])}</span>')
        n = len(d['corsi'])
        extra = d['ruolo'].split(' · ')[0] if ' · ' in d['ruolo'] else ''
        insegna = (f'<div class="dept">{n} insegnament{"o" if n == 1 else "i"}</div>' if n else '')
        return f'''        <a class="person" href="{PRE}docenti/{d['slug']}.html">
          <div class="photo">{foto}</div>
          <h3>{esc(d['nome'])}</h3>
          <div class="role">{esc(d['qualifica'] or 'Docente')}</div>
          {f'<div class="dept">{esc(extra)}</div>' if extra else ''}
          {insegna}
        </a>'''

    PRE = '../' * profondita

    # In evidenza: chi ha insegnamenti attivi nei corsi di laurea,
    # con il ruolo accademico tra parentesi. Il raggruppamento per
    # qualifica resta sotto, per chi non insegna quest'anno.
    ETICH_SING = {c['chiave']: c.get('singolare') for c in categorie}
    squadra = sorted((d for d in docenti.values() if d['corsi']),
                     key=lambda x: x['nome'].split()[-1])
    con_corsi = {d['slug'] for d in squadra}

    def scheda_squadra(d):
        foto = (f'<img src="{esc(d["foto"])}" alt="{esc(d["nome"])}" loading="lazy" data-initials="{esc(d["iniziali"])}">'
                if d['foto'] else f'<span class="avatar-fallback" aria-hidden="true">{esc(d["iniziali"])}</span>')
        n = len(d['corsi'])
        return f'''        <a class="person" href="{PRE}docenti/{d['slug']}.html">
          <div class="photo">{foto}</div>
          <h3>{esc(d['nome'])}</h3>
          <div class="role">({esc(d['qualifica'] or 'Docente')})</div>
          <div class="dept">{n} {'insegnamento' if n == 1 else 'insegnamenti'}</div>
        </a>'''

    filtri = [f'<a href="#squadra">Con insegnamenti <span>{len(squadra)}</span></a>']
    sezioni = f'''
      <section class="people-section" id="squadra">
        <h2>Chi insegna nell'A.A. 2026/2027</h2>
        <p class="sub">I docenti titolari di insegnamento nel Baccalaureato e nella Licenza magistrale, con il ruolo accademico tra parentesi.</p>
        <div class="people-grid">
{''.join(scheda_squadra(d) for d in squadra)}
        </div>
      </section>'''

    per_cat = {}
    for d in docenti.values():
        if d['slug'] in con_corsi:
            continue
        per_cat.setdefault(d['categoria'], []).append(d)

    for cat in categorie:
        k = cat['chiave']
        gruppo = sorted(per_cat.get(k, []), key=lambda x: x['nome'].split()[-1])
        if not gruppo:
            continue
        filtri.append(f'<a href="#{k}">{esc(cat["etichetta"])} <span>{len(gruppo)}</span></a>')
        sezioni += f'''
      <section class="people-section" id="{k}">
        <h2>{esc(cat['etichetta'])}</h2>
        {f'<p class="sub">{esc(cat["nota"])}</p>' if cat.get('nota') else ''}
        <div class="people-grid">
{''.join(scheda(d) for d in gruppo)}
        </div>
      </section>'''

    corpo = f'''{intestazione('Docenti', 'Persone',
        f"{len(docenti)} docenti. In apertura chi insegna nei corsi di laurea di quest’anno; a seguire il resto del corpo accademico, per qualifica.", None)}

<nav class="indice-categorie" aria-label="Categorie di docenti">
  <div class="wrap">{''.join(filtri)}</div>
</nav>

<section>
  <div class="wrap">{sezioni}
  </div>
</section>'''
    return pagina(profondita, 'Docenti',
                  "I docenti dell'Istituto Universitario Sophia: chi insegna nei corsi di laurea e il corpo accademico, con i rispettivi insegnamenti.",
                  [('Home', 'index.html'), ('Docenti', None)], corpo,
                  sezione='istituto', corrente='docenti.html')


def genera_staff(staff, organi):
    def scheda(p):
        foto = (f'<img src="{esc(p["foto"])}" alt="{esc(p["nome"])}" loading="lazy" data-initials="{esc(iniziali(p["nome"]))}">'
                if p.get('foto') else f'<span class="avatar-fallback" aria-hidden="true">{esc(iniziali(p["nome"]))}</span>')
        ruolo = p.get('ruolo') or 'Staff'
        segno = '' if p.get('stato') == 'confermato' else '<span class="pallino" title="Ufficio da confermare"></span>'
        return f"""        <div class="person">
          <div class="photo">{foto}</div>
          <h3>{esc(p['nome'])}</h3>
          <div class="role">{esc(ruolo)}{segno}</div>
        </div>"""

    gruppi = ''
    for gr in organi:
        voci = ''.join(f"""          <div class="body-card">
            <h3>{esc(v['nome'])}</h3>
            {f'<p class="titolare">{esc(v["persona"])}</p>' if v.get('persona') else ''}
            <p>{esc(v['testo'])}</p>
          </div>""" for v in gr['voci'])
        gruppi += f"""
      <section class="people-section">
        <h3>{esc(gr['titolo'])}</h3>
        <div class="bodies">{voci}</div>
      </section>"""

    corpo = f"""{intestazione('Staff e organi di ateneo', 'Persone',
        "Chi fa funzionare l'Istituto ogni giorno, e gli organi che ne guidano la vita accademica e amministrativa.", None)}

<section>
  <div class="wrap">
    <section class="people-section" id="staff">
      <h2>Staff</h2>
      <p class="sub">Segreteria, amministrazione, biblioteca, progetti e servizi agli studenti.</p>
      <div class="people-grid">
{''.join(scheda(p) for p in staff)}
      </div>
    </section>
  </div>
</section>

<section style="background:var(--color-bg-alt)" id="organi">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Governance</p><h2>Organi di ateneo</h2>
    <p>Le autorità accademiche sono collegiali e personali. Composizione nominativa e testo integrale degli statuti restano nei documenti ufficiali.</p></div>
    {gruppi}
  </div>
</section>"""
    return pagina(0, 'Staff e organi di ateneo',
                  "Lo staff dell'Istituto Universitario Sophia e gli organi di ateneo: autorità personali, collegiali e organismi operativi.",
                  [('Home', 'index.html'), ('Staff e organi', None)], corpo,
                  sezione='istituto', corrente='staff.html')



# ------------------------------------------------- versione per la stampa

def genera_stampa(piano):
    """Documento A4 autonomo, da cui si ricava il PDF del piano di studi.
    Non dipende dal CSS del sito: gli stili sono qui dentro, pensati per
    la carta (nessuna ombra, nessuna animazione, interruzioni controllate).
    Si rende in PDF con:  node stampa/rendi-pdf.js"""
    import base64, os
    logo_b64 = ''
    p_logo = os.path.join(BASE, 'loghi', 'logosophiablue2023.png')
    if os.path.exists(p_logo):
        logo_b64 = base64.b64encode(open(p_logo, 'rb').read()).decode()

    n_ind = len(piano['indirizzi'])
    tot_ects = piano['indirizzi'][0]['totale_ects']
    n_anni = len(piano['indirizzi'][0]['anni'])
    sezioni = ''
    for i_ind, ind in enumerate(piano['indirizzi']):
        anni = ''
        for n, anno in enumerate(ind['anni'], 1):
            righe = ''
            for c in anno['corsi']:
                if c['esterno']:
                    doc = '<i>esame a UniPg</i>'
                elif c['docente']:
                    doc = esc(c['docente'].replace(';', ' ·'))
                else:
                    doc = '<span class="vuoto">—</span>'
                righe += f"""<tr>
        <td class="ects">{esc(c['ects'])}</td>
        <td class="corso">{esc(c['corso'])}</td>
        <td class="doc">{doc}</td>
        <td class="sem">{esc(c['semestre'])}</td>
        <td class="ssd">{esc(c['ssd'])}</td>
      </tr>"""
            anni += f"""
    <section class="anno">
      <h3>{ROMANI[n]} anno <span>{anno['totale_ects']} ECTS · {len(anno['corsi'])} insegnament{'o' if len(anno['corsi'])==1 else 'i'}</span></h3>
      <table>
        <thead><tr><th>ECTS</th><th>Insegnamento</th><th>Docente</th><th>Sem.</th><th>SSD</th></tr></thead>
        <tbody>{righe}</tbody>
      </table>
    </section>"""
        if ind['doppio_titolo']:
            _p = PARTNER.get(ind['doppio_titolo'], {})
            _logo = (f'<img class="marchio" src="../{_p["logo"]}" alt="">'
                     if _p.get('logo') else '')
            badge = (f'<p class="badge">{_logo}'
                     f'<span>Doppio titolo con l\'{esc(ind["doppio_titolo"])}'
                     + (f' · {esc(_p["sigla"])}' if _p.get('sigla') else '')
                     + '</span></p>')
        else:
            badge = '<p class="badge">Percorso interno a Sophia</p>' 
        sezioni += f"""
  <section class="indirizzo{' nuova-pagina' if i_ind else ''}">
    <div class="ind-testa">
      <div>
        <p class="occhiello">Indirizzo</p>
        <h2>{esc(ind['nome'])}</h2>
        {badge}
      </div>
      <p class="tot"><b>{ind['totale_ects']}</b><span>ECTS</span></p>
    </div>
    {anni}
  </section>"""

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<!-- copia per la stampa: resta fuori dagli indici anche dopo il lancio -->
<meta name="robots" content="noindex">
<title>{esc(piano['titolo'])} — Piano degli studi</title>
<style>
  @page {{ size:A4; margin:18mm 16mm 20mm }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  :root{{
    --navy:#152D3A; --oro:#F8B815; --indaco:#4A5180;
    --grigio:#696967; --linea:rgba(21,45,58,.14); --tenue:#EDEFF7;
    --titolo:Georgia,"Times New Roman",serif;
    --testo:"Helvetica Neue",Arial,sans-serif;
  }}
  body{{font-family:var(--testo);color:var(--navy);font-size:9.4pt;line-height:1.45;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
  h1,h2,h3{{font-family:var(--titolo);font-weight:400}}

  .copertina{{border-bottom:2.5pt solid var(--navy);padding-bottom:9mm;margin-bottom:8mm}}
  .copertina img{{height:16mm;margin-bottom:7mm}}
  .copertina .aa{{font-size:8pt;letter-spacing:.16em;text-transform:uppercase;color:var(--indaco);font-weight:600}}
  .copertina h1{{font-size:23pt;line-height:1.12;margin:2.5mm 0 3mm;max-width:16cm}}
  .copertina .sotto{{font-size:12pt;color:var(--grigio);font-family:var(--titolo)}}
  .copertina .premessa{{margin-top:5mm;font-size:9.6pt;color:#33414E;max-width:15.5cm}}

  .riepilogo{{display:flex;gap:4mm;margin:7mm 0 0}}
  .riepilogo div{{flex:1;background:var(--tenue);border-radius:2.5mm;padding:4mm 4.5mm}}
  .riepilogo b{{display:block;font-family:var(--titolo);font-size:15pt;line-height:1}}
  .riepilogo span{{display:block;margin-top:1.5mm;font-size:7.6pt;letter-spacing:.06em;text-transform:uppercase;color:var(--grigio)}}

  .indirizzo{{margin-top:9mm}}
  .nuova-pagina{{break-before:page;margin-top:0}}
  .ind-testa{{break-after:avoid;display:flex;justify-content:space-between;align-items:flex-end;
    border-bottom:1.6pt solid var(--navy);padding-bottom:3mm;margin-bottom:5mm}}
  .occhiello{{font-size:7.6pt;letter-spacing:.14em;text-transform:uppercase;color:var(--indaco);font-weight:600}}
  .ind-testa h2{{font-size:16pt;margin:1.5mm 0 2mm}}
  .badge{{display:inline-flex;align-items:center;gap:2.4mm;font-size:8pt;
    background:var(--oro);color:var(--navy);padding:1mm 3.4mm 1mm 1.4mm;
    border-radius:8mm;font-weight:600}}
  .badge .marchio{{height:7.5mm;width:auto;display:block}}
  .tot{{text-align:right;line-height:1}}
  .tot b{{font-family:var(--titolo);font-size:21pt}}
  .tot span{{display:block;font-size:7.4pt;letter-spacing:.1em;text-transform:uppercase;color:var(--grigio);margin-top:1mm}}

  /* l'anno può spezzarsi fra le pagine — se no una tabella lunga
     lascia mezza pagina bianca — ma non fra il titolo e la prima
     riga, e mai dentro una riga */
  .anno{{margin-top:6mm;break-inside:auto}}
  .anno h3{{break-after:avoid}}
  thead{{display:table-header-group}}
  tbody tr{{break-inside:avoid;break-after:auto}}
  .anno h3{{font-size:11.5pt;border-bottom:.6pt solid var(--linea);padding-bottom:1.6mm;margin-bottom:2mm;
    display:flex;justify-content:space-between;align-items:baseline}}
  .anno h3 span{{font-family:var(--testo);font-size:8.2pt;color:var(--grigio);letter-spacing:.02em}}

  table{{width:100%;border-collapse:collapse}}
  thead th{{font-size:7.2pt;letter-spacing:.08em;text-transform:uppercase;color:var(--grigio);
    font-weight:600;text-align:left;padding:1.4mm 2mm;border-bottom:.6pt solid var(--linea)}}
  tbody td{{padding:1.7mm 2mm;border-bottom:.4pt solid var(--linea);vertical-align:top}}
  tbody tr:nth-child(even) td{{background:#FAFBFD}}
  td.ects{{width:12mm;text-align:center;font-family:var(--titolo);font-size:11pt;line-height:1.1}}
  td.corso{{font-weight:600}}
  td.doc{{width:42mm;color:#33414E}}
  td.sem{{width:14mm;text-align:center;color:var(--grigio)}}
  td.ssd{{width:22mm;font-size:8pt;color:var(--grigio);white-space:nowrap}}
  td i{{color:var(--grigio)}}
  .vuoto{{color:#B9B9B7}}
  .vuoto{{color:#B9B9B7}}

  .nota{{margin-top:7mm;font-size:8.2pt;color:var(--grigio);border-top:.6pt solid var(--linea);padding-top:3mm}}
</style>
</head>
<body>

<header class="copertina">
  {f'<img src="data:image/png;base64,{logo_b64}" alt="Istituto Universitario Sophia">' if logo_b64 else ''}
  <p class="aa">Anno accademico 2026/2027 · {esc(piano['meta']['breve'])}</p>
  <h1>{esc(piano['titolo'])}</h1>
  <p class="sotto">{esc(piano['sottotitolo'])}</p>
  <p class="premessa">{esc(piano['premessa'])}</p>
  <div class="riepilogo">
    <div><b>{n_ind}</b><span>{'Percorsi' if n_ind > 1 else 'Percorso'}</span></div>
    <div><b>{tot_ects}</b><span>ECTS per percorso</span></div>
    <div><b>{n_anni}</b><span>Anni</span></div>
    <div><b>2</b><span>Titoli: ecclesiastico e statale</span></div>
  </div>
</header>
{sezioni}

<p class="nota">Istituto Universitario Sophia · Via San Vito 28, 50064 Figline e Incisa Valdarno (FI) ·
info@sophiauniversity.org · sophiauniversity.org — I corsi contrassegnati «esame a UniPg» si sostengono
presso l'Università degli Studi di Perugia nell'ambito della convenzione di doppio titolo.</p>

</body>
</html>"""


# --------------------------------------------------------------------- main

def genera_404():
    """Pagina per gli indirizzi che non esistono più o sbagliati.
    I collegamenti sono relativi: il <base> qui sotto li fa funzionare sia sul
    dominio vero sia sull'anteprima di GitHub Pages, che vive in sottocartella."""
    corpo = '''<section class="page-hero">
  <div class="rombo pr1"></div><div class="rombo pr2"></div>
  <div class="wrap">
    <p class="eyebrow light">Errore 404</p>
    <h1>Questa pagina non c'è</h1>
    <p>L'indirizzo è cambiato, oppure c'è un refuso. Da qui puoi ripartire.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="cards c3">
      <a class="card" href="offerta.html"><h3>Offerta formativa</h3>
        <p>Baccalaureato, Licenza magistrale, dottorato e percorsi brevi.</p></a>
      <a class="card" href="ammissione.html"><h3>Ammissione</h3>
        <p>Come si entra a Sophia, scadenze e documenti.</p></a>
      <a class="card" href="contatti.html"><h3>Contatti</h3>
        <p>Le due sedi, i recapiti e il modulo per scriverci.</p></a>
    </div>
    <p style="margin-top:30px"><a class="btn btn-navy" href="index.html">Torna alla home</a></p>
  </div>
</section>'''
    h = pagina(0, 'Pagina non trovata',
               "La pagina cercata non esiste più o l'indirizzo è sbagliato: riparti da qui.",
               [('Home', 'index.html'), ('Pagina non trovata', None)], corpo)
    base = ("<script>document.write('<base href=\"'+"
            "(location.pathname.indexOf('/sito-sophia/')===0?'/sito-sophia/':'/')+'\">')</script>")
    h = h.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n' + base, 1)
    # la pagina d'errore non va indicizzata mai, nemmeno dopo il lancio
    if 'name="robots"' in h:
        h = h.replace('<meta name="robots" content="noindex, nofollow">',
                      '<meta name="robots" content="noindex">', 1)
    else:
        h = h.replace('<meta charset="UTF-8">',
                      '<meta charset="UTF-8">\n<meta name="robots" content="noindex">', 1)
    return h


def main():
    piani, corsi, docenti, categorie, staff, organi = carica()
    os.makedirs(os.path.join(BASE, 'corsi'), exist_ok=True)
    os.makedirs(os.path.join(BASE, 'docenti'), exist_ok=True)

    scritti = 0
    def scrivi(percorso, contenuto):
        nonlocal scritti
        contenuto = sistema(contenuto, percorso)
        with open(os.path.join(BASE, percorso), 'w', encoding='utf-8') as f:
            f.write(contenuto)
        scritti += 1

    os.makedirs(os.path.join(BASE, 'stampa'), exist_ok=True)
    for piano in piani:
        scrivi(piano['meta']['pagina'], genera_piano(piano, corsi, docenti))
        scrivi('stampa/' + piano['meta']['pagina'], genera_stampa(piano))
    for piano in piani:
        if piano['meta']['chiave'] != 'baccalaureato':
            continue
        for ind in piano['indirizzi']:
            if ind['nome'] in INDIRIZZI_PAGINA:
                scrivi(INDIRIZZI_PAGINA[ind['nome']]['file'],
                       genera_indirizzo(piano, ind, corsi, docenti))
    scrivi('404.html', genera_404())
    scrivi('corsi/index.html', genera_indice_corsi(corsi))
    scrivi('docenti.html', genera_indice_docenti(docenti, categorie))
    scrivi('staff.html', genera_staff(staff, organi))
    for c in corsi.values():
        scrivi(f'corsi/{c["slug"]}.html', genera_corso(c))
    for d in docenti.values():
        scrivi(f'docenti/{d["slug"]}.html', genera_docente(d))

    print(f'{scritti} pagine generate')
    print(f'  {len(piani)} piani di studio · {len(corsi)} insegnamenti · {len(docenti)} docenti · staff e organi')

if __name__ == '__main__':
    main()
