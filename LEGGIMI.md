# Sito Sophia — versione consolidata

Aggiornamento del 7 agosto 2026. Sostituisce i file precedenti in `[8] Sito Web`.

## Che cosa è cambiato

### Livello A dell'audit — chiuso

| Difetto | Stato |
|---|---|
| A1 · `sophia-site.css` sovrascriveva i token | risolto: il blocco `:root` di fallback è stato eliminato, tutti i token stanno in `sophia-tokens.css` e i componenti usano i ruoli semantici `--color-*` |
| A2 · contrasti sotto la soglia AA | risolto: l'oro è ora solo colore di superficie, l'inchiostro dei link è l'indaco di manuale. **0 violazioni** su 12 pagine, misurate elemento per elemento nel browser |
| A3 · fallback delle foto profilo | risolto: si controlla anche `complete && naturalWidth===0`. Da 10 su 21 a **21 su 21** |
| A5 · modulo contatti | risolto: `action`/`method`, campi `name`, `required`, casella di consenso, trappola anti-spam. Rimosso `onsubmit="return false"` |
| A6 · ancore coperte dall'header | risolto: `scroll-padding-top: 92px` |

### Anche chiusi, dai livelli B e C

- Header e footer: da 7 e 6 varianti a **una sola**
- Un unico percorso di iscrizione: `studiare.html#ammissione`
- `<main>`, skip link, `aria-label` sui `<nav>`, `:focus-visible`, nessun `h4` orfano
- Voce di menu attiva via `aria-current`, calcolata dallo script su tutte le 12 pagine
- Il CTA "Iscriviti" resta visibile su mobile
- `og:`, `canonical`, `hreflang`, favicon, JSON-LD `CollegeOrUniversity`
- Email cliccabili; zero `href="#"`; zero link rotti
- I componenti locali di `news.html` e `studiare.html` sono nel foglio condiviso
- Stampa: il contenuto rivelato allo scroll resta visibile
- Pagine legali create come segnaposto strutturati: `privacy.html`, `cookie.html`, `note-legali.html`
- `en/index.html`: pagina ponte in inglese, così il selettore di lingua non è più finto

## Struttura

```
sophia-tokens.css   unica sorgente dei valori. Ogni token porta annotato
                    il proprio rapporto di contrasto: va riverificato a
                    ogni modifica.
sophia-site.css     solo componenti. Non dichiara variabili.
sophia-site.js      menu, video hero, comparsa allo scroll, contatori,
                    filtro persone, fallback avatar.
media/              hero-sophia.*  = loop di 6,7 s montato da tre spezzoni
                                     del video istituzionale (gli unici privi
                                     di sottotitoli impressi). Sorgente a
                                     640x360: da rigirare quando possibile.
                    placeholder-*  = immagini segnaposto, da sostituire
```

## Prima della messa online — non rinviabile

1. **Scrivere l'informativa privacy.** Finché è un segnaposto il modulo contatti non va pubblicato.
2. **Sostituire `action="/moduli/richiesta-informazioni"`** con l'endpoint reale.
3. **Scaricare i 21 ritratti** da `sophiauniversity.org` e servirli localmente, in WebP, con `width`/`height`.
4. **Verificare i due dati contrassegnati `[da verificare]`** nella fascia numeri della home.
5. **Sostituire i media provvisori** con le riprese e le fotografie vere.

## Resta aperto

- Nessun sistema di build: header e footer sono di nuovo copiati in 15 file. Sono allineati **oggi**; divergeranno alla prossima modifica fatta a mano. È il punto B1 dell'audit e la ragione per cui la Fase 2 conta.
- 144 attributi `style=""` inline.
- Contenuti obbligatori ancora assenti: statuti, regolamenti, calendario accademico, piani di studio, rette.


## Il video dell'hero non parte?

**Apri `diagnostica-video.html`** con lo stesso browser: elenca una per una le
condizioni e dice quale non è soddisfatta.

La causa più frequente è il protocollo. Aprendo `index.html` con un doppio clic
dal Finder l'indirizzo è `file://`, e Safari — in parte anche Chrome — limita la
riproduzione dei video letti così. Per provare in locale nelle condizioni giuste:

    cd "percorso/sito-sophia" && python3 -m http.server 8000

poi `http://localhost:8000`. Online il problema non si presenta.

