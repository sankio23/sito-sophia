# -*- coding: utf-8 -*-
"""Le due mail della Fondazione «Per Sophia» ETS: quella per chi aderisce e
quella interna. Questo file serve per le prove e per le anteprime; in
produzione lo stesso markup vive dentro FondazioneBackend.gs (Apps Script)."""

BAND = "https://sankio23.github.io/sito-sophia/email/band-fondazione.png"
SITO = "https://sankio23.github.io/sito-sophia/fondazione/index.html"

NAVY   = "#152D3A"
ORO    = "#F8B815"
OROCUP = "#8A7014"
TESTO  = "#2B3A45"
FIOCO  = "#6B7885"
FILO   = "#E3E8EF"
FONDO  = "#EEF1F6"
TENUE  = "#F6F8FB"

SERIF = "Georgia,'Times New Roman',Times,serif"
SANS  = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"


def _righe(voci):
    out = []
    for i, (etichetta, valore) in enumerate(voci):
        if not valore:
            continue
        bordo = "" if i == 0 else "border-top:1px solid %s;" % FILO
        out.append(
            '<tr>'
            '<td style="%spadding:11px 0 11px 22px;font:400 13px %s;color:%s;width:42%%;vertical-align:top">%s</td>'
            '<td style="%spadding:11px 22px 11px 12px;font:600 14px %s;color:%s;vertical-align:top">%s</td>'
            '</tr>' % (bordo, SANS, FIOCO, etichetta, bordo, SANS, NAVY, valore)
        )
    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%%" '
        'style="background:%s;border-left:3px solid %s;border-radius:0 8px 8px 0">%s</table>'
        % (TENUE, ORO, "".join(out))
    )


def _guscio(occhiello, titolo, corpo_html):
    return f"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titolo}</title></head>
<body style="margin:0;padding:0;background:{FONDO};-webkit-text-size-adjust:100%">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:{FONDO}">
<tr><td align="center" style="padding:30px 12px">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640"
         style="width:640px;max-width:100%;background:#FFFFFF;border:1px solid {FILO};border-radius:14px;overflow:hidden">
    <tr><td style="line-height:0;font-size:0">
      <img src="{BAND}" width="640" alt="Fondazione per Sophia ETS"
           style="display:block;width:100%;max-width:640px;height:auto;border:0">
    </td></tr>
    <tr><td style="padding:36px 44px 0">
      <p style="margin:0 0 14px;font:600 11px {SANS};letter-spacing:.16em;text-transform:uppercase;color:{OROCUP}">{occhiello}</p>
      <h1 style="margin:0 0 20px;font:400 29px/1.22 {SERIF};color:{NAVY}">{titolo}</h1>
    </td></tr>
    {corpo_html}
    <tr><td style="padding:14px 44px 40px">
      <p style="margin:0;font:400 15px/1.7 {SANS};color:{TESTO}">Con gratitudine,<br>
      <b style="color:{NAVY}">La Fondazione «Per Sophia» ETS</b></p>
    </td></tr>
  </table>
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640" style="width:640px;max-width:100%">
    <tr><td style="padding:20px 24px 6px;font:400 12px/1.7 {SANS};color:{FIOCO};text-align:center">
      Fondazione «Per Sophia» ETS · Codice fiscale 94177760488<br>
      Sede legale: Loc. Burchio, c/o Polo Lionello Bonfanti — 50064 Figline e Incisa Valdarno (FI)<br>
      Tel. +39 055 9051515 · <a href="mailto:fondazione@sophiauniversity.org" style="color:{FIOCO}">fondazione@sophiauniversity.org</a> ·
      <a href="{SITO}" style="color:{FIOCO}">sophiauniversity.org</a>
    </td></tr>
  </table>
