# Mettere online la copia da far revisionare

L'obiettivo è avere un indirizzo da mandare in giro, non pubblicare il sito
definitivo. La copia porta `<meta name="robots" content="noindex, nofollow">`
su tutte e 122 le pagine: i motori di ricerca non la indicizzeranno.

## Perché questo passaggio lo devi fare tu

La sessione da cui è stato costruito il sito può leggere e scrivere su Drive,
ma non può caricare su GitHub: il proxy che gestisce le credenziali autorizza
solo i repository dichiarati all'avvio della sessione, e qui non ce n'è
nessuno. Il tentativo restituisce:

    access denied by the git proxy: sankio23/sito-sophia is not in this
    session's authorized repository set

I file sono comunque tutti pronti. Quello che segue richiede cinque minuti e
nessun comando da terminale.

## 1. Crea il repository

Su [github.com/new](https://github.com/new):

- nome: `sito-sophia`
- visibilità: **privato** (le pagine legali sono ancora segnaposto)
- **non** spuntare README, `.gitignore` né licenza: ci sono già nei file, e
  un doppione bloccherebbe il caricamento

## 2. Carica i file

Nella pagina del repository appena creato: **Add file → Upload files**, poi
trascina dentro **il contenuto** della cartella `sito-sophia` — non la cartella
stessa, i file e le sottocartelle che stanno dentro.

Su macOS il Finder nasconde i file che iniziano con un punto. Premi
**Cmd + Shift + .** per vederli e trascina anche `.nojekyll`, `.gitignore`,
`.gitattributes` e la cartella `.github`. Se non compaiono non è grave: il
punto 3 funziona lo stesso.

In fondo alla pagina scrivi un messaggio (per esempio «Prima versione da
revisionare») e premi **Commit changes**.

## 3. Accendi GitHub Pages

**Settings → Pages**. In *Build and deployment*, alla voce *Source*, scegli
**Deploy from a branch**, ramo `main`, cartella `/ (root)`. Salva.

Dopo un paio di minuti il sito è su:

    https://sankio23.github.io/sito-sophia/

Pages pubblica anche se il repository è privato: chiunque abbia l'indirizzo
vede il sito, ma non i file.

## 4. Quando arrivano le correzioni

Le correzioni si fanno qui, sulla cartella su Drive, e si ricarica. Per
sostituire un file già presente su GitHub: aprilo nel browser, matita in alto
a destra, incolla la versione nuova, **Commit changes**. Per un caricamento
in blocco vale di nuovo **Add file → Upload files**: i file con lo stesso nome
vengono sostituiti.

## Prima di andare in linea per davvero

Togliere il `noindex` da tutte le pagine. È una riga sola, dalla cartella del
sito:

```bash
python3 - <<'PY'
import pathlib
for p in pathlib.Path('.').rglob('*.html'):
    t = p.read_text(encoding='utf-8')
    n = t.replace('<meta name="robots" content="noindex, nofollow">\n', '')
    if n != t: p.write_text(n, encoding='utf-8')
PY
```

E toglierlo anche da `genera.py` (una riga, subito dopo `<meta charset`) e da
`index.html`, altrimenti la prima rigenerazione lo rimette.

## Alternativa in un minuto, se serve solo un'occhiata veloce

[app.netlify.com/drop](https://app.netlify.com/drop): trascini la cartella
compressa e ottieni subito un indirizzo, senza repository e senza account.
Va bene per far vedere il sito a qualcuno oggi; non va bene come base di
lavoro, perché ogni modifica richiede di ricaricare tutto.
