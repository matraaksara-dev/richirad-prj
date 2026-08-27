# AUDIT UI/UX & RENCANA PERBAIKAN — Richirad. Landing Page

> **Dokumen ini adalah rencana eksekusi. JANGAN BERPIKIR, CUKUP IKUTI LANGKAH.**
> Setiap tugas bersifat atomik: kerjakan berurutan Task 1 → Task 8, jangan loncat,
> jangan rakit ulang struktur, jangan ubah teks/desain di luar yang diperintahkan.
>
> **Target halaman:** homepage (`src/pages/index.astro`) dan turunannya, plus halaman VIP bila disebut.
> **Stack:** Astro v7 + Tailwind CSS v4. Token warna & tema gelap/terang WAJIB dipertahankan.

---

## BAGIAN A — HASIL AUDIT (ringkasan kondisi saat ini)

### Yang SUDAH BAIK (jangan dirusak)
| Area | Status |
|------|--------|
| SEO meta (title, description, OG, canonical, 1× h1) | ✅ Baik |
| Aksesibilitas dasar (alt text, aria-label, focus-visible, hierarki heading) | ✅ Baik |
| Tema gelap/terang dengan token semantik | ✅ Baik |
| Responsif mobile (tidak ada horizontal overflow) | ✅ Baik |
| Konsistensi ukuran tombol CTA pasangan (btn-primary vs btn-gold) | ✅ Sudah diperbaiki |
| Disclaimer legal footer | ✅ Ada |

### MASALAH yang ditemukan (harus diperbaiki)
| # | Masalah | Prioritas | Diperbaiki di Task |
|---|---------|-----------|--------------------|
| M1 | **Formulir pendaftaran redundan.** Registrasi kini langsung ke Telegram, tapi masih ada form 4 field + checkbox + validasi JS di `JoinSection.astro`. Form tanpa backend hanyalah dead-end UX. | 🔴 Tinggi | Task 2 |
| M2 | **Aset raksasa untuk ukuran kecil.** `logo-mrtrader.png` = 452 KB, `logo-syntesium.png` = 973 KB — total ~1,4 MB hanya untuk 2 lingkaran 36×36 px. Melanggar best practice performa (LCP). | 🔴 Tinggi | Task 1 |
| M3 | **Nol animasi.** Tidak ada satu pun `@keyframes`/`animation` di CSS. Halaman terasa statis/kaku dibanding standar landing page modern. | 🟡 Sedang | Task 4–7 |
| M4 | **Background flat.** Semua section hanya warna solid, tanpa depth/glambient. Terutama section gelap Final CTA yang terasa kosong. | 🟡 Sedang | Task 5 |
| M5 | **FAQ accordion terbuka "menyentak"** (native details, tanpa animasi). | 🟢 Rendah | Task 6 |
| M6 | **Tombol tidak punya feedback gerak** saat hover/press (hanya pergantian warna). | 🟢 Rendah | Task 7 |

### Di luar lingkup AI (catatan manual untuk founder)
- `public/og-image.svg` masih placeholder — banyak platform sosial butuh **PNG/JPG 1200×630 asli** (bukan SVG). Buat manual dengan desainer.
- Link WhatsApp & Instagram di footer masih placeholder.
- Testimoni masih placeholder dari PRD.

---

## BAGIAN B — ATURAN WAJIB UNTUK EKSEKUTOR (baca dulu!)

1. Kerjakan tugas secara URUT (Task 1 … Task 8). Satu tugas = satu commit.
2. Setelah SELESAI tiap task, jalankan `npm run build`. Wajib sukses sebelum lanjut task berikutnya.
3. GUNAKAN kode yang diberikan APA ADANYA. Jangan menambah, mengurangi, atau menata-ulang properti.
4. JANGAN mengubah: token warna di `global.css` (@theme/:root/.light), teks disclaimer, teks copywriting lain, urutan section di `index.astro`, konfigurasi tema, dan struktur Header.
5. JANGAN membuat file baru kecuali diminta. JANGAN install package tambahan.
6. Semua perubahan CSS ditulis di AKHIR file `src/styles/global.css` (setelah baris terakhir), KECUALI disebut lain.
7. Push (git push origin main) HANYA dilakukan di Task 8 setelah semua verifikasi lulus.

---

## TASK 1 — OPTIMASI GAMBAR BRANDING (perbaiki M2)

**File yang berubah:** `public/branding/logo-mrtrader.png`, `public/branding/logo-syntesium.png`
(nama file TIDAK boleh diganti supaya HTML tidak perlu diedit)

