# Richirad. — Landing Page

Landing page komunitas edukasi trading futures & spot di Kota Malang.

**Tagline:** Trading butuh teman. Bersama, kita naik level.

## Tech Stack

- **Framework:** [Astro](https://astro.build) v7 (static site generation)
- **Styling:** [Tailwind CSS](https://tailwindcss.com) v4
- **Icons:** [Lucide Icons](https://lucide.dev) via `astro-icon`
- **Font:** Inter (Google Fonts, `display=swap`)

## Design System

Color palette, typography, spacing, dan komponen mengacu pada PRD v2.0:

| Token | Hex | Penggunaan |
|-------|-----|------------|
| `primary` | `#4A90E2` | CTA, accent |
| `ink` | `#0F0F0F` | Heading |
| `ink-soft` | `#1A1A1A` | Body text |
| `muted` | `#6B7280` | Secondary text |
| `surface` | `#F3F4F6` | Background card |
| `primary-light` | `#E8F4FC` | Section soft bg |
| `border` | `#E5E7EB` | Border |

## Struktur Halaman

Semua section dari PRD (3.1–3.13) + Amendment v2.1:

1. **Header** — Sticky, nav (termasuk **VIP**), mobile hamburger, **CTA Telegram**
2. **Hero** — 2 kolom, visual card komposisi, **CTA → Telegram**
3. **Trust Bar** — 4 item keunggulan
4. **Problem → Solution** — Sendiri vs Bersama
5. **Filosofi & Nilai** — 5 nilai inti
6. **Benefits** — 6 kartu manfaat
7. **Learning Path** — 3 level edukasi
8. **👉 VipTeaser** — Banner "Kenali VIP Education" (baru, antara LearningPath & Meetup)
9. **Komunitas & Meetup** — Agenda meetup, CTA daftar → Telegram
10. **Testimoni** — 3 placeholder
11. **👉 Founders** — Profil Richi & Rad (baru, setelah Testimoni)
12. **Cara Bergabung** — 4 langkah + **CTA Telegram utama** + form opsional
13. **FAQ** — Accordion 5 item
14. **Final CTA** — Dark section, **CTA Telegram** + **Daftar VIP Insider** → `/vip`
15. **Footer** — Disclaimer legal wajib, link Telegram + VIP

### Halaman VIP (`/vip`)

Halaman khusus **VIP Education**: Hero (CTA → Telegram), target segmen, penjelasan program + **tabel skema transparan**, manfaat, cara daftar (→ Telegram), FAQ, dan **disclaimer compliance berlapis** (hero, tabel, FAQ, footer).

## Form Join

**Registrasi Telegram-first** (Amendment v2.1): semua CTA utama mengarah langsung ke
grup Telegram `https://t.me/Taa_x_Richirad` — pengguna daftar di grup.

Form di `JoinSection.astro` kini **opsional** (judul "Atau, isi formulir") untuk pengguna
yang ingin dihubungi admin. Field: Nama, Domisili, Level Pengalaman, WhatsApp/Email,
Checkbox disclaimer. Handler masih simulasi sukses (placeholder).  
**Untuk produksi:** ganti handler di `JoinSection.astro` → Formspree / API endpoint.

## Tema Gelap / Terang

- **Default: gelap** (`<html class="dark">` + token CSS di `:root`)
- Toggle Sun/Moon di header, pilihan disimpan di `localStorage` (`richirad-theme`)
- Anti-flash: script inline di `<head>` menerapkan tema sebelum render
- Token warna semantik: `bg-bg`, `bg-card`, `text-ink`, dst. berubah otomatis per tema;
  section yang selalu gelap (Final CTA, Footer) memakai token `bg-night`
- `color-scheme` ikut berubah agar kontrol form (select/checkbox) tampil sesuai tema

## Development

```sh
npm run dev      # Dev server
npm run build    # Build ke dist/
npm run preview  # Preview build
```

## SEO

- Title: `Richirad. — Komunitas Edukasi Trading Futures & Spot di Malang`
- Meta description: ✓
- Open Graph: `og-image.svg` (1200×630, placeholder SVG)
- Canonical: ✓
- Heading: 1× h1, heading hierarki terstruktur

## Disclaimer

Landing page ini adalah hasil implementasi dari PRD v2.0.  
Konten placeholder (testimoni, link WhatsApp, Instagram) perlu diisi dengan data real sebelum launch.

© 2026 Richirad. • Malang, Indonesia