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

  // Currency input formatting helpers
  function formatCurrencyInput(input) {
    const cursorStart = input.selectionStart;
    const oldValue = input.value;
    const digitsBefore = oldValue.substring(0, cursorStart).replace(/[^\d]/g, '').length;
    const digits = oldValue.replace(/[^\d]/g, '');
    const formatted = digits ? Number(digits).toLocaleString('en-US') : '';
    input.value = formatted;
    let newCursor = 0;
    let digitCount = 0;
    while (digitCount < digitsBefore && newCursor < formatted.length) {
      if (/\d/.test(formatted[newCursor])) digitCount++;
      newCursor++;
    }
    try { input.setSelectionRange(newCursor, newCursor); } catch (e) {}
  }
  function attachCurrencyFormatting(selector) {
    document.querySelectorAll(selector).forEach(input => {
      if (input.value) {
        const digits = input.value.replace(/[^\d]/g, '');
        if (digits) input.value = Number(digits).toLocaleString('en-US');
      }
      input.addEventListener('input', e => formatCurrencyInput(e.target));
      input.addEventListener('blur', e => formatCurrencyInput(e.target));
    });
  }
  function getCurrencyValue(input) {
    return parseInt(input.value.replace(/[^\d]/g, ''), 10) || 0;
  }
  attachCurrencyFormatting('input.currency, input[data-format="currency"]');

  // Mortgage calculator
  const calc = document.getElementById('mortgage-calc');
  if (calc) {
    const price = calc.querySelector('[name=price]');
    const down = calc.querySelector('[name=down]');
    const downpct = calc.querySelector('[name=downpct]');
    const rate = calc.querySelector('[name=rate]');
    const term = calc.querySelector('[name=term]');
    const tax = calc.querySelector('[name=tax]');
    const ins = calc.querySelector('[name=ins]');
    const pmi = calc.querySelector('[name=pmi]');
    const hoa = calc.querySelector('[name=hoa]');
    const out = calc.querySelector('[data-output]');

    // Optional results card elements (only present on polished calculator page)
    const legPI = document.querySelector('[data-leg-pi]');
    const legTax = document.querySelector('[data-leg-tax]');
    const legIns = document.querySelector('[data-leg-ins]');
    const legPmi = document.querySelector('[data-leg-pmi]');
    const legHoa = document.querySelector('[data-leg-hoa]');
    const totalMonthlyEl = document.querySelector('[data-total-monthly]');
    const totalInterestEl = document.querySelector('[data-total-interest]');
    const totalPaidEl = document.querySelector('[data-total-paid]');
    const loanEl = document.querySelector('[data-loan]');
    const slicesGroup = document.querySelector('[data-donut-slices]');

    const fmt = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
    const SLICE_COLORS = {
      pi: '#c8972b',
      tax: '#e0b54a',
      ins: '#f6f1e7',
      pmi: '#9a3a3a',
      hoa: '#4d1414'
    };

    function renderDonut(parts) {
      if (!slicesGroup) return;
      const total = parts.reduce((a, b) => a + b.value, 0);
      slicesGroup.innerHTML = '';
      if (total <= 0) return;
      const r = 76;
      const C = 2 * Math.PI * r;
      let offset = 0;
      parts.forEach(part => {
        if (part.value <= 0) return;
        const frac = part.value / total;
        const len = frac * C;
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('class', 'slice');
        circle.setAttribute('cx', '100');
        circle.setAttribute('cy', '100');
        circle.setAttribute('r', String(r));
        circle.setAttribute('stroke', part.color);
        circle.setAttribute('stroke-dasharray', `${len} ${C - len}`);
        circle.setAttribute('stroke-dashoffset', String(-offset));
        slicesGroup.appendChild(circle);
        offset += len;
      });
    }

    const recalc = () => {
      const p = getCurrencyValue(price);
      const d = getCurrencyValue(down);
      const r = (parseFloat(rate.value) || 0) / 100 / 12;
      const n = (parseInt(term.value) || 30) * 12;
      const loan = Math.max(p - d, 0);
      let monthlyPI = 0;
      if (r > 0 && loan > 0) {
        monthlyPI = loan * (r * Math.pow(1+r,n)) / (Math.pow(1+r,n) - 1);
      } else if (loan > 0) {
        monthlyPI = loan / n;
      }
      out.textContent = fmt.format(monthlyPI);

      // Sync down %
      if (downpct) {
        const pct = p > 0 ? (d / p) * 100 : 0;
        downpct.value = pct.toFixed(1) + '%';
      }

      // Breakdown (only if extras present)
      if (slicesGroup) {
        const monthlyTax = tax ? getCurrencyValue(tax) / 12 : 0;
        const monthlyIns = ins ? getCurrencyValue(ins) / 12 : 0;
        const monthlyPmi = pmi ? getCurrencyValue(pmi) / 12 : 0;
        const monthlyHoa = hoa ? getCurrencyValue(hoa) : 0;
        const totalMonthly = monthlyPI + monthlyTax + monthlyIns + monthlyPmi + monthlyHoa;
        const totalPaid = monthlyPI * n;
        const totalInterest = Math.max(totalPaid - loan, 0);

        if (legPI) legPI.textContent = fmt.format(monthlyPI);
        if (legTax) legTax.textContent = fmt.format(monthlyTax);
        if (legIns) legIns.textContent = fmt.format(monthlyIns);
        if (legPmi) legPmi.textContent = fmt.format(monthlyPmi);
        if (legHoa) legHoa.textContent = fmt.format(monthlyHoa);
        if (totalMonthlyEl) totalMonthlyEl.textContent = fmt.format(totalMonthly);
        if (totalInterestEl) totalInterestEl.textContent = fmt.format(totalInterest);
        if (totalPaidEl) totalPaidEl.textContent = fmt.format(totalPaid);
        if (loanEl) loanEl.textContent = fmt.format(loan);

        renderDonut([
          { value: monthlyPI, color: SLICE_COLORS.pi },
          { value: monthlyTax, color: SLICE_COLORS.tax },
          { value: monthlyIns, color: SLICE_COLORS.ins },
          { value: monthlyPmi, color: SLICE_COLORS.pmi },
          { value: monthlyHoa, color: SLICE_COLORS.hoa }
        ]);
      }
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
      btn.style.background = '#c8972b';
      btn.style.color = '#752222';
    });
  }
})();
