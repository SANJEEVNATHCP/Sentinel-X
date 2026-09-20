/* =============================================
   FRAUDLENS AI — ANIMATIONS MODULE
   ============================================= */

/* ── Particle System (Hero Background) ──────── */
class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.mouse = { x: 0, y: 0 };
    this.animationId = null;
    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    this.canvas.width = this.canvas.offsetWidth * (window.devicePixelRatio || 1);
    this.canvas.height = this.canvas.offsetHeight * (window.devicePixelRatio || 1);
    this.ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
    this.width = this.canvas.offsetWidth;
    this.height = this.canvas.offsetHeight;
    this.initParticles();
  }

  initParticles() {
    const count = Math.min(Math.floor((this.width * this.height) / 15000), 80);
    this.particles = [];
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        radius: Math.random() * 1.5 + 0.5,
        opacity: Math.random() * 0.4 + 0.1
      });
    }
  }

  draw() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Draw connections
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const dx = this.particles[i].x - this.particles[j].x;
        const dy = this.particles[i].y - this.particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          const alpha = (1 - dist / 120) * 0.12;
          this.ctx.beginPath();
          this.ctx.strokeStyle = `rgba(59, 130, 246, ${alpha})`;
          this.ctx.lineWidth = 0.5;
          this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
          this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
          this.ctx.stroke();
        }
      }
    }

    // Draw particles
    this.particles.forEach(p => {
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = `rgba(96, 165, 250, ${p.opacity})`;
      this.ctx.fill();
    });
  }

  update() {
    this.particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > this.width) p.vx *= -1;
      if (p.y < 0 || p.y > this.height) p.vy *= -1;
    });
  }

  animate() {
    this.update();
    this.draw();
    this.animationId = requestAnimationFrame(() => this.animate());
  }

  start() {
    if (!this.animationId) this.animate();
  }

  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }
}

