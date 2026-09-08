/* Modulo di adesione alla Fondazione «Per Sophia» ETS.
   Alla conferma: compila nel browser il PDF ufficiale (media/Modulo-di-adesione…pdf,
   che è un modulo PDF con campi), lo scarica sul dispositivo di chi lo compila e lo
   allega alla mail che parte verso la Fondazione e, in copia, verso chi ha compilato.
   Senza JavaScript il modulo resta un normale invio: i dati arrivano lo stesso,
   soltanto senza il PDF già compilato. */
(function () {
  'use strict';

  var form = document.getElementById('modulo-adesione');
  if (!form) return;

  var MODELLO = '../media/Modulo-di-adesione-Fondazione-per-Sophia.pdf';
  var bottone = form.querySelector('button[type="submit"]');
  var avviso = document.getElementById('modulo-avviso');
  var fatto = document.getElementById('modulo-fatto');
  var scaricaDiNuovo = document.getElementById('modulo-riscarica');
  var allegato = document.getElementById('ad-allegato');

  /* con JavaScript la risposta di FormSubmit finisce in una cornice nascosta:
     la pagina non si sposta e il download appena avviato non viene interrotto. */
  form.target = 'fps-invio';

  function val(nome) {
    var c = form.elements[nome];
    return c ? String(c.value || '').trim() : '';
  }

  function data(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
    return m ? m[3] + '/' + m[2] + '/' + m[1] : (iso || '');
  }

  function importo(x) {
    var n = String(x || '').replace(/[^\d,.]/g, '').replace(/\./g, '').replace(',', '.');
    if (!n || isNaN(parseFloat(n))) return String(x || '');
    return parseFloat(n).toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function pulisci(s) {
    return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^A-Za-z0-9]+/g, '-').replace(/^-|-$/g, '');
  }

  async function componiPdf() {
    var risposta = await fetch(MODELLO, { cache: 'no-cache' });
    if (!risposta.ok) throw new Error('modello non raggiungibile');
    var pdf = await PDFLib.PDFDocument.load(await risposta.arrayBuffer());
    var campi = pdf.getForm();

    function scrivi(nome, valore) {
      if (!valore) return;
      try { campi.getTextField(nome).setText(String(valore)); } catch (e) {}
    }
    function spunta(nome) {
      try { campi.getCheckBox(nome).check(); } catch (e) {}
    }

    scrivi('nome_cognome', (val('Nome') + ' ' + val('Cognome')).trim());
    scrivi('nato_a', val('Luogo di nascita'));
    scrivi('nato_il', data(val('Data di nascita')));
    scrivi('residenza', val('Comune'));
    scrivi('provincia', val('Provincia'));
    scrivi('nazione', val('Nazione'));
    scrivi('cap', val('CAP'));
    scrivi('via', val('Indirizzo'));
    scrivi('civico', val('Numero civico'));
    scrivi('codice_fiscale', val('Codice fiscale').toUpperCase());
    scrivi('telefono', val('Telefono'));
    scrivi('email', val('Email'));

    scrivi('ruolo_ente', val('Ruolo nell ente'));
    scrivi('ente', val('Ente'));
    scrivi('sede_ente', val('Sede ente'));
    scrivi('provincia_ente', val('Provincia ente'));
    scrivi('nazione_ente', val('Nazione ente'));
    scrivi('cap_ente', val('CAP ente'));
    scrivi('via_ente', val('Indirizzo ente'));
    scrivi('civico_ente', val('Numero civico ente'));
    scrivi('cf_ente', val('Codice fiscale ente').toUpperCase());
    scrivi('piva_ente', val('Partita IVA ente'));

    var tipo = val('Tipo di adesione');
    var euro = importo(val('Importo annuo'));
    var anni = val('Anni di versamento');
    if (tipo === 'Sovventore') {
      spunta('quota_sovventore'); scrivi('importo_sovventore', euro); scrivi('anni_sovventore', anni);
    } else if (tipo === 'Aderente') {
      spunta('quota_aderente'); scrivi('importo_aderente', euro); scrivi('anni_aderente', anni);
    } else {
      spunta('quota_contribuente'); scrivi('importo_contribuente', euro); scrivi('anni_contribuente', anni);
    }

    if (val('Destinazione') === 'Al patrimonio') spunta('destina_patrimonio');
    else { spunta('destina_gestione'); scrivi('obiettivi_specifici', val('Obiettivo specifico')); }

    campi.flatten();
    return await pdf.save();
  }

  function scarica(blob, nome) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = nome; a.style.display = 'none';
    document.body.appendChild(a); a.click(); a.remove();
    if (scaricaDiNuovo) { scaricaDiNuovo.href = url; scaricaDiNuovo.download = nome; scaricaDiNuovo.hidden = false; }
    setTimeout(function () { if (!scaricaDiNuovo) URL.revokeObjectURL(url); }, 120000);
  }

  function messaggio(testo, errore) {
    if (!avviso) return;
    avviso.hidden = false;
    avviso.textContent = testo;
    avviso.className = errore ? 'form-note form-note--errore' : 'form-note';
  }

  function concludi() {
    form.hidden = true;
    if (fatto) { fatto.hidden = false; fatto.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (!form.reportValidity()) return;

    bottone.disabled = true;
    var etichetta = bottone.textContent;
    bottone.textContent = 'Preparo il modulo…';
    messaggio('Sto compilando il modulo di adesione…');

    /* l'indirizzo di chi compila riceve copia della stessa mail, con il PDF allegato */
    var copia = form.elements['_cc'];
    if (copia) copia.value = val('Email');

    var lavoro = (typeof PDFLib === 'undefined')
      ? Promise.reject(new Error('pdf-lib non disponibile'))
      : componiPdf();

    lavoro.then(function (byte) {
      var blob = new Blob([byte], { type: 'application/pdf' });
      var nome = 'Modulo-adesione-' + (pulisci(val('Cognome')) || 'Fondazione-per-Sophia') + '.pdf';
      scarica(blob, nome);
      try {
        var dt = new DataTransfer();
        dt.items.add(new File([blob], nome, { type: 'application/pdf' }));
        allegato.files = dt.files;
      } catch (e) { /* qualche browser non lo consente: la mail parte senza allegato */ }
    }).catch(function (e) {
      if (window.console) console.warn('[modulo] PDF non generato:', e);
    }).then(function () {
      form.submit();
      setTimeout(concludi, 400);
    });
  });
})();
