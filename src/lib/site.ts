// Konstanta situs Richirad. — single source of truth untuk link & teks legal
export const SITE = {
  name: 'Richirad.',
  domain: 'https://richirad.id',
  // Saluran resmi registrasi (Amendment v2.1): masuk grup Telegram dulu
  telegram: 'https://t.me/Taa_x_Richirad',
  telegramLabel: 'Gabung Grup Richirad',
  // Placeholder — ganti sebelum launch
  whatsapp: 'https://wa.me/6281234567890',
  instagram: 'https://instagram.com/richirad',
} as const;

// Disclaimer khusus VIP (PRD Amendment v2.1, Bagian 8 — wajib di beberapa tempat)
export const VIP_DISCLAIMER =
  'Richirad. adalah komunitas edukasi trading. Program VIP Education merupakan program edukasi dan praktik, bukan produk investasi dengan jaminan imbal hasil. Trading futures dan spot mengandung risiko tinggi termasuk kehilangan seluruh modal. Seluruh keputusan trading dan tanggung jawab berada pada masing-masing individu. Pastikan Anda memahami risiko sebelum bergabung.';