/* ── Shield / Node Network Animation ────────── */
class ShieldAnimation {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.nodes = [];
    this.time = 0;
    this.animationId = null;
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.initNodes();
  }

  resize() {
    const size = this.canvas.offsetWidth;
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = size * dpr;
    this.canvas.height = size * dpr;
    this.ctx.scale(dpr, dpr);
    this.size = size;
    this.cx = size / 2;
    this.cy = size / 2;
  }

  initNodes() {
    const labels = ['Transaction', 'URL', 'Company', 'Recruiter', 'Device', 'Location', 'Message'];
    const colors = ['#3b82f6', '#8b5cf6', '#6366f1', '#ec4899', '#f97316', '#22c55e', '#eab308'];
    this.nodes = labels.map((label, i) => ({
      label,
      color: colors[i],
      angle: (i / labels.length) * Math.PI * 2 - Math.PI / 2,
      radius: Math.min(this.size * 0.34, 150),
      pulseOffset: Math.random() * Math.PI * 2,
      size: 6
    }));
  }

  drawShield() {
    const { ctx, cx, cy, time } = this;
    const r = Math.min(this.size * 0.15, 60);

    // Outer ring
    ctx.beginPath();
    ctx.arc(cx, cy, r + 20 + Math.sin(time * 0.8) * 3, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.08)';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Rotating ring segment
    ctx.beginPath();
    const startAngle = time * 0.5;
    ctx.arc(cx, cy, r + 20, startAngle, startAngle + Math.PI * 0.6);
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.25)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Inner glow
    const grd = ctx.createRadialGradient(cx, cy, 0, cx, cy, r + 10);
    grd.addColorStop(0, 'rgba(59, 130, 246, 0.08)');
    grd.addColorStop(0.7, 'rgba(59, 130, 246, 0.02)');
    grd.addColorStop(1, 'transparent');
    ctx.fillStyle = grd;
    ctx.beginPath();
    ctx.arc(cx, cy, r + 10, 0, Math.PI * 2);
    ctx.fill();

    // Shield icon (simplified path)
    ctx.save();
    ctx.translate(cx, cy);
    const s = r * 0.5;
    ctx.beginPath();
    ctx.moveTo(0, -s);
    ctx.bezierCurveTo(s * 0.8, -s * 0.8, s, -s * 0.3, s, 0);
    ctx.bezierCurveTo(s, s * 0.6, s * 0.3, s * 0.9, 0, s * 1.1);
    ctx.bezierCurveTo(-s * 0.3, s * 0.9, -s, s * 0.6, -s, 0);
    ctx.bezierCurveTo(-s, -s * 0.3, -s * 0.8, -s * 0.8, 0, -s);
    ctx.closePath();
    ctx.fillStyle = 'rgba(59, 130, 246, 0.06)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.3)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Lens cross
    ctx.beginPath();
    ctx.arc(s * 0.15, -s * 0.1, s * 0.35, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(96, 165, 250, 0.3)';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Scan line
    const scanY = Math.sin(time * 1.2) * s * 0.6;
    ctx.beginPath();
    ctx.moveTo(-s * 0.6, scanY);
    ctx.lineTo(s * 0.6, scanY);
    ctx.strokeStyle = `rgba(59, 130, 246, ${0.15 + Math.sin(time * 2) * 0.1})`;
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.restore();
  }

  drawNodes() {
    const { ctx, cx, cy, time, nodes } = this;

    nodes.forEach((node, i) => {
      const angle = node.angle + time * 0.15;
      const pulse = 1 + Math.sin(time * 1.5 + node.pulseOffset) * 0.08;
      const r = node.radius * pulse;
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;

      // Connection line
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x, y);
      const lineAlpha = 0.06 + Math.sin(time + i) * 0.04;
      ctx.strokeStyle = `rgba(96, 165, 250, ${lineAlpha})`;
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Data flow dot
      const flowT = (time * 0.3 + i * 0.4) % 1;
      const fx = cx + (x - cx) * flowT;
      const fy = cy + (y - cy) * flowT;
      ctx.beginPath();
      ctx.arc(fx, fy, 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(96, 165, 250, ${0.6 - flowT * 0.5})`;
      ctx.fill();

      // Node circle
      ctx.beginPath();
      ctx.arc(x, y, node.size + 2, 0, Math.PI * 2);
      ctx.fillStyle = `${node.color}15`;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(x, y, node.size, 0, Math.PI * 2);
      ctx.fillStyle = node.color + '40';
      ctx.fill();
      ctx.strokeStyle = node.color + '80';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Label
      ctx.font = '500 10px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillStyle = 'rgba(139, 153, 176, 0.8)';
      ctx.fillText(node.label, x, y + node.size + 16);
    });
  }

  drawRiskEngine() {
    const { ctx, cx, cy, time, size } = this;
    const y = cy + Math.min(size * 0.25, 100);

    // "RISK ENGINE" label
    ctx.font = '700 10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = 'rgba(96, 165, 250, 0.5)';
    ctx.letterSpacing = '0.1em';
    ctx.fillText('RISK ENGINE', cx, y);

    // Score
    const scoreAlpha = 0.5 + Math.sin(time * 1.2) * 0.2;
    ctx.font = '900 28px Inter, sans-serif';
    ctx.fillStyle = `rgba(239, 68, 68, ${scoreAlpha})`;
    ctx.fillText('87 / 100', cx, y + 30);

    // Arrow from center to risk engine
    ctx.beginPath();
    ctx.moveTo(cx, cy + Math.min(size * 0.15, 60) + 10);
    ctx.lineTo(cx, y - 18);
    ctx.strokeStyle = 'rgba(96, 165, 250, 0.1)';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  animate() {
    this.ctx.clearRect(0, 0, this.size, this.size);
    this.time += 0.016;
    this.drawShield();
    this.drawNodes();
    this.drawRiskEngine();
    this.animationId = requestAnimationFrame(() => this.animate());
  }

  start() {
    if (!this.animationId) this.animate();
  }

  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }
}

/* ── Animated Counter ───────────────────────── */
function animateCounter(element, target, duration = 1500) {
  const start = 0;
  const startTime = performance.now();

  function tick(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.round(start + (target - start) * eased);
    element.textContent = value;
    if (progress < 1) requestAnimationFrame(tick);
  }

  requestAnimationFrame(tick);
}

/* ── Scroll Reveal Observer ─────────────────── */
function initScrollReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          // Trigger counters if present
          const counters = entry.target.querySelectorAll('[data-count]');
          counters.forEach(el => {
            if (!el.dataset.counted) {
              el.dataset.counted = 'true';
              animateCounter(el, parseInt(el.dataset.count));
            }
          });
        }
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  return observer;
}

/* ── Evidence Bar Animation ─────────────────── */
function animateEvidenceBars() {
  const bars = document.querySelectorAll('.bar-fill[data-width]');
  bars.forEach((bar, i) => {
    setTimeout(() => {
      bar.style.width = bar.dataset.width + '%';
    }, i * 200);
  });
}

/* ── Score Ring Animation ───────────────────── */
function animateScoreRing(ringEl, score) {
  const circumference = 2 * Math.PI * 80; // radius=80
  const offset = circumference - (score / 100) * circumference;
  const fill = ringEl.querySelector('.ring-fill');
  if (fill) {
    fill.style.strokeDasharray = circumference;
    setTimeout(() => {
      fill.style.strokeDashoffset = offset;
    }, 300);
  }
}
