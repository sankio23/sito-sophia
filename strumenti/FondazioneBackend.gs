/**
 * Fondazione «Per Sophia» ETS — ricezione del modulo di adesione dal sito.
 *
 * COME SI INSTALLA (una volta sola)
 *  1. script.google.com → Nuovo progetto → incolla questo file al posto di Codice.gs
 *  2. Salva, poi Distribuisci → Nuova distribuzione → tipo «App web»
 *       · Esegui come: me stesso
 *       · Chi ha accesso: chiunque
 *  3. Copia l'URL che finisce con /exec e incollalo in js/config.js del sito
 *  4. Alla prima esecuzione Google chiede l'autorizzazione a inviare email: concedila
 *
 * DURANTE LE PROVE le mail vanno solo a PROVA. Per andare in produzione
 * basta mettere PROVA = '' qui sotto.
 */

var PROVA       = 'marco.sanchioni@sophiauniversity.org'; // '' per andare in produzione
var FONDAZIONE  = 'fondazione@sophiauniversity.org';
var MITTENTE    = 'Fondazione «Per Sophia» ETS';
var BAND        = 'https://sankio23.github.io/sito-sophia/email/band-fondazione.png';
var SITO        = 'https://sankio23.github.io/sito-sophia/fondazione/index.html';

var NAVY = '#152D3A', ORO = '#F8B815', OROCUP = '#8A7014',
    TESTO = '#2B3A45', FIOCO = '#6B7885', FILO = '#E3E8EF',
    FONDO = '#EEF1F6', TENUE = '#F6F8FB';
