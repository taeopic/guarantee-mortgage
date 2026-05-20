/* Golden Light Cascade -- subtle warm motes drifting through the hero.
   Pairs with the CSS sheen sweep in .hero-shimmer::after. */
(function () {
  function init() {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var host = document.querySelector('.hero-shimmer');
    if (!host) return;

    var canvas = document.createElement('canvas');
    host.appendChild(canvas);
    var ctx = canvas.getContext('2d');

    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var particles = [];
    var width = 0, height = 0, count = 0;
    var lastTime = performance.now();

    function resize() {
      var rect = host.getBoundingClientRect();
      width = Math.max(1, Math.floor(rect.width));
      height = Math.max(1, Math.floor(rect.height));
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      count = window.innerWidth < 768 ? 15 : 45;
      seed();
    }

    function rand(min, max) { return min + Math.random() * (max - min); }

    function spawn(p, fromTop) {
      p.x = rand(0, width);
      p.y = fromTop ? rand(-20, 0) : rand(0, height);
      p.vy = rand(8, 20);
      p.amp = rand(4, 14);
      p.freq = rand(0.3, 0.9);
      p.phase = rand(0, Math.PI * 2);
      p.r = rand(1, 3);
      p.life = 0;
      p.fadeIn = rand(0.8, 1.4);
      p.hold = rand(1.5, 3.5);
      p.fadeOut = rand(1.6, 2.4);
      p.total = p.fadeIn + p.hold + p.fadeOut;
      p.maxA = rand(0.4, 0.7);
      var warm = Math.random();
      p.color = warm < 0.5 ? '200,151,43' : '224,181,74';
    }

    function seed() {
      particles = [];
      for (var i = 0; i < count; i++) {
        var p = {};
        spawn(p, false);
        p.life = rand(0, p.total);
        particles.push(p);
      }
    }

    function step(now) {
      var dt = Math.min(0.05, (now - lastTime) / 1000);
      lastTime = now;
      ctx.clearRect(0, 0, width, height);
      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        p.life += dt;
        p.y += p.vy * dt;
        var sway = Math.sin(p.life * p.freq * Math.PI * 2 + p.phase) * p.amp;
        var alpha;
        if (p.life < p.fadeIn) alpha = (p.life / p.fadeIn) * p.maxA;
        else if (p.life < p.fadeIn + p.hold) alpha = p.maxA;
        else alpha = Math.max(0, (1 - (p.life - p.fadeIn - p.hold) / p.fadeOut)) * p.maxA;

        if (p.life > p.total || p.y > height + 10) { spawn(p, true); continue; }

        ctx.beginPath();
        var grd = ctx.createRadialGradient(p.x + sway, p.y, 0, p.x + sway, p.y, p.r * 4);
        grd.addColorStop(0, 'rgba(' + p.color + ',' + alpha + ')');
        grd.addColorStop(1, 'rgba(' + p.color + ',0)');
        ctx.fillStyle = grd;
        ctx.arc(p.x + sway, p.y, p.r * 4, 0, Math.PI * 2);
        ctx.fill();
      }
      requestAnimationFrame(step);
    }

    resize();
    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(host);
    else window.addEventListener('resize', resize);
    requestAnimationFrame(step);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
