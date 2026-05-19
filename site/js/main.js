// Guarantee Mortgage - main.js
(function(){
  // Mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  }

  // Auto-hide nav on scroll
  const nav = document.querySelector('.site-nav');
  let lastY = window.scrollY;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (!nav) return;
    if (y > 80) nav.classList.add('scrolled'); else nav.classList.remove('scrolled');
    if (y > lastY && y > 200) nav.classList.add('hidden');
    else nav.classList.remove('hidden');
    lastY = y;
  }, { passive: true });

  // Reveal on scroll
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  // Mortgage calculator
  const calc = document.getElementById('mortgage-calc');
  if (calc) {
    const price = calc.querySelector('[name=price]');
    const down = calc.querySelector('[name=down]');
    const rate = calc.querySelector('[name=rate]');
    const term = calc.querySelector('[name=term]');
    const out = calc.querySelector('[data-output]');
    const recalc = () => {
      const p = parseFloat(price.value) || 0;
      const d = parseFloat(down.value) || 0;
      const r = (parseFloat(rate.value) || 0) / 100 / 12;
      const n = (parseInt(term.value) || 30) * 12;
      const loan = Math.max(p - d, 0);
      let monthly = 0;
      if (r > 0 && loan > 0) {
        monthly = loan * (r * Math.pow(1+r,n)) / (Math.pow(1+r,n) - 1);
      } else if (loan > 0) {
        monthly = loan / n;
      }
      const fmt = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
      out.textContent = fmt.format(monthly);
    };
    calc.querySelectorAll('input, select').forEach(el => el.addEventListener('input', recalc));
    recalc();
  }

  // Form submit demo
  const form = document.querySelector('.lead-form form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type=submit]');
      btn.textContent = 'Thanks! We will reach out within 1 business day.';
      btn.disabled = true;
      btn.style.background = '#c9a449';
      btn.style.color = '#0f2545';
    });
  }
})();
