# Richirad. UI/UX Library — Portable Design System

> Design system lengkap yang dipakai di landing page Richirad.
> Dapat diterapkan ke website lain (framework apa pun — pure CSS + JS, tanpa dependency).

---

## 1. FONT

Google Fonts **Inter** (dengan preconnect + `display=swap` agar tidak memblokir render):

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
  rel="stylesheet"
/>
```

---

## 2. DESIGN TOKENS (CSS Variables)

### 2a. Warna — Tema Gelap (DEFAULT) & Terang

```css
/* ===== THEME: Dark (default) & Light ===== */
:root {
  --c-bg: #0f0f0f;            /* background halaman */
  --c-card: #1a1a1a;          /* background card */
  --c-surface: #141414;       /* background section alternate */
  --c-border: #2b2b2b;        /* border */
  --c-ink: #f9fafb;           /* heading */
  --c-ink-soft: #e5e7eb;      /* body text */
  --c-muted: #9ca3af;         /* teks sekunder */
  --c-primary-light: #1b3a5c; /* background icon/aksen */
  --c-gold: #e6b320;          /* emas (VIP) */
  --c-gold-hover: #c79a1c;
  --c-gold-text: #0f0f0f;     /* teks di atas tombol emas */
  color-scheme: dark;
}

.light {
  --c-bg: #ffffff;
  --c-card: #ffffff;
  --c-surface: #f3f4f6;
  --c-border: #e5e7eb;
  --c-ink: #0f0f0f;
  --c-ink-soft: #1a1a1a;
  --c-muted: #6b7280;
  --c-primary-light: #e8f4fc;
  --c-gold: #8b6914;
  --c-gold-hover: #6f560f;
  --c-gold-text: #ffffff;
  color-scheme: light;
}
```

**Warna brand tetap (tidak berubah antar tema):**
| Token | Hex | Penggunaan |
|-------|-----|------------|
| Primary Blue | `#4A90E2` | CTA, accent, icon |
| Primary Dark | `#2E6BB0` | Hover CTA |
| Night | `#0F0F0F` | Section selalu gelap (footer, CTA dark) |
| Gold Bright | `#E6B320` | Teks emas di atas bg selalu gelap |

### 2b. Tipografi & Geometri

```css
:root {
  --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --radius-card: 8px;
  --radius-btn: 6px;
  --shadow-card: 0 1px 3px rgb(0 0 0 / 0.06);
  --shadow-card-hover: 0 8px 24px rgb(0 0 0 / 0.08);
  --container-max: 1200px;
  --section-pad: 80px 100px; /* desktop */
}
```

---

## 3. CSS — KERNEL (base + komponen)

> Jika pakai **Tailwind CSS v4**: cukup tempel bagian `@layer` + variabel di atas, token otomatis jadi utility (`bg-card`, `text-ink`, dst.).
> Jika **CSS murni**: gunakan blok `@layer components` langsung — semua class siap pakai.

```css
/* ===== BASE ===== */
html { scroll-behavior: smooth; }
body {
  background-color: var(--c-bg);
  color: var(--c-ink-soft);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
}
:focus-visible { outline: 2px solid #4a90e2; outline-offset: 2px; }
details > summary { list-style: none; }
details > summary::-webkit-details-marker { display: none; }

/* ===== COMPONENTS ===== */
.container-page { max-width: 1200px; margin-inline: auto; padding-inline: 20px; }
@media (min-width: 640px) { .container-page { padding-inline: 32px; } }

.section-pad { padding-block: 48px; }
@media (min-width: 768px) { .section-pad { padding-block: 80px; } }
@media (min-width: 1024px) { .section-pad { padding-block: 96px; } }

/* Label kecil di atas headline */
.eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 14px; border-radius: 999px;
  border: 1px solid var(--c-border); background: var(--c-card);
  font-size: 13px; font-weight: 500; color: var(--c-muted);
}

/* Headings */
.h1 { font-size: clamp(32px, 5vw, 56px); font-weight: 700; line-height: 1.2; color: var(--c-ink); }
.h2 { font-size: clamp(24px, 3.5vw, 36px); font-weight: 600; line-height: 1.3; color: var(--c-ink); }
.h3 { font-size: clamp(18px, 2.2vw, 22px); font-weight: 600; line-height: 1.4; color: var(--c-ink); }

.lead { font-size: 16-18px; line-height: 1.6; color: var(--c-ink-soft); }
.body-secondary { font-size: 14-15px; line-height: 1.5; color: var(--c-muted); }
.caption { font-size: 13px; line-height: 1.4; color: var(--c-muted); }

/* Card */
.card {
  background: var(--c-card); border: 1px solid var(--c-border);
  border-radius: 8px; box-shadow: 0 1px 3px rgb(0 0 0 / 0.06);
}
.card:hover { box-shadow: 0 8px 24px rgb(0 0 0 / 0.08); }

/* Buttons */
.btn-primary, .btn-secondary, .btn-gold {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 12px 28px; border-radius: 6px; font-size: 15px; font-weight: 500;
  cursor: pointer; text-decoration: none;
  transition: color .2s, background-color .2s, border-color .2s;
}
.btn-primary  { background: #4a90e2; color: #fff; }
.btn-primary:hover { background: #2e6bb0; }
.btn-secondary { border: 1px solid #4a90e2; color: #4a90e2; background: transparent; }
.btn-secondary:hover { background: var(--c-primary-light); }
.btn-gold { background: var(--c-gold); color: var(--c-gold-text); font-weight: 600; }
.btn-gold:hover { background: var(--c-gold-hover); }
```