**Langkah:** jalankan perintah Python ini satu kali di root proyek:

```bash
python - <<'PY'
from PIL import Image
import os
base = "public/branding/"
for f in ["logo-mrtrader.png", "logo-syntesium.png"]:
    im = Image.open(base + f).convert("RGB")
    im = im.resize((96, 96), Image.LANCZOS)
    im.save(base + f, "PNG", optimize=True)
    print(f, "->", os.path.getsize(base+f)//1024, "KB")
PY
```

**VERIFIKASI (wajib):**
```bash
ls -la public/branding/
npm run build
```
- `[OK]` kedua file ≤ 100 KB masing-masing (dari 452 KB / 950 KB).
- `[OK]` `dist/branding/` berisi kedua file hasil baru.
- Commit: `perf: optimasi aset logo branding 96x96`

---

## TASK 2 — HAPUS FORMULIR PENDAFTARAN (perbaiki M1)

Registrasi kini murni lewat grup Telegram. Formulir beserta script validasinya DIHAPUS TOTAL dan section dirapikan jadi satu kolom centered.

**File:** `src/components/JoinSection.astro`
**AKSI:** GANTI SELURUH ISI FILE dengan teks di bawah ini (persis, karakter demi karakter):

```astro
---
// Richirad. — Cara Bergabung (PRD 3.10 + Amendment v2.1)
// Telegram-first: registrasi langsung lewat grup Telegram (tanpa formulir)
import { Icon } from 'astro-icon/components';
import SectionHeading from './SectionHeading.astro';
import { SITE } from '../lib/site';

const steps = [
  { number: '1', icon: 'lucide:send', title: 'Klik Tombol Gabung', desc: 'Kamu akan diarahkan langsung ke grup resmi Richirad.' },
  { number: '2', icon: 'lucide:message-circle', title: 'Perkenalkan Diri', desc: 'Sampaikan minat dan level pengalaman belajar kamu.' },
  { number: '3', icon: 'lucide:book-open', title: 'Mulai Belajar', desc: 'Ikuti materi, diskusi, dan meetup sesuai level.' },
  { number: '4', icon: 'lucide:trending-up', title: 'Tumbuh Bersama', desc: 'Bangun kebiasaan trading yang lebih disiplin dan aman.' },
];
---

<section id="gabung" class="section-pad scroll-mt-24 bg-bg">
  <div class="container-page">
    <SectionHeading eyebrow="Gabung" title="Cara bergabung sangat sederhana." align="center" />

    <div class="mx-auto mt-12 grid max-w-3xl gap-6 sm:grid-cols-2">
      {
        steps.map((step) => (
          <div class="card flex items-start gap-4 p-5">
            <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-[8px] bg-primary-light text-[15px] font-bold text-primary">
              {step.number}
            </span>
            <div>
              <p class="text-[15px] font-semibold text-ink">{step.title}</p>
              <p class="body-secondary mt-1">{step.desc}</p>
            </div>
          </div>
        ))
      }
    </div>

    <div class="mt-10 text-center">
      <a
        href={SITE.telegram}
        target="_blank"
        rel="noopener noreferrer"
        class="btn-primary px-10 py-4 text-base"
      >
        <Icon name="lucide:send" class="h-5 w-5" />
        {SITE.telegramLabel}
      </a>
      <p class="caption mt-3">Diskusi &amp; update komunitas</p>
    </div>
  </div>
</section>
```

**Larangan khusus task ini:** JANGAN menambahkan kembali form, input, label, checkbox, element `<script>`, ataupun pesan sukses. JANGAN mengubah id="gabung".

**VERIFIKASI (wajib):**
```bash
npm run build
grep -c "join-form\|Kirim Pendaftaran\|form-success" dist/index.html
```
- `[OK]` angka yang keluar adalah `0`.
- `[OK]` dist/index.html masih mengandung `Gabung Grup Richirad`.
- Commit: `refactor: hapus formulir — registrasi langsung via Telegram`

---

## TASK 3 — SIAPKAN FONDASI ANIMASI SCROLL REVEAL (fondasi untuk Task 4)

Pola aman: konten TETAP TERLIHAT walau JavaScript mati (kelas `.js` dipasang dulu oleh script head).

### 3a. File: `src/layouts/BaseLayout.astro`
Tambahkan SATU baris ini sebagai baris pertama DI DALAM fungsi inline script tema yang sudah ada (blok `/* Anti-flash ... */`):

```js
        document.documentElement.classList.add('js');
```
(letakkan tepat sebelum baris `var light = stored === 'light';` — indentasi 8 spasi seperti baris lain di blok itu.)

