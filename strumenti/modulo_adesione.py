# -*- coding: utf-8 -*-
"""Genera il modulo di adesione della Fondazione «Per Sophia» ETS come PDF
compilabile (AcroForm). Lo stesso file serve due scopi:
  · scaricato in bianco, si compila a mano o sul computer;
  · usato come modello dal sito, che lo precompila nel browser con pdf-lib.
I nomi dei campi qui sotto sono gli stessi usati da sophia-modulo.js.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

USCITA = "media/Modulo-di-adesione-Fondazione-per-Sophia.pdf"

LARG, ALT = A4
SX, DX = 54.0, 541.0          # margini in punti
CORPO = "Times-Roman"
GRASSETTO = "Times-Bold"
CORSIVO = "Times-Italic"
FS = 9.2                      # corpo del testo
INTER = 14.6                  # interlinea
INCHIOSTRO = colors.HexColor("#1A2530")
FILO = colors.HexColor("#4A5560")
TINTA = colors.HexColor("#F1F4F9")   # fondo tenue dei campi, quasi bianco in stampa

c = canvas.Canvas(USCITA, pagesize=A4)
c.setTitle("Modulo di adesione — Fondazione «Per Sophia» ETS")
c.setAuthor("Fondazione «Per Sophia» ETS")
c.setFillColor(INCHIOSTRO)
c.setStrokeColor(FILO)


def larghezza(s, font=CORPO, size=FS):
    return stringWidth(s, font, size)


def campo(nome, x, y, larg, alt=12.0, maxlen=120):
    """Campo di testo con la sola riga di base, come un modulo cartaceo."""
    c.acroForm.textfield(
        name=nome, x=x, y=y - 3.0, width=larg, height=alt,
        borderStyle="underlined", borderWidth=0.7, borderColor=FILO,
        fillColor=TINTA, forceBorder=True, textColor=INCHIOSTRO,
        fontName="Helvetica", fontSize=8.8, maxlen=maxlen,
        annotationFlags="print", relative=False,
    )
    return x + larg + 2.5


def casella(nome, x, y, lato=9.0):
    c.acroForm.checkbox(
        name=nome, x=x, y=y - 1.0, size=lato, checked=False,
        buttonStyle="check", borderWidth=0.7, borderColor=FILO,
        fillColor=TINTA, textColor=INCHIOSTRO, forceBorder=True,
        annotationFlags="print", relative=False,
    )
    return x + lato + 5.0


def riga(y, pezzi, x=SX, size=FS):
    """pezzi: ('t', testo, font) oppure ('c', nome, larghezza)."""
    cur = x
    for p in pezzi:
        if p[0] == "t":
            c.setFont(p[2], size)
            c.drawString(cur, y, p[1])
            cur += larghezza(p[1], p[2], size)
        else:
            cur = campo(p[1], cur, y, p[2])
    if cur > DX + 0.5:
        raise SystemExit("riga oltre il margine destro (%.1f > %.1f): %r" % (cur, DX, pezzi))
    return cur


def paragrafo(y, testo, font=CORPO, size=FS, x=SX, destra=DX, lead=None):
    lead = lead or (size + 3.4)
    c.setFont(font, size)
    parole, linea = testo.split(), ""
    for w in parole:
        prova = (linea + " " + w).strip()
        if larghezza(prova, font, size) > (destra - x):
            c.drawString(x, y, linea)
            y -= lead
            linea = w
        else:
            linea = prova
    if linea:
        c.drawString(x, y, linea)
        y -= lead
    return y


def sezione(y, testo):
    c.setFont(GRASSETTO, FS + 0.4)
    c.drawString(SX, y, testo)
    c.setLineWidth(0.6)
    c.line(SX, y - 2.2, SX + larghezza(testo, GRASSETTO, FS + 0.4), y - 2.2)
    return y - INTER


def riga_a_mano(y, etichetta_sx, larg_sx, etichetta_dx, larg_dx):
    c.setFont(CORPO, FS)
    c.drawString(SX, y, etichetta_sx)
    x = SX + larghezza(etichetta_sx) + 4
    c.setLineWidth(0.7)
    c.line(x, y - 2.5, x + larg_sx, y - 2.5)
    xd = SX + 300
    c.drawString(xd, y, etichetta_dx)
    xd += larghezza(etichetta_dx) + 4
    c.line(xd, y - 2.5, xd + larg_dx, y - 2.5)
    return y - INTER


# ─────────────────────────── intestazione ───────────────────────────
y = ALT - 52

c.setFont(CORPO, 10)
testa = "Spett.le "
c.drawRightString(DX - larghezza("Fondazione «Per Sophia» ETS", GRASSETTO, 10), y, testa)
c.setFont(GRASSETTO, 10)
c.drawRightString(DX, y, "Fondazione «Per Sophia» ETS")
y -= 26

titolo = "MODULO DI ADESIONE"
c.setFont(GRASSETTO, 12.5)
c.drawCentredString(LARG / 2, y, titolo)
lt = larghezza(titolo, GRASSETTO, 12.5)
c.setLineWidth(0.7)
c.line((LARG - lt) / 2, y - 2.6, (LARG + lt) / 2, y - 2.6)
y -= 24

y = paragrafo(
    y,
    "• Presa visione e preso atto delle caratteristiche, delle finalità e, in generale, "
    "della missione della Fondazione «Per Sophia» ETS, così come enunciate nello statuto, "
    "che dichiaro di ben conoscere e accettare;",
)
y -= 9

# ─────────────────────────── dati personali ───────────────────────────
riga(y, [("t", "Il sottoscritto ", GRASSETTO), ("c", "nome_cognome", 196),
         ("t", " nato a ", CORPO), ("c", "nato_a", 118),
         ("t", " il ", CORPO), ("c", "nato_il", 62)])
y -= INTER
riga(y, [("t", "residente in ", CORPO), ("c", "residenza", 150),
         ("t", " prov. ", CORPO), ("c", "provincia", 34),
         ("t", " nazione ", CORPO), ("c", "nazione", 96),
         ("t", " c.a.p. ", CORPO), ("c", "cap", 42)])
y -= INTER
riga(y, [("t", "indirizzo ", CORPO), ("c", "via", 184),
         ("t", " n. ", CORPO), ("c", "civico", 38),
         ("t", " codice fiscale ", CORPO), ("c", "codice_fiscale", 128)])
y -= INTER
riga(y, [("t", "n. di telefono ", CORPO), ("c", "telefono", 130),
         ("t", " e-mail ", CORPO), ("c", "email", 210)])
y -= INTER + 5

c.setFont(CORSIVO, FS)
c.drawString(SX, y, "(solo in caso di enti, ecc.)")
y -= INTER

riga(y, [("t", "in qualità di ", CORPO), ("c", "ruolo_ente", 150),
         ("t", " dell'ente ", CORPO), ("c", "ente", 220)])
y -= INTER
riga(y, [("t", "con sede in ", CORPO), ("c", "sede_ente", 150),
         ("t", " prov. ", CORPO), ("c", "provincia_ente", 34),
         ("t", " nazione ", CORPO), ("c", "nazione_ente", 92),
         ("t", " c.a.p. ", CORPO), ("c", "cap_ente", 42)])
y -= INTER
riga(y, [("t", "indirizzo ", CORPO), ("c", "via_ente", 106),
         ("t", " n. ", CORPO), ("c", "civico_ente", 30),
         ("t", " codice fiscale ", CORPO), ("c", "cf_ente", 96),
         ("t", " partita IVA ", CORPO), ("c", "piva_ente", 84)])
y -= INTER + 8

# ─────────────────────────── quota ───────────────────────────
y = sezione(y, "sottoscrive la quota di:")

def blocco_quota(y, casella_nome, etichetta, minimo, campo_imp, campo_anni):
    x = casella(casella_nome, SX, y)
    c.setFont(GRASSETTO, FS)
    c.drawString(x, y, etichetta)
    x += larghezza(etichetta, GRASSETTO)
    coda = " (quota annuale minima di € %s): € " % minimo
    c.setFont(CORPO, FS)
    c.drawString(x, y, coda)
    x += larghezza(coda)
    campo(campo_imp, x, y, 120)
    y -= INTER
    testo = "da versare nei seguenti anni: "
    c.setFont(CORPO, FS)
    c.drawString(SX + 24, y, testo)
    campo(campo_anni, SX + 24 + larghezza(testo), y, 230)
    return y - (INTER + 3)

y = blocco_quota(y, "quota_sovventore", "«Partecipante Sovventore»", "10.000,00",
                 "importo_sovventore", "anni_sovventore")
y = blocco_quota(y, "quota_aderente", "«Partecipante Aderente»", "500,00",
                 "importo_aderente", "anni_aderente")

x = casella("quota_contribuente", SX, y)
c.setFont(GRASSETTO, FS)
c.drawString(x, y, "Contribuente")
x += larghezza("Contribuente", GRASSETTO)
coda = " (ai sensi dell'art. 4 dello statuto: è possibile versare contributi senza il ruolo di Partecipante): € "
c.setFont(CORPO, FS)
c.drawString(x, y, coda)
campo("importo_contribuente", x + larghezza(coda), y, 74)
y -= INTER
testo = "da versare nei seguenti anni: "
c.setFont(CORPO, FS)
c.drawString(SX + 24, y, testo)
campo("anni_contribuente", SX + 24 + larghezza(testo), y, 230)
y -= INTER + 8

# ─────────────────────────── destinazione ───────────────────────────
y = sezione(y, "che viene destinata, ai sensi dell'atto costitutivo e dello statuto della Fondazione:")

x = casella("destina_gestione", SX, y)
y = paragrafo(
    y,
    "a far fronte alle spese inerenti la gestione ordinaria della Fondazione e alle attività "
    "indicate nell'art. 2 dello statuto",
    font=GRASSETTO, x=x, destra=DX,
)
y = paragrafo(
    y,
    "(sostegno delle attività di studio e di ricerca realizzate presso l'Istituto Universitario "
    "Sophia, finanziamento di iniziative promozionali e di ricerca nei campi di interesse "
    "dell'Istituto, finanziamento di progetti culturali e didattici e delle spese di gestione "
    "dell'Istituto stesso, ecc.).",
    x=x, destra=DX,
)
y -= 3
y = paragrafo(
    y,
    "Il sottoscritto richiede, altresì, che la propria contribuzione venga finalizzata al "
    "perseguimento di specifici obiettivi e/o progetti di particolare rilevanza rientranti nelle "
    "finalità di cui all'art. 2 dello statuto:",
    x=x, destra=DX,
)
campo("obiettivi_specifici", x, y - 1, DX - x, maxlen=220)
y -= INTER + 6

x = casella("destina_patrimonio", SX, y)
c.setFont(GRASSETTO, FS)
c.drawString(x, y, "al patrimonio.")
y -= INTER + 12

# ─────────────────────────── firme e privacy ───────────────────────────
y = riga_a_mano(y, "Luogo e data", 150, "Firma", 190)
y -= 4
y = paragrafo(
    y,
    "Il sottoscritto autorizza il trattamento dei dati personali contenuti nel presente modulo "
    "di adesione ai sensi del Regolamento (UE) 2016/679 (GDPR) e del D. Lgs. 196/2003, come "
    "modificato dal D. Lgs. 101/2018, per lo svolgimento e la gestione delle attività legate "
    "agli scopi della Fondazione, e dichiara di essere a conoscenza che i dati personali forniti "
    "saranno trattati conformemente a tali disposizioni.",
    size=8.4, lead=11.2,
)
y -= 5
y = riga_a_mano(y, "Luogo e data", 150, "Firma", 190)
y -= 8

# ─────────────────────────── istruzioni ───────────────────────────
c.setLineWidth(1.1)
c.setStrokeColor(colors.HexColor("#152D3A"))
c.line(SX, y, DX, y)
c.setStrokeColor(FILO)
y -= 15

t = "Istruzioni per il versamento e per l'invio del presente modulo"
c.setFont(GRASSETTO, 9.4)
c.drawCentredString(LARG / 2, y, t)
lt = larghezza(t, GRASSETTO, 9.4)
c.setLineWidth(0.6)
c.line((LARG - lt) / 2, y - 2.4, (LARG + lt) / 2, y - 2.4)
y -= 16

c.setFont(GRASSETTO, 8.6)
c.drawString(SX, y, "Bonifico bancario")
c.setFont(CORPO, 8.6)
c.drawString(SX + larghezza("Bonifico bancario", GRASSETTO, 8.6), y,
             " a favore di: Fondazione «Per Sophia» ETS, Località Burchio c/o Polo Lionello Bonfanti,")
y -= 11.4
y = paragrafo(y, "50064 Figline e Incisa Valdarno (FI) — IBAN IT52 I050 1802 8000 0001 1307 055 — BIC CCRTIT2T84A "
                 "(Banca Popolare Etica, Filiale di Firenze, via Dell'Agnolo 73/R). In alternativa, conto corrente "
                 "postale n. 1011096771, stessa intestazione.", size=8.6, lead=11.4)
y -= 3
c.setFont(GRASSETTO, 8.6)
c.drawString(SX, y, "Il presente modulo dovrà essere inviato:")
y -= 11.4
c.setFont(CORPO, 8.6)
c.drawString(SX, y, "– a mezzo e-mail all'indirizzo fondazione@sophiauniversity.org, allegando copia dell'avvenuto versamento;")
y -= 11.4
c.drawString(SX, y, "– a mezzo posta a: Fondazione «Per Sophia» ETS, Località Burchio c/o Polo Lionello Bonfanti,")
y -= 11.4
c.drawString(SX, y, "   50064 Figline e Incisa Valdarno (FI).")

c.showPage()
c.save()
print("scritto", USCITA, "· ultima y:", round(y, 1))