Le altre condizioni sono volute, non guasti: il video non viene caricato se la
riduzione del movimento è attiva nel sistema, se la finestra è sotto 860 px, o
se il browser dichiara una connessione lenta o a consumo. In tutti questi casi
resta il fotogramma fisso e la pagina funziona identica.

Se l'avvio automatico viene negato dal browser, in basso a destra compare il
pulsante **▶ Riproduci**: non si resta mai davanti a un fotogramma morto.



## Hero: il video con la maschera

Il montaggio dura **62 secondi** e mette insieme **28 spezzoni** presi a
intervalli regolari lungo tutta la durata del video istituzionale, dal secondo
20 al 256. Nessuna selezione a mano: compaiono anche tratti d'intervista, e va
bene così.

Il ritaglio tiene il **78% superiore** del fotogramma. Serve a togliere due cose
impresse nell'immagine della sorgente: i sottotitoli inglesi (y 320–334, cioè
fra l'89% e il 93% dell'altezza) e le didascalie con i nomi dei relatori, che
stanno più in alto. Senza quel taglio comparirebbero dietro al titolo.

**La maschera resta.** Non è un vezzo: misurata su 63 fotogrammi lungo l'intero
ciclo, senza schermatura il titolo bianco scende a 1,0–1,3:1 di contrasto sul
girato in esterni, cioè sparisce. I valori attuali della sfumatura sono tarati
su questo montaggio:

| zona | contrasto peggiore | soglia | margine |
|---|---:|---:|---:|
| occhiello | 5,57 | 4,5 | +1,07 |
| titolo bianco | 9,39 | 3,0 | +6,39 |
| titolo oro | 6,11 | 3,0 | +3,11 |
| testo di apertura | 9,84 | 4,5 | +5,34 |
| bordo del pulsante | 15,02 | 3,0 | +12,02 |

Se si tocca `.hero-veil` in `sophia-site.css`, o se si sostituisce il video,
**va rimisurato tutto il ciclo**: è l'unico modo per sapere se il titolo resta
leggibile nei fotogrammi più chiari.

**Peso**: 3,2 MB (MP4) e 4,3 MB (WebM) a 1152×562. Su schermi sotto 860 px il
file non viene scaricato affatto.

## Piano degli studi, insegnamenti, docenti — generati dai dati

Il piano del Baccalaureato, le 40 schede degli insegnamenti e le 9 schede dei
docenti **non si scrivono a mano**: si generano da `dati/piano-baccalaureato.json`.

```bash
python3 genera.py
```

Produce `piano-baccalaureato.html`, `corsi/` (indice + una scheda per
insegnamento) e `docenti/` (indice + una scheda per docente): **52 pagine**.

La ragione è la stessa per cui header e footer erano divergenti: piano, schede
corso e schede docente raccontano gli stessi fatti da tre punti di vista. Se un
insegnamento cambia crediti e lo si corregge solo nel piano, le altre due pagine
mentono. Qui la sorgente è una sola. Non modificare a mano i file dentro
`corsi/` e `docenti/`: al prossimo `genera.py` le modifiche vengono sovrascritte.

### Dati verificati

Estratti dal PDF `PianodistudioBaccalaureato.pdf`. La tabella del PDF usa un font
con la codifica difettosa — ogni `a` esce come `à`, e `é`/`ó` escono come lettera
più spazio — quindi il testo è stato ripulito in fase di estrazione. Controllo
fatto: **tutti e tre gli indirizzi sommano esattamente 180 ECTS**, e per ciascun
anno la somma dei crediti coincide con il totale dichiarato nel PDF.

### Ciò che manca, ed è dichiarato

Le schede riportano solo i dati che il PDF contiene davvero: crediti, semestre,
settore, docente, in quali indirizzi e anni compare l'insegnamento. Obiettivi
formativi, contenuti, modalità di verifica e bibliografia **non sono inventati**:
compaiono come riquadri tratteggiati con la dicitura «non ancora compilata».
Lo stesso vale per i profili dei docenti.

Sono 40 schede corso × 4 sezioni e 9 profili: conviene raccoglierli con un modulo
inviato ai docenti, non a voce.




## Persone: due pagine, generate dai dati

`persone.html` non esiste più. Al suo posto:

- **`docenti.html`** — i 36 docenti divisi nelle sette categorie, con barra di
  ancore in alto. Ogni scheda porta alla pagina personale in `docenti/<nome>.html`.
