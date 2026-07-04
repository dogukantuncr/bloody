# Kanlı Kabadayılar (Bloody Bastards tarzı)

Klavyeden oynanan, fizik tabanlı (ragdoll) ortaçağ kılıç dövüşü oyunu. Tek dosya, tarayıcıda çalışır — `index.html`'i açman yeterli.

## Nasıl oynanır
| Tuş | İşlev |
|-----|-------|
| `A` / `D` (veya `←` `→`) | Hareket |
| `W` / `Boşluk` | Zıpla |
| `J` / Fare-sol | Kılıcı savur (VUR) |
| `K` / `Shift` | Siper al (savunma / parry) |
| `S` (basılı tut) | Kılıcı yukarı kaldır |
| `P` | Duraklat |

**2 Kişi modu** — 2. oyuncu: `←` `→` hareket, `↑` zıpla, `Sağ Ctrl` vur, `Enter` siper.

## Mekanik
- Verlet fiziğiyle esneyen ragdoll karakterler.
- Darbe gücü kılıcın **momentumuna** (savurma hızına) bağlı — ne kadar hızlı savurursan o kadar sert vurur.
- Siperi doğru anda alırsan darbeyi **savuşturursun** (parry, altın kıvılcım).
- Kafaya isabet daha çok hasar verir. En iyi 3 raunttan 2'sini kazanan galip.
- Tek rakip (AI) veya 2 kişilik yerel dövüş.

Ses (WebAudio) ve kan efektleri dahil, harici dosya/bağımlılık yok.