### 3b. File: `src/layouts/BaseLayout.astro`
Di dekat akhir file, tambahkan blok script ini TEPAT SEBELUM tag `</body>`:

```astro
    <script>
      // Scroll reveal — pasang [data-animate] otomatis pada anak langsung tiap section
      const els = document.querySelectorAll('main section .container-page > *');
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
    </script>
```

### 3c. File: `src/styles/global.css`
Tambahkan di AKHIR file:

```css
/* Scroll reveal (Task 3) — konten tetap terlihat tanpa JS */
@media (prefers-reduced-motion: no-preference) {
  html.js [data-animate] {
    opacity: 0;
    transform: translateY(16px);
    transition:
      opacity 0.6s ease-out,
      transform 0.6s ease-out;
  }
  html.js [data-animate].is-visible {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**VERIFIKASI (wajib):**
```bash
npm run build
grep -c "is-visible\|data-animate" dist/index.html
grep -c "classList.add('js')" dist/index.html
```
- `[OK]` kedua angka ≥ 1.
- Commit: `feat: fondasi scroll reveal dengan fallback tanpa-JS`

---

## TASK 4 — ANIMASI FAQ ACCORDION (perbaiki M5)

**File:** `src/styles/global.css` — tambahkan di AKHIR file (setelah blok Task 3):

```css
/* FAQ accordion — transisi buka halus (Task 4) */
@media (prefers-reduced-motion: no-preference) {
  details[open] > summary + * {
    animation: faq-in 0.25s ease-out both;
  }
}
@keyframes faq-in {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
```

**VERIFIKASI:**
```bash
npm run build && grep -c "faq-in" dist/index.html
```
- `[OK]` angka ≥ 1. Commit: `feat: animasi buka accordion FAQ`

---

## TASK 5 — BACKGROUND IMPROVEMENT / AMBIENT GLOW (perbaiki M4)

Prinsip: dekorasi dipisah (`aria-hidden="true"`), diberi `-z-10` (di belakang konten), dan section wajib mendapat `relative overflow-hidden`.

### 5a. File: `src/components/Hero.astro`
1. Ubah baris pembuka section menjadi persis:
   `<section id="beranda" class="section-pad relative overflow-hidden">`
2. Tambahkan baris-baris ini LANGSUNG SETELAH baris pembuka section tersebut (sebelum `<div class="container-page ...">`):

```astro
  <!-- Dekorasi ambient -->
  <div aria-hidden="true" class="pointer-events-none absolute -top-24 left-1/2 h-[360px] w-[360px] -translate-x-1/2 rounded-full bg-primary/10 blur-3xl"></div>
  <div aria-hidden="true" class="pointer-events-none absolute -left-24 top-40 hidden h-[280px] w-[280px] rounded-full bg-gold/10 blur-3xl lg:block"></div>
```

### 5b. File: `src/components/FinalCta.astro`
1. Ubah pembuka section menjadi persis: `<section class="relative overflow-hidden bg-night">`
2. Tambahkan SEBELUM `<div class="container-page ...">`:

```astro
  <div aria-hidden="true" class="pointer-events-none absolute -right-20 -top-20 h-[320px] w-[320px] rounded-full bg-gold/10 blur-3xl"></div>
  <div aria-hidden="true" class="pointer-events-none absolute -bottom-24 -left-24 h-[340px] w-[340px] rounded-full bg-primary/15 blur-3xl"></div>
```

### 5c. File: `src/components/vip/VipFinalCta.astro`
1. Pembuka section jadi: `<section class="relative overflow-hidden bg-night">`
2. Tambahkan SEBELUM `<div class="container-page ...">`:

```astro
  <div aria-hidden="true" class="pointer-events-none absolute -right-24 -top-24 h-[320px] w-[320px] rounded-full bg-gold/10 blur-3xl"></div>
  <div aria-hidden="true" class="pointer-events-none absolute -bottom-24 -left-24 h-[320px] w-[320px] rounded-full bg-primary/15 blur-3xl"></div>
```

### 5d. File: `src/components/vip/VipHero.astro`
1. Pembuka section jadi: `<section class="section-pad relative overflow-hidden bg-bg">`
2. Tambahkan SEBELUM `<div class="container-page ...">`:

```astro
  <div aria-hidden="true" class="pointer-events-none absolute left-1/2 top-[-140px] h-[400px] w-[400px] -translate-x-1/2 rounded-full bg-gold/10 blur-3xl"></div>
```

**VERIFIKASI:**
```bash
npm run build
grep -c "blur-3xl" dist/index.html
curl -s http://localhost:4321/ | grep -c "aria-hidden"
```
- `[OK]` `blur-3xl` ≥ 5 (home + vip).
- Commit: `feat: ambient glow pada hero & final CTA`

---

## TASK 6 — FLOAT ANIMATION BADGE HERO (maksimalkan M3)

**File:** `src/styles/global.css` — tambahkan di AKHIR file:

```css
/* Float halus badge hero (Task 6) */
@media (prefers-reduced-motion: no-preference) {
  .animate-float {
    animation: floaty 6s ease-in-out infinite;
  }
  .animate-float-delay {
    animation: floaty 7s ease-in-out infinite;
    animation-delay: 1.2s;
  }
}
@keyframes floaty {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}
```

**File:** `src/components/Hero.astro` — dua pengeditan TEPAT:
1. Cari string `class="card absolute -top-5 right-2 flex items-center gap-3 p-3.5 sm:right-0"`
   → ganti menjadi `class="card animate-float absolute -top-5 right-2 flex items-center gap-3 p-3.5 sm:right-0"`
2. Cari string `class="card absolute -bottom-5 left-2 flex items-center gap-3 p-3.5 sm:left-0"`
   → ganti menjadi `class="card animate-float-delay absolute -bottom-5 left-2 flex items-center gap-3 p-3.5 sm:left-0"`

**VERIFIKASI:**
```bash
npm run build && grep -c "animate-float" dist/index.html
```
- `[OK]` angka = 2. Commit: `feat: float animation badge hero`

---

## TASK 7 — MICRO-INTERACTION TOMBOL (perbaiki M6)

**File:** `src/styles/global.css` — tambahkan di AKHIR file:

```css
/* Micro-interaction tombol (Task 7) */
@media (prefers-reduced-motion: no-preference) {
  .btn-primary,
  .btn-secondary,
  .btn-gold {
    transition-property:
      color,
      background-color,
      border-color,
      transform,
      box-shadow;
  }
  .btn-primary:hover,
  .btn-secondary:hover,
  .btn-gold:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgb(0 0 0 / 0.18);
  }
  .btn-primary:active,
  .btn-secondary:active,
  .btn-gold:active {
    transform: translateY(0);
    box-shadow: none;
  }
}
```

**VERIFIKASI:**
```bash
npm run build && grep -c "translateY(-1px)" dist/_astro/*.css
```
- `[OK]` angka ≥ 1. Commit: `feat: hover lift pada tombol`

---

## TASK 8 — VERIFIKASI AKHIR & DEPLOY

Jalankan SEMUA perintah berikut. Hanya lanjut push jika semua `[OK]`:

```bash
# 1. Build produksi
npm run build

# 2. Tidak ada jejak form
grep -c "join-form\|Kirim Pendaftaran\|form-success" dist/index.html
#    HARUS: 0

# 3. Fondasi reveal aktif
grep -c "classList.add('js')" dist/index.html
#    HARUS: >= 1

# 4. Glow & animasi ada
grep -c "blur-3xl" dist/index.html
#    HARUS: >= 5
grep -oc "@keyframes" dist/_astro/*.css
#    HARUS: >= 3 (faq-in, floaty)

# 5. Aset logo sudah kecil
ls -la public/branding/
#    HARUS: logo-mrtrader.png dan logo-syntesium.png <= 100KB

# 6. Cek visual browser manual:
#    - Halaman bergerak masuk (fade-up) saat discroll
#    - Badge hero mengambang pelan
#    - FAQ buka halus
#    - Tombol naik 1px saat hover
#    - Toggle dark/light tetap berfungsi normal
#    - Belanja ke halaman /vip juga dicek

# Deploy (auto-deploy dari GitHub)
git add -A
git commit -m "chore: verifikasi akhir upgrade UI/UX" --allow-empty
git push origin main
```

**Verifikasi production (setelah ±1 menit):**
```bash
curl -s https://richiradtrading.vercel.app/ | grep -c "Powered by"
#     HARUS: >= 1
curl -s -o /dev/null -w "%{http_code}\n" https://richiradtrading.vercel.app/vip/
#     HARUS: 200
```

---

## CATATAN UNTUK PEMILIK PROYEK
- Seluruh animasi otomatis NON-AKTIF bagi pengguna dengan preferensi "reduced motion" (aksesibilitas).
- Placeholder yang masih butuh manusia: OG image PNG 1200×630, link WA/IG real, testimoni real.