- **`staff.html`** — le 12 persone dello staff e gli organi di ateneo
  (autorità personali, collegiali, organismi operativi), all'ancora `#organi`.

Tutti i collegamenti che puntavano a `persone.html` sono stati riportati sulle
nuove pagine; il menu ha ora le voci **Docenti** e **Staff**.

### Sorgenti

| File | Contenuto | Provenienza |
|---|---|---|
| `dati/piano-baccalaureato.json` | piano di studi | `PianodistudioBaccalaureato.pdf` |
| `dati/docenti.json` | 36 docenti in 7 categorie | pagina docenti ufficiale, 8 agosto 2026 |
| `dati/staff.json` | 12 persone | pagina staff ufficiale, 8 agosto 2026 |
| `dati/organi.json` | organi di ateneo | pagina organi di ateneo, 8 agosto 2026 |

Le categorie dei docenti e i loro numeri (stabili 6, incaricati 3, invitati 3,
ricercatori 8, visiting 4, emeriti 10) corrispondono a quelli del sito attuale.
La settima, «Docenti a contratto», non esiste nel sito attuale: raccoglie Irene
Severi e Cecilia Ricci, titolari di insegnamento nel Baccalaureato ma assenti
dall'elenco pubblico.

### Marchio dell'ateneo convenzionato

`loghi/logo-unipg.png` è lo stemma dell'Università degli Studi di Perugia
(220x220, fondo trasparente), ritagliato dal lockup ufficiale fornito
dall'ateneo. Compare nei tre percorsi in doppio titolo — due indirizzi del
Baccalaureato e il percorso in doppio titolo della Licenza — sia a schermo
sia nei PDF dei piani, con collegamento a https://fissuf.unipg.it/.
Il nome esteso dell'ateneo è composto in tipografia accanto allo stemma:
il lockup completo non e' stato usato perche' l'unico file disponibile
ha la parte tipografica tagliata sul margine destro. Se arriva il lockup
integro, si sostituisce l'immagine e si toglie il testo in `partner()`
dentro `genera.py`.

### Cosa resta da confermare

La pagina staff ufficiale non indica l'ufficio di ciascuno: solo cinque persone
su dodici hanno un ruolo attribuito, ricavato dalla bozza precedente e dalla
pagina Organi di ateneo. Le altre sette portano l'etichetta generica «Staff» con
un pallino oro. Si correggono in `dati/staff.json`.

Le descrizioni degli organi sono riassunte, non copiate: la composizione
nominativa e il testo integrale restano negli statuti.

**Non modificare a mano** `docenti.html`, `staff.html`, `piano-baccalaureato.html`
e le cartelle `corsi/` e `docenti/`: si rigenerano tutte con `python3 genera.py`.

## Piani di studio: due, generati dagli stessi dati

| Sorgente | Pagina | PDF |
|---|---|---|
| `dati/piano-baccalaureato.json` | `piano-baccalaureato.html` | `media/Piano-di-studi-Baccalaureato.pdf` |
| `dati/piano-licenza.json` | `piano-licenza.html` | `media/Piano-di-studi-Licenza-magistrale.pdf` |

Da entrambi nascono anche le schede in `corsi/` (63 insegnamenti) e gli
insegnamenti che compaiono nelle schede docente.

### Rigenerare il PDF

`genera.py` scrive la versione per la stampa in `stampa/`. Il PDF si ottiene da
lì con Chromium:

```bash
python3 genera.py
node rendi-pdf.js
```

`rendi-pdf.js` richiede Playwright (`npm i playwright`). Il documento per la
stampa è autonomo: non usa il CSS del sito, ha il proprio foglio di stile pensato
per la carta (A4, nessuna ombra, intestazioni di tabella ripetute a ogni pagina,
interruzioni mai dentro una riga).

### Dati verificati

Estratti dai due PDF originali, la cui tabella usa un font con la codifica
difettosa (ogni `a` esce come `à`). Controllo fatto:

- Baccalaureato: i tre indirizzi sommano **180 ECTS** ciascuno
- Licenza magistrale: entrambi i percorsi sommano **120 ECTS**

e in ogni anno la somma dei crediti coincide con il totale dichiarato nel PDF.

### Titolarità non ancora assegnate

Nel piano della Licenza cinque insegnamenti sono attribuiti a «Docente di
Economia» e uno a «Contrattista». Non sono persone: non generano una pagina
docente e non sono collegati. Nelle schede corso compare una nota esplicita.
