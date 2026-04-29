/* ═══════════════════════════════════════════════
   SOMBRERERO NÁUFRAGO — Main JS
   ═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ─── NAV SCROLL ────────────────────────────
  const nav = document.getElementById('main-nav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  });

  // ─── MOBILE NAV TOGGLE ─────────────────────
  const toggle = document.getElementById('nav-toggle');
  const links = document.getElementById('nav-links');
  toggle.addEventListener('click', () => links.classList.toggle('open'));
  links.querySelectorAll('a').forEach(a =>
    a.addEventListener('click', () => links.classList.remove('open'))
  );

  // ─── SCROLL ANIMATIONS ─────────────────────
  const animEls = document.querySelectorAll('[data-animate]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  animEls.forEach(el => observer.observe(el));

  // ─── FRAGMENTOS CAROUSEL ───────────────────
  const slides = document.querySelectorAll('.fragmento-slide');
  const dotsC = document.getElementById('frag-dots');
  let current = 0;

  // Create dots
  slides.forEach((_, i) => {
    const dot = document.createElement('span');
    dot.className = 'frag-dot' + (i === 0 ? ' active' : '');
    dot.addEventListener('click', () => goTo(i));
    dotsC.appendChild(dot);
  });

  function goTo(idx) {
    slides[current].classList.remove('active');
    dotsC.children[current].classList.remove('active');
    current = (idx + slides.length) % slides.length;
    slides[current].classList.add('active');
    dotsC.children[current].classList.add('active');
  }

  document.getElementById('frag-prev').addEventListener('click', () => goTo(current - 1));
  document.getElementById('frag-next').addEventListener('click', () => goTo(current + 1));

  // Auto-advance every 6s
  setInterval(() => goTo(current + 1), 6000);

  // ─── PARALLAX EFFECT ───────────────────────
  const pStrip = document.querySelector('.parallax-strip img');
  if (pStrip) {
    window.addEventListener('scroll', () => {
      const rect = pStrip.parentElement.parentElement.getBoundingClientRect();
      const speed = 0.3;
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        const offset = (rect.top / window.innerHeight) * 100 * speed;
        pStrip.style.transform = `translateY(${offset}px)`;
      }
    });
  }

  // ─── SMOOTH SCROLL FOR ALL ANCHORS ─────────
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ─── NEWSLETTER FORM ───────────────────────
  const form = document.getElementById('newsletter-form');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('newsletter-email').value;
    if (email) {
      form.innerHTML = '<p style="color:var(--arena);font-size:1.1rem;">✦ Bienvenido a bordo, náufrago. Nos vemos en el horizonte.</p>';
    }
  });
});
