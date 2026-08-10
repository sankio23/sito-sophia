const { chromium } = require('playwright');
const path = require('path');

// Genera i PDF dei piani di studio dalle pagine in stampa/.
// Prima: python3 genera.py
(async () => {
  const b = await chromium.launch();
  const pg = await (await b.newContext()).newPage();
  const lavori = [
    ['piano-baccalaureato', 'Piano-di-studi-Baccalaureato',
     'Baccalaureato in Filosofia e Scienze Umane'],
    ['piano-licenza', 'Piano-di-studi-Licenza-magistrale',
     'Licenza Magistrale in Filosofia, Economia di Comunione e Ambiente'],
  ];
  for (const [src, out, titolo] of lavori) {
    await pg.goto('file://' + path.resolve('stampa', src + '.html'), { waitUntil: 'networkidle' });
    await pg.emulateMedia({ media: 'print' });
    await pg.pdf({
      path: path.resolve('media', out + '.pdf'),
      format: 'A4', printBackground: true,
      margin: { top: '16mm', bottom: '18mm', left: '16mm', right: '16mm' },
      displayHeaderFooter: true,
      headerTemplate: '<div></div>',
      footerTemplate: `<div style="width:100%;font-size:7pt;color:#696967;
        font-family:Helvetica,Arial,sans-serif;padding:0 16mm;
        display:flex;justify-content:space-between;">
        <span>Istituto Universitario Sophia · ${titolo}</span>
        <span>pag. <span class="pageNumber"></span> di <span class="totalPages"></span></span></div>`,
    });
    console.log('creato: media/' + out + '.pdf');
  }
  await b.close();
})();