---

## 4. CSS — ANIMASI (semua menghormati `prefers-reduced-motion`)

```css
/* 4a. Scroll Reveal — tambahkan atribut data-animate ke elemen yang mau di-animasi */
@media (prefers-reduced-motion: no-preference) {
  html.js [data-animate] {
    opacity: 0;
    transform: translateY(16px);
    transition: opacity .6s ease-out, transform .6s ease-out;
  }
  html.js [data-animate].is-visible { opacity: 1; transform: translateY(0); }
}

/* 4b. FAQ Accordion — buka halus (elemen <details>) */
@media (prefers-reduced-motion: no-preference) {
  details[open] > summary + * { animation: faq-in .25s ease-out both; }
}
@keyframes faq-in {
  from { opacity: 0; transform: translateY(-4px); }
  to   { opacity: 1; transform: none; }
}

/* 4c. Float — untuk badge/card mengambang pelan */
@media (prefers-reduced-motion: no-preference) {
  .animate-float { animation: floaty 6s ease-in-out infinite; }
  .animate-float-delay { animation: floaty 7s ease-in-out infinite; animation-delay: 1.2s; }
}
@keyframes floaty {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-8px); }
}

/* 4d. Micro-interaction tombol — hover lift + press */
@media (prefers-reduced-motion: no-preference) {
  .btn-primary, .btn-secondary, .btn-gold {
    transition-property: color, background-color, border-color, transform, box-shadow;
  }
  .btn-primary:hover, .btn-secondary:hover, .btn-gold:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgb(0 0 0 / 0.18);
  }
  .btn-primary:active, .btn-secondary:active, .btn-gold:active {
    transform: translateY(0); box-shadow: none;
  }
}

/* 4e. Ambient Glow — blob blur di section dark (letakkan dengan posisi absolute) */
.glow-blob {
  position: absolute; border-radius: 9999px; filter: blur(64px);
  pointer-events: none; z-index: -1;
}
```

---

## 5. JAVASCRIPT

### 5a. Inisialisasi Tema + Fallback `.js` (tempel di `<head>`, sebelum CSS render)

```html
<script>
  (function () {
    document.documentElement.classList.add('js');
    var stored = null;
    try { stored = localStorage.getItem('site-theme'); } catch (e) { stored = null; }
    var light = stored === 'light';
    document.documentElement.classList.toggle('light', light);
    document.documentElement.classList.toggle('dark', !light);
    document.documentElement.setAttribute('data-theme', light ? 'light' : 'dark');
  })();
</script>
```

> HTML: `<html lang="id" class="dark">` — default gelap; tanpa JS pun tetap gelap.

### 5b. Toggle Tema (tombol Sun/Moon)

```html
<button id="theme-toggle" type="button" aria-label="Aktifkan tema terang" aria-pressed="false">
  <!-- ikon moon (terlihat saat light) & sun (terlihat saat dark) -->
  <svg class="icon-moon"><!-- moon icon --></svg>
  <svg class="icon-sun" hidden><!-- sun icon --></svg>
</button>
```

```js
// CSS-nya: .dark .icon-moon { display:none }  .dark .icon-sun { display:block }
const root = document.documentElement;
const toggle = document.getElementById('theme-toggle');

function applyTheme(light) {
  root.classList.toggle('light', light);
  root.classList.toggle('dark', !light);
  root.setAttribute('data-theme', light ? 'light' : 'dark');
  try { localStorage.setItem('site-theme', light ? 'light' : 'dark'); } catch (e) {}
  toggle.setAttribute('aria-pressed', String(!light));
  toggle.setAttribute('aria-label', light ? 'Aktifkan tema gelap' : 'Aktifkan tema terang');
}
toggle.addEventListener('click', () => applyTheme(root.classList.contains('dark')));
// sinkronkan label saat halaman dimuat
applyTheme(root.classList.contains('light'));
```