</td></tr></table>
</body></html>"""


def _p(testo, extra=""):
    return '<p style="margin:0 0 16px;font:400 15px/1.7 %s;color:%s;%s">%s</p>' % (SANS, TESTO, extra, testo)


def mail_aderente(d):
    """d: nome, cognome, tipo, importo, anni, destinazione, obiettivo, data, ente"""
    nome = d.get("nome", "")
    voci = [
        ("Tipo di adesione", d.get("tipo_esteso") or d.get("tipo")),
        ("Importo annuo", ("%s €" % d["importo"]) if d.get("importo") else ""),
        ("Anni di versamento", d.get("anni")),
        ("Destinazione", d.get("destinazione")),
        ("Progetto indicato", d.get("obiettivo")),
        ("Per conto di", d.get("ente")),
        ("Richiesta ricevuta il", d.get("data")),
    ]
    passi = [
        ("1", "Firma il modulo", "Apri il PDF allegato — è già compilato con i tuoi dati. Aggiungi <b>luogo, data e firma</b> nei due spazi previsti."),
        ("2", "Effettua il versamento", "Con le coordinate qui sotto, indicando come causale il tuo nome e «adesione alla Fondazione»."),
        ("3", "Rispediscilo", 'Manda il modulo firmato e la ricevuta del versamento a <a href="mailto:fondazione@sophiauniversity.org" style="color:%s">fondazione@sophiauniversity.org</a>, oppure per posta alla sede legale.' % OROCUP),
    ]
    passi_html = ""
    for n, t, c in passi:
        passi_html += (
            '<tr>'
            '<td width="34" style="padding:0 14px 18px 0;vertical-align:top">'
            '<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
            '<td width="28" height="28" align="center" valign="middle" bgcolor="%s" '
            'style="width:28px;height:28px;border-radius:14px;font:700 13px %s;color:#fff">%s</td>'
            '</tr></table></td>'
            '<td style="padding:0 0 18px;font:400 15px/1.65 %s;color:%s">'
            '<b style="color:%s">%s</b><br>%s</td></tr>' % (NAVY, SANS, n, SANS, TESTO, NAVY, t, c)
        )

    corpo = f"""
    <tr><td style="padding:0 44px">
      {_p("La tua richiesta di adesione alla Fondazione «Per Sophia» ETS è arrivata. In allegato trovi il <b>modulo già compilato</b> con i dati che ci hai lasciato: manca solo la tua firma.")}
    </td></tr>
    <tr><td style="padding:6px 44px 24px">{_righe(voci)}</td></tr>
    <tr><td style="padding:0 44px 4px">
      <p style="margin:0 0 18px;font:600 11px {SANS};letter-spacing:.16em;text-transform:uppercase;color:{OROCUP}">Cosa fare adesso</p>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">{passi_html}</table>
    </td></tr>
    <tr><td style="padding:6px 44px 8px">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
             style="background:{NAVY};border-radius:10px">
        <tr><td style="padding:22px 24px">
          <p style="margin:0 0 12px;font:600 11px {SANS};letter-spacing:.16em;text-transform:uppercase;color:{ORO}">Coordinate per il versamento</p>
          <p style="margin:0;font:400 14px/1.75 {SANS};color:#E7ECF3">
            Fondazione «Per Sophia» ETS · Banca Popolare Etica, Filiale di Firenze<br>
            <span style="font:600 15px {SANS};color:#fff;letter-spacing:.02em">IT52 I050 1802 8000 0001 1307 055</span><br>
            BIC CCRTIT2T84A &nbsp;·&nbsp; c/c postale 1011096771
          </p>
        </td></tr>
      </table>
    </td></tr>
    <tr><td style="padding:24px 44px 0">
      {_p("Il tuo contributo diventa borse di studio, cattedre d'insegnamento, ricerca e biblioteca per gli studenti dell'Istituto Universitario Sophia. Per qualsiasi cosa, scrivici: ti rispondiamo noi.")}
    </td></tr>"""
    return _guscio("Adesione ricevuta", "Grazie, %s." % nome, corpo)


def mail_interna(d):
    voci = [
        ("Nome e cognome", "%s %s" % (d.get("nome", ""), d.get("cognome", ""))),
        ("Email", d.get("email")),
        ("Telefono", d.get("telefono")),
        ("Nato a", d.get("nato")),
        ("Codice fiscale", d.get("cf")),
        ("Residenza", d.get("residenza")),
        ("Ente", d.get("ente")),
        ("Tipo di adesione", d.get("tipo_esteso") or d.get("tipo")),
        ("Importo annuo", ("%s €" % d["importo"]) if d.get("importo") else ""),
        ("Anni di versamento", d.get("anni")),
        ("Destinazione", d.get("destinazione")),
        ("Progetto indicato", d.get("obiettivo")),
        ("Messaggio", d.get("messaggio")),
        ("Ricevuta il", d.get("data")),
    ]
    corpo = f"""
    <tr><td style="padding:0 44px">
      {_p("È arrivata una nuova richiesta di adesione dal sito. Il <b>modulo compilato</b> è in allegato; una copia è già stata inviata a chi ha aderito, con le coordinate per il versamento.")}
    </td></tr>
    <tr><td style="padding:6px 44px 26px">{_righe(voci)}</td></tr>
    <tr><td style="padding:0 44px 6px">
      {_p("Quando arriveranno il modulo firmato e la ricevuta, l'adesione potrà essere registrata.", "color:%s;font-size:14px" % FIOCO)}
    </td></tr>"""
    titolo = "%s %s — %s" % (d.get("nome", ""), d.get("cognome", ""), d.get("tipo", ""))
    return _guscio("Nuova adesione", titolo, corpo)
