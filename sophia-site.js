/* ============================================================
   SOPHIA — script condiviso del sito
   ============================================================ */
(function () {
  'use strict';

  function ready(fn) {
    document.readyState !== 'loading'
      ? fn()
      : document.addEventListener('DOMContentLoaded', fn);
  }

  var reduceMotion = window.matchMedia
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  ready(function () {

    /* --------------------------------------------------------
       Menu mobile
       -------------------------------------------------------- */
    var toggle = document.querySelector('.menu-toggle');
    var nav = document.querySelector('nav.main');
    if (toggle && nav) {
      toggle.addEventListener('click', function () {
        var open = nav.classList.toggle('open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      nav.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () {
          nav.classList.remove('open');
          toggle.setAttribute('aria-expanded', 'false');
        });
      });
      // clic fuori dal menu: chiude
      document.addEventListener('click', function (e) {
        if (!nav.classList.contains('open')) return;
        if (nav.contains(e.target) || toggle.contains(e.target)) return;
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
      // Esc chiude il menu e riporta il focus sul pulsante
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && nav.classList.contains('open')) {
          nav.classList.remove('open');
          toggle.setAttribute('aria-expanded', 'false');
          toggle.focus();
        }
      });
    }

    /* --------------------------------------------------------
       Voce di menu corrispondente alla pagina corrente
       Sostituisce class="active" scritta a mano, che era
       applicata solo su 5 pagine su 12.
       -------------------------------------------------------- */
    var here = location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('nav.main > ul > li > a').forEach(function (a) {
      var target = (a.getAttribute('href') || '').split('#')[0];
      if (target && target === here) a.setAttribute('aria-current', 'page');
    });

    /* --------------------------------------------------------
       Ombra dell'header allo scroll
       -------------------------------------------------------- */
    var header = document.querySelector('header.site');
    if (header) {
      var onScroll = function () {
        header.classList.toggle('scrolled', window.scrollY > 8);
      };
      onScroll();
      window.addEventListener('scroll', onScroll, { passive: true });
    }

    /* --------------------------------------------------------
       Video di sfondo dell'hero
       Condizioni per far partire il video, tutte necessarie:
         - l'utente non ha chiesto meno animazioni
         - lo schermo non è piccolo (su mobile è spreco di dati)
         - la connessione non è dichiarata lenta o a consumo
       Se una manca, resta il poster: il testo è già leggibile
       sopra l'immagine, quindi non si perde nulla.
       -------------------------------------------------------- */
    document.querySelectorAll('[data-hero-video]').forEach(function (holder) {
      var video = holder.querySelector('video');
      var poster = holder.querySelector('.hero-poster');
      var btn = holder.parentElement.querySelector('.media-toggle');
      if (!video) return;

      var conn = navigator.connection || {};
      var slow = conn.saveData === true
        || /^(slow-)?2g$/.test(conn.effectiveType || '');
      var small = window.matchMedia('(max-width: 860px)').matches;

      if (reduceMotion || small || slow) {
        video.remove();
        if (btn) btn.hidden = true;
        return;
      }

      var started = false;

      function mostraVideo() {
        if (started) return;
        started = true;
        video.classList.add('is-playing');
        if (poster) poster.classList.add('is-hidden');
        if (btn) {
          btn.hidden = false;
          btn.textContent = '\u275A\u275A Metti in pausa';
          btn.setAttribute('aria-pressed', 'false');
        }
      }

      function offriRiproduzione() {
        // L'autoplay è stato negato. Non si lascia un fotogramma morto:
        // si mostra un comando esplicito. Cause tipiche: risparmio
        // energetico, impostazione del browser, Safari da file://.
        if (started || !btn) return;
        btn.hidden = false;
        btn.textContent = '\u25B6 Riproduci';
        btn.setAttribute('aria-pressed', 'true');
      }

      function avvia() {
        var p = video.play();
        if (p && p.then) {
          p.then(mostraVideo).catch(offriRiproduzione);
        } else {
          // browser che non restituiscono una promise
          setTimeout(function () {
            video.paused ? offriRiproduzione() : mostraVideo();
          }, 400);
        }
      }

      // Le sorgenti stanno in data-src per non scaricarle su mobile.
      video.querySelectorAll('source[data-src]').forEach(function (s) {
        s.src = s.getAttribute('data-src');
      });

      // play() va chiamata DOPO che ci sono dati, non subito dopo load():
      // in Safari load() interrompe la play() precedente e la promise
      // viene rifiutata con AbortError.
      video.addEventListener('loadeddata', avvia, { once: true });
      video.addEventListener('playing', mostraVideo);
      video.addEventListener('error', offriRiproduzione);
      video.load();

      // Rete di sicurezza: se dopo 3 s non è partito nulla, offri il comando.
      setTimeout(function () { if (video.paused) offriRiproduzione(); }, 3000);

      // Molti browser sbloccano l'autoplay dopo la prima interazione:
      // al primo gesto dell'utente si riprova, una volta sola.
      ['pointerdown', 'keydown', 'touchstart'].forEach(function (ev) {
        document.addEventListener(ev, function riprova() {
          if (!started && video.paused) avvia();
          ['pointerdown', 'keydown', 'touchstart'].forEach(function (e2) {
            document.removeEventListener(e2, riprova);
          });
        }, { once: true, passive: true });
      });

      // WCAG 2.2.2: un media che parte da solo e dura più di 5 s
      // deve poter essere fermato.
      if (btn) {
        btn.addEventListener('click', function () {
          if (video.paused) {
            avvia();
            btn.textContent = '\u275A\u275A Metti in pausa';
            btn.setAttribute('aria-pressed', 'false');
          } else {
            video.pause();
            btn.textContent = '\u25B6 Riprendi';
            btn.setAttribute('aria-pressed', 'true');
          }
        });
      }

      // Non consumare risorse quando la scheda non è in primo piano.
      document.addEventListener('visibilitychange', function () {
        if (document.hidden) { if (!video.paused) video.pause(); }
        else if (started && btn && btn.getAttribute('aria-pressed') !== 'true') avvia();
      });
    });

    /* --------------------------------------------------------
       Ancore interne: lo scorrimento morbido è già gestito dal CSS
       (scroll-behavior + scroll-padding-top). Qui si sposta il fuoco
       sulla destinazione, che altrimenti resterebbe dov'era: senza
       questo la tastiera continua a navigare dal punto di partenza.
       -------------------------------------------------------- */
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute('href').slice(1);
      if (!id) return;
      var dest = document.getElementById(id);
      if (!dest) return;
      window.setTimeout(function () {
        if (!dest.hasAttribute('tabindex')) dest.setAttribute('tabindex', '-1');
        dest.focus({ preventScroll: true });
      }, reduceMotion ? 0 : 420);
    });

    /* --------------------------------------------------------
       Comparsa progressiva allo scroll
       -------------------------------------------------------- */
    var selectors = ['.section-head', '.cols2 > *', '.card', '.center', '.stat',
      '.fig', '.tl', '.timeline', '.panel', '.feature', '.news', '.prose',
      '.band .wrap', '.chips', '.person', '.org-card', '.value-card',
      '.step', '.spotlight .inner'];
    var targets = [];
    selectors.forEach(function (s) {
      document.querySelectorAll(s).forEach(function (el) {
        if (!el.closest('header.site') && !el.closest('footer.site')) targets.push(el);
      });
    });
    ['.cards', '.cgrid', '.news-grid', '.people-grid', '.steps'].forEach(function (g) {
      document.querySelectorAll(g).forEach(function (grid) {
        grid.classList.add('is-stagger');
      });
    });

    if (reduceMotion || !('IntersectionObserver' in window)) {
      targets.forEach(function (el) { el.classList.add('in'); });
    } else {
      targets.forEach(function (el) { el.classList.add('reveal'); });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -12% 0px' });
      targets.forEach(function (el) { io.observe(el); });
      // rete di sicurezza: se qualcosa resta invisibile, mostralo
      window.addEventListener('beforeprint', function () {
        targets.forEach(function (el) { el.classList.add('in'); });
      });
    }

    /* --------------------------------------------------------
       Contatori animati
       -------------------------------------------------------- */
    var nums = Array.prototype.slice.call(document.querySelectorAll('.stat .n, .figures .n'));
    function animateCount(el) {
      var raw = el.textContent.trim();
      var m = raw.match(/^(~)?(\d+)$/);
      if (!m) return;                       // salta "1:5", "2007/2028"
      var target = parseInt(m[2], 10);
      if (target > 1900) return;            // gli anni non si contano
      var prefix = m[1] || '';
      var dur = 1400, start = null;
      el.setAttribute('aria-label', raw);   // il valore reale per gli screen reader
      function step(ts) {
        if (!start) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        var e = 1 - Math.pow(1 - p, 4);   // stessa uscita morbida delle transizioni
        el.textContent = prefix + Math.round(e * target);
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = raw;          // ripristina il valore esatto
      }
      el.textContent = prefix + '0';
      requestAnimationFrame(step);
    }
    if (!reduceMotion && 'IntersectionObserver' in window && nums.length) {
      var io2 = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { animateCount(e.target); io2.unobserve(e.target); }
        });
      }, { threshold: 0.6 });
      nums.forEach(function (n) { io2.observe(n); });
    }

    /* --------------------------------------------------------
       Filtro Persone
       -------------------------------------------------------- */
    var filterBar = document.querySelector('[data-people-filter]');
    if (filterBar) {
      var buttons = filterBar.querySelectorAll('button');
      buttons.forEach(function (b) {
        b.addEventListener('click', function () {
          buttons.forEach(function (x) {
            x.classList.remove('active');
            x.setAttribute('aria-pressed', 'false');
          });
          b.classList.add('active');
          b.setAttribute('aria-pressed', 'true');
          var f = b.getAttribute('data-filter');
          document.querySelectorAll('.people-section').forEach(function (sec) {
            sec.hidden = !(f === 'all' || sec.getAttribute('data-cat') === f);
          });
        });
      });
    }

    /* --------------------------------------------------------
       Fallback delle foto profilo
       Il difetto precedente: il listener 'error' veniva agganciato
       dentro DOMContentLoaded, quando per molte immagini l'evento
       era GIÀ stato emesso e non si ripete. Su 21 ritratti se ne
       recuperavano 10. Ora si controlla anche lo stato attuale.
       -------------------------------------------------------- */
    function toInitials(img) {
      if (!img.parentNode) return;
      var span = document.createElement('span');
      span.className = 'avatar-fallback';
      span.setAttribute('aria-hidden', 'true');
      span.textContent = img.getAttribute('data-initials') || '';
      var alt = img.getAttribute('alt');
      if (alt) {
        var sr = document.createElement('span');
        sr.className = 'visually-hidden';
        sr.textContent = alt;
        span.appendChild(sr);
      }
      img.parentNode.replaceChild(span, img);
    }

    document.querySelectorAll('img[data-initials]').forEach(function (img) {
      // 1. immagini già fallite prima che lo script partisse
      if (img.complete && img.naturalWidth === 0) { toInitials(img); return; }
      // 2. immagini che falliranno più avanti
      img.addEventListener('error', function () { toInitials(img); });
      // 3. rete di sicurezza per i casi limite (cache, decodifica)
      if (!img.complete) {
        img.addEventListener('load', function () {
          if (img.naturalWidth === 0) toInitials(img);
        });
      }
    });
  });
})();

/* ------------------------------------------------------------------
   Marchio dell'ateneo convenzionato: se il file del logo non c'è
   ancora, si nasconde l'immagine e resta la dicitura testuale, che
   da sola è già completa e leggibile.
   ------------------------------------------------------------------ */
(function () {
  'use strict';
  function nascondi(img) { img.style.display = 'none'; }
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.partner img').forEach(function (img) {
      if (img.complete && img.naturalWidth === 0) { nascondi(img); return; }
      img.addEventListener('error', function () { nascondi(img); });
      if (!img.complete) {
        img.addEventListener('load', function () {
          if (img.naturalWidth === 0) nascondi(img);
        });
      }
    });
  });
})();