### 5c. Scroll Reveal (IntersectionObserver)

```js
const els = document.querySelectorAll('main section .container > *');
els.forEach((el) => el.setAttribute('data-animate', ''));

const io = new IntersectionObserver(
  (entries) => {
    for (const e of entries) {
      if (e.isIntersecting) {
        e.target.classList.add('is-visible');
        io.unobserve(e.target);
      }
    }
  },
  { threshold: 0.12 }
);
document.querySelectorAll('[data-animate]').forEach((el) => io.observe(el));
```

### 5d. Mobile Menu (hamburger)

```js
const menuToggle = document.getElementById('menu-toggle');
const menu = document.getElementById('mobile-menu');
menuToggle.addEventListener('click', () => {
  const open = menu.classList.toggle('hidden');
  menuToggle.setAttribute('aria-expanded', String(!open));
});
// tutup dengan Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !menu.classList.contains('hidden')) menu.classList.add('hidden');
});
```

---

## 6. ELEMEN SIAP PAKAI (HTML)

### 6a. Buttons
```html
<button class="btn-primary">Gabung Komunitas</button>
<button class="btn-secondary">Pelajari Lebih Lanjut</button>
<button class="btn-gold">Daftar VIP Insider</button>
```

### 6b. Card
```html
<article class="card" style="padding: 28px;">
  <div class="eyebrow">Kategori</div>
  <h3 class="h3" style="margin-top:16px;">Judul Card</h3>
  <p class="body-secondary" style="margin-top:8px;">Deskripsi card yang jelas dan ringkas.</p>
</article>
```

### 6c. FAQ Accordion (tanpa JS — native `<details>`)
```html
<details class="card">
  <summary style="padding:20px 24px;font-weight:600;cursor:pointer;">
    Apakah ini jaminan profit?
  </summary>
  <div style="padding:0 24px 24px;">
    <p class="body-secondary">Tidak. Ini adalah program edukasi.</p>
  </div>
</details>
```

### 6d. Section Heading
```html
<div style="max-width:720px;text-align:center;margin-inline:auto;">
  <p class="eyebrow">Eyebrow</p>
  <h2 class="h2" style="margin-top:12px;">Judul Section</h2>
  <p class="lead" style="margin-top:16px;color:var(--c-muted);">Subjudul section.</p>
</div>
```

### 6e. Trust Item (ikon + label)
```html
<div style="display:flex;align-items:center;gap:12px;">
  <span style="width:40px;height:40px;display:flex;align-items:center;justify-content:center;
        border-radius:8px;background:var(--c-primary-light);color:#4a90e2;">
    <!-- svg icon 20px -->
  </span>
  <p style="font-size:14px;font-weight:500;color:var(--c-ink-soft);">Label Item</p>
</div>
```

### 6f. Form Input
```css
.input {
  width: 100%; padding: 10px 14px; border-radius: 6px;
  border: 1px solid var(--c-border); background: var(--c-card);
  font-size: 15px; color: var(--c-ink);
}
.input:focus { border-color: #4a90e2; outline: 1px solid #4a90e2; }
.input::placeholder { color: var(--c-muted); }
```

### 6g. Ambient Glow (contoh penempatan)
```html
<section style="position:relative;overflow:hidden;background:var(--c-bg);">
  <div class="glow-blob" style="width:360px;height:360px;top:-96px;left:50%;
       transform:translateX(-50%);background:rgba(74,144,226,.10);"></div>
  <!-- konten section -->
</section>
```

---

## 7. CATATAN AKSESIBILITAS & BEST PRACTICE
- Semua animasi non-aktif otomatis untuk pengguna `prefers-reduced-motion`.
- Konten reveal tetap terlihat walau JavaScript mati (fallback kelas `.js` di `<html>`).
- Gunakan `aria-label` untuk ikon-only button, `alt` untuk gambar.
- Kontras: `--c-muted` aman untuk teks sekunder; heading pakai `--c-ink`.
- Button wajib bisa difokus keyboard (`focus-visible` outline disediakan).

---
*Berasal dari Richirad. Landing Page (Astro + Tailwind v4) — di-ekstrak menjadi library CSS/JS murni.*