var SERIF = "Georgia,'Times New Roman',Times,serif";
var SANS  = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif";

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    var oggi = Utilities.formatDate(new Date(), 'Europe/Rome', "d MMMM yyyy");
    d.data = oggi;

    var allegati = [];
    if (d.pdf) {
      allegati.push(Utilities.newBlob(
        Utilities.base64Decode(d.pdf), 'application/pdf',
        d.pdfNome || 'Modulo-di-adesione.pdf'));
    }

    // 1 · alla Fondazione (o all'indirizzo di prova)
    MailApp.sendEmail({
      to: PROVA || FONDAZIONE,
      subject: 'Nuova adesione — ' + d.nome + ' ' + d.cognome,
      htmlBody: mailInterna(d),
      body: testoSemplice(d),
      name: MITTENTE,
      replyTo: d.email || FONDAZIONE,
      attachments: allegati
    });

    // 2 · a chi ha aderito
    if (d.email) {
      MailApp.sendEmail({
        to: PROVA || d.email,
        subject: 'La tua adesione alla Fondazione «Per Sophia» ETS',
        htmlBody: mailAderente(d),
        body: testoSemplice(d),
        name: MITTENTE,
        replyTo: FONDAZIONE,
        attachments: allegati
      });
    }
    return ContentService.createTextOutput(JSON.stringify({ok: true}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    MailApp.sendEmail(PROVA || FONDAZIONE, 'Errore nel modulo di adesione', String(err));
    return ContentService.createTextOutput(JSON.stringify({ok: false, errore: String(err)}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService.createTextOutput('Fondazione per Sophia ETS — endpoint del modulo di adesione.');
}

/* ───────────────────────── pezzi comuni ───────────────────────── */

function righe(voci) {
  var out = '', primo = true;
  for (var i = 0; i < voci.length; i++) {
    var et = voci[i][0], va = voci[i][1];
    if (!va) continue;
    var b = primo ? '' : 'border-top:1px solid ' + FILO + ';';
    primo = false;
    out += '<tr><td style="' + b + 'padding:11px 0 11px 22px;font:400 13px ' + SANS + ';color:' + FIOCO + ';width:42%;vertical-align:top">' + et + '</td>'
         + '<td style="' + b + 'padding:11px 22px 11px 12px;font:600 14px ' + SANS + ';color:' + NAVY + ';vertical-align:top">' + esc(va) + '</td></tr>';
  }
  return '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:' + TENUE
       + ';border-left:3px solid ' + ORO + ';border-radius:0 8px 8px 0">' + out + '</table>';
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function p(t) {
  return '<p style="margin:0 0 16px;font:400 15px/1.7 ' + SANS + ';color:' + TESTO + '">' + t + '</p>';
}

function guscio(occhiello, titolo, corpo) {
  return '<!DOCTYPE html><html lang="it"><head><meta charset="utf-8">'
  + '<meta name="viewport" content="width=device-width,initial-scale=1"><title>' + esc(titolo) + '</title></head>'
  + '<body style="margin:0;padding:0;background:' + FONDO + '">'
  + '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:' + FONDO + '">'
  + '<tr><td align="center" style="padding:30px 12px">'
  + '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640" style="width:640px;max-width:100%;background:#FFFFFF;border:1px solid ' + FILO + ';border-radius:14px;overflow:hidden">'
  + '<tr><td style="line-height:0;font-size:0"><img src="' + BAND + '" width="640" alt="Fondazione per Sophia ETS" style="display:block;width:100%;max-width:640px;height:auto;border:0"></td></tr>'
  + '<tr><td style="padding:36px 44px 0">'
  + '<p style="margin:0 0 14px;font:600 11px ' + SANS + ';letter-spacing:.16em;text-transform:uppercase;color:' + OROCUP + '">' + occhiello + '</p>'
  + '<h1 style="margin:0 0 20px;font:400 29px/1.22 ' + SERIF + ';color:' + NAVY + '">' + esc(titolo) + '</h1></td></tr>'
  + corpo
  + '<tr><td style="padding:14px 44px 40px"><p style="margin:0;font:400 15px/1.7 ' + SANS + ';color:' + TESTO + '">Con gratitudine,<br><b style="color:' + NAVY + '">La Fondazione «Per Sophia» ETS</b></p></td></tr>'
  + '</table>'
  + '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640" style="width:640px;max-width:100%"><tr>'
  + '<td style="padding:20px 24px 6px;font:400 12px/1.7 ' + SANS + ';color:' + FIOCO + ';text-align:center">'
  + 'Fondazione «Per Sophia» ETS · Codice fiscale 94177760488<br>'
  + 'Sede legale: Loc. Burchio, c/o Polo Lionello Bonfanti — 50064 Figline e Incisa Valdarno (FI)<br>'
  + 'Tel. +39 055 9051515 · <a href="mailto:' + FONDAZIONE + '" style="color:' + FIOCO + '">' + FONDAZIONE + '</a> · '
  + '<a href="' + SITO + '" style="color:' + FIOCO + '">sophiauniversity.org</a>'
  + '</td></tr></table></td></tr></table></body></html>';
}

/* ───────────────────────── le due mail ───────────────────────── */

function mailAderente(d) {
  var voci = [
    ['Tipo di adesione', d.tipoEsteso || d.tipo],
    ['Importo annuo', d.importo ? d.importo + ' €' : ''],
    ['Anni di versamento', d.anni],
    ['Destinazione', d.destinazione],
    ['Progetto indicato', d.obiettivo],
    ['Per conto di', d.ente],
    ['Richiesta ricevuta il', d.data]
  ];
  var passi = [
    ['1', 'Firma il modulo', 'Apri il PDF allegato — è già compilato con i tuoi dati. Aggiungi <b>luogo, data e firma</b> nei due spazi previsti.'],
    ['2', 'Effettua il versamento', 'Con le coordinate qui sotto, indicando come causale il tuo nome e «adesione alla Fondazione».'],
    ['3', 'Rispediscilo', 'Manda il modulo firmato e la ricevuta del versamento a <a href="mailto:' + FONDAZIONE + '" style="color:' + OROCUP + '">' + FONDAZIONE + '</a>, oppure per posta alla sede legale.']
  ];
  var passiHtml = '';
  for (var i = 0; i < passi.length; i++) {
    passiHtml += '<tr><td width="34" style="padding:0 14px 18px 0;vertical-align:top">'
      + '<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
      + '<td width="28" height="28" align="center" valign="middle" bgcolor="' + NAVY + '" style="width:28px;height:28px;border-radius:14px;font:700 13px ' + SANS + ';color:#fff">' + passi[i][0] + '</td>'
      + '</tr></table></td>'
      + '<td style="padding:0 0 18px;font:400 15px/1.65 ' + SANS + ';color:' + TESTO + '">'
      + '<b style="color:' + NAVY + '">' + passi[i][1] + '</b><br>' + passi[i][2] + '</td></tr>';
  }
  var corpo =
      '<tr><td style="padding:0 44px">' + p('La tua richiesta di adesione alla Fondazione «Per Sophia» ETS è arrivata. In allegato trovi il <b>modulo già compilato</b> con i dati che ci hai lasciato: manca solo la tua firma.') + '</td></tr>'
    + '<tr><td style="padding:6px 44px 24px">' + righe(voci) + '</td></tr>'
    + '<tr><td style="padding:0 44px 4px"><p style="margin:0 0 18px;font:600 11px ' + SANS + ';letter-spacing:.16em;text-transform:uppercase;color:' + OROCUP + '">Cosa fare adesso</p>'
    + '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">' + passiHtml + '</table></td></tr>'
    + '<tr><td style="padding:6px 44px 8px"><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:' + NAVY + ';border-radius:10px"><tr><td style="padding:22px 24px">'
    + '<p style="margin:0 0 12px;font:600 11px ' + SANS + ';letter-spacing:.16em;text-transform:uppercase;color:' + ORO + '">Coordinate per il versamento</p>'
    + '<p style="margin:0;font:400 14px/1.75 ' + SANS + ';color:#E7ECF3">Fondazione «Per Sophia» ETS · Banca Popolare Etica, Filiale di Firenze<br>'
    + '<span style="font:600 15px ' + SANS + ';color:#fff;letter-spacing:.02em">IT52 I050 1802 8000 0001 1307 055</span><br>'
    + 'BIC CCRTIT2T84A &nbsp;·&nbsp; c/c postale 1011096771</p></td></tr></table></td></tr>'
    + '<tr><td style="padding:24px 44px 0">' + p("Il tuo contributo diventa borse di studio, cattedre d'insegnamento, ricerca e biblioteca per gli studenti dell'Istituto Universitario Sophia. Per qualsiasi cosa, scrivici: ti rispondiamo noi.") + '</td></tr>';
  return guscio('Adesione ricevuta', 'Grazie, ' + d.nome + '.', corpo);
}

function mailInterna(d) {
  var voci = [
    ['Nome e cognome', d.nome + ' ' + d.cognome],
    ['Email', d.email],
    ['Telefono', d.telefono],
    ['Nato a', d.nato],
    ['Codice fiscale', d.cf],
    ['Residenza', d.residenza],
    ['Ente', d.ente],
    ['Ruolo nell\'ente', d.ruoloEnte],
    ['Tipo di adesione', d.tipoEsteso || d.tipo],
    ['Importo annuo', d.importo ? d.importo + ' €' : ''],
    ['Anni di versamento', d.anni],
    ['Destinazione', d.destinazione],
    ['Progetto indicato', d.obiettivo],
    ['Messaggio', d.messaggio],
    ['Ricevuta il', d.data]
  ];
  var corpo =
      '<tr><td style="padding:0 44px">' + p('È arrivata una nuova richiesta di adesione dal sito. Il <b>modulo compilato</b> è in allegato; una copia è già stata inviata a chi ha aderito, con le coordinate per il versamento.') + '</td></tr>'
    + '<tr><td style="padding:6px 44px 26px">' + righe(voci) + '</td></tr>'
    + '<tr><td style="padding:0 44px 6px"><p style="margin:0;font:400 14px/1.7 ' + SANS + ';color:' + FIOCO + '">Quando arriveranno il modulo firmato e la ricevuta del versamento, l\'adesione potrà essere registrata.</p></td></tr>';
  return guscio('Nuova adesione', d.nome + ' ' + d.cognome + ' — ' + (d.tipo || ''), corpo);
}

function testoSemplice(d) {
  return 'Adesione alla Fondazione «Per Sophia» ETS\n\n'
    + d.nome + ' ' + d.cognome + '\n' + (d.email || '') + '\n'
    + (d.tipoEsteso || d.tipo || '') + (d.importo ? ' — ' + d.importo + ' €' : '') + '\n\n'
    + 'Il modulo compilato è in allegato.';
}
