# Agentic Gelir Sistemi — Mimari Plan (v1)

> Hedef: Gömülü (STM32/ESP32/FPGA/RTOS) + C# WPF companion-app becerileriyle,
> yurt dışı dolar geliri üzerinden aylık **net 200.000₺ ≈ $4.300/ay**.
> Kısıt: gündüz fiziksel iş, akşam 1–2 saat, hafta sonu ~6 saat, sermaye ~10.000₺/ay.
>
> Bu doküman **kod yazmadan önceki mimari plandır** (Aşama: "önce plan, onayla, sonra inşa et").
> İki bileşen tasarlanıyor:
> 1. **Agentic Arka Ofis** — işi bulan/taslaklayan/raporlayan sistem (sen işteyken çalışır).
> 2. **Portföy Vitrin Projesi** — ESP32/STM32 + gerçek zamanlı WPF dashboard demo.

---

## 0. "Python + Claude API" — neden Claude API?

**"Claude API" nedir:** Ajanların *beyni*. Sistem şu işleri bir LLM'e yaptırır:
uzun iş ilanlarını/mail dizilerini okuyup sınıflandırmak, ilanları skorlamak,
kişiselleştirilmiş (spam olmayan) mesaj taslakları yazmak, teklif/proposal üretmek,
pazar araştırmasını özetlemek. Bu LLM çağrıları Claude API üzerinden yapılır.

**Alternatifler:** OpenAI API, Google Gemini, yerel açık modeller (Ollama/Llama).
Mimari sağlayıcıdan bağımsız kurulur; istenirse değiştirilebilir. Ama **bu iş için
önerim Claude**, çünkü:

| Gereksinim | Claude'un avantajı |
|---|---|
| Uzun bağlam okuma | Uzun iş ilanları + mail dizilerini tek seferde okuyup çıkarım yapar (1M token bağlam). |
| Yapılandırılmış çıktı | Tool use + structured output (JSON şemaya uyan çıktı) — ajan mantığı için birinci sınıf. |
| Doğal yazı (TR+EN) | Soğuk e-posta/LinkedIn mesajı için robotik olmayan, ikna edici metin. |
| Agentic tool use | Ajanların araç çağırması first-class özellik. |
| Ekosistem | Bu sistemi zaten Claude Code ile kuruyorsun; aynı ekosistem. |

**Maliyet stratejisi — model kademelemesi (gerçek 2026 fiyatları, $/1M token):**

| Model | Girdi / Çıktı | Sistemde kullanımı |
|---|---|---|
| **Claude Haiku 4.5** (`claude-haiku-4-5`) | $1 / $5 | Ucuz + yüksek hacim: ilan tarama, skorlama, inbox triyaj/sınıflandırma. |
| **Claude Sonnet 5** (`claude-sonnet-5`) | $3 / $15 | Orta: proposal taslağı, araştırma özeti. |
| **Claude Opus 4.8** (`claude-opus-4-8`) | $5 / $25 | En kaliteli metin: kişiselleştirilmiş outreach, ilk müşteri teklifleri. |

Yüksek hacimli işi Haiku'ya, kaliteli yazıyı Opus/Sonnet'e vererek **aylık API
maliyeti ~$30–80** bandında tutulur (bkz. §6 Maliyet). Bu, 10.000₺ sermayenin çok altında.

> Kod deseni: `client.messages.create(model="claude-haiku-4-5", ...)` gibi. Ajan
> mantığı için tool use + structured output (`output_config.format`) kullanılacak.

---

## 1. En kritik soru: Hangi PC? GitHub'da mı, lokal PC'de mi çalışır?

Bu ikisi **farklı şeyler**, karıştırma:

- **GitHub reposu = kaynak kod + versiyon geçmişi + yedek.** Sistem GitHub'da *çalışmaz*;
  kod orada *saklanır*. `dogukantuncr/bloody` reposu (veya yeni bir repo) kodu tutar.
- **Sistem, kodu çalıştırdığın makinede çalışır** (ajanlar orada koşar, zamanlanmış
  görevler orada tetiklenir, LinkedIn/mail oturumu orada durur).

### Çalıştırma seçenekleri

| Seçenek | Artı | Eksi | Ne zaman |
|---|---|---|---|
| **A. Ev PC'si (her zaman açık)** | Ücretsiz, tam kontrol | PC kapalıysa sistem durur; elektrik/uyku ayarı derdi | PC'yi zaten açık bırakıyorsan |
| **B. Ucuz Linux VPS** *(önerilen)* | 7/24 çalışır, sen işteyken lead toplar, reboot'a dayanır, IP sabit | ~$5/ay | "Ben işteyken sistem çalışsın" hayali için ideal |
| **C. Ev PC (dev) + VPS (runtime)** *(en iyi)* | Geliştir ev PC'sinde, 7/24 çalıştır VPS'te | İki ortam | Ciddi kuruluş |

**Önerim (C):**
- **Geliştirme:** Ev PC'n (Windows) — WPF/gömülü işlerini zaten burada yaparsın.
- **Runtime (7/24):** Ucuz Linux VPS. Örn. **Hetzner CX22 (~€4/ay)** veya
  DigitalOcean/Vultr ($5/ay). Ajanları burada **cron** ile zamanlarsın; sen fiziksel
  işteyken gündüz lead toplar, akşam sen onaylarsın.
- **Alternatif (bütçe sıfır):** Ev PC'sini açık bırak, **Windows Task Scheduler** ile
  zamanla. VPS almadan başlamak istersen bu yeterli.

### Deployment topolojisi (diyagram)

```
   ┌──────────────────────────┐        git push        ┌───────────────────────┐
   │   EV PC (Windows)         │  ───────────────────▶  │   GitHub repo         │
   │   - geliştirme            │                        │   (kaynak + geçmiş)   │
   │   - WPF/gömülü işleri      │  ◀───────────────────  │   .env ASLA burada yok │
   └──────────────────────────┘        git pull         └───────────┬───────────┘
                                                                      │ git pull (deploy)
                                                                      ▼
                                                     ┌────────────────────────────┐
                                                     │   VPS (Linux, 7/24)         │
                                                     │   - cron ile zamanlanmış     │
                                                     │   - ajanlar burada koşar     │
                                                     │   - .env (secrets) BURADA    │
                                                     │   - SQLite veritabanı        │
                                                     └───────────┬────────────────┘
                                                                 │ akşam
                                                                 ▼
                                                     ┌────────────────────────────┐
                                                     │   Sen: onay paneli / rapor   │
                                                     │   (taslakları onayla, gönder)│
                                                     └────────────────────────────┘
```

### Sırlar (secrets) nerede durur? — KRİTİK

- `.env` dosyası: `ANTHROPIC_API_KEY`, mail/SMTP bilgileri, DB yolu vb.
- **`.env` ASLA GitHub'a commit edilmez.** `.gitignore`'a eklenir.
- `.env` yalnızca **çalıştığın makinede** (ev PC ve/veya VPS) lokal durur.
- API anahtarı sızarsa fatura sana çıkar — bu yüzden bu kural pazarlık dışı.

### Geçici ortam uyarısı (bu Claude Code oturumu için)

Bu oturumun kendi container'ı **geçicidir** — saklanacak her şey commit + push
edilmeli. Bu doküman o yüzden repoya yazıldı. Senin gerçek runtime'ın ise ev
PC'n / VPS'in olacak, bu container değil.

---

## 2. Agentic Arka Ofis — mimari

**Felsefe:** Ajanlar *araştırır + taslaklar + triyaj yapar + raporlar* (asenkron,
sen işteyken). **Sen** onay kapısısın — LinkedIn'de toplu gönderim ve para hareketi
asla otonom değil (LinkedIn Q1 2026'da otomasyon tespitini sıkılaştırdı; para
regüle). Ajan çıktısı → senin akşam onayın → gerçek gönderim.

### Bileşenler / dosya yapısı (öngörülen)

```
agentic-gelir-sistemi/
├── .env.example              # şablon (gerçek .env gitignore'da)
├── requirements.txt          # anthropic, httpx, apscheduler/cron, sqlite3 ...
├── config.py                 # niş anahtar kelimeleri, model seçimi, eşikler
├── db/
│   └── schema.sql            # SQLite: leads, drafts, outreach_log, pipeline
├── agents/
│   ├── lead_research.py      # Upwork/Toptal/Wellfound/LinkedIn ilan tarama + skorlama (Haiku)
│   ├── proposal_draft.py     # ilan → kişiselleştirilmiş teklif taslağı (Opus/Sonnet)
│   ├── inbox_triage.py       # gelen mailleri sınıfla + yanıt taslağı (Haiku→Sonnet)
│   ├── content_draft.py      # LinkedIn post taslakları, build-in-public (Sonnet)
│   └── reporter.py           # günlük pipeline/gelir/saat özeti (Haiku)
├── core/
│   ├── llm.py                # Claude API sarmalayıcı (model kademeleme + retry)
│   ├── scoring.py            # ilan uygunluk skoru (firmware+GUI nişine göre)
│   └── store.py              # SQLite CRUD
├── scheduler.py              # cron/APScheduler: hangi ajan ne zaman koşar
└── dashboard/
    └── app.py                # basit yerel panel (onayla/gönder/reddet)
```

### Otomasyon seviyeleri (dürüst tablo)

| Görev | Seviye | Not |
|---|---|---|
| Pazar/iş ilanı araştırması | 🟢 Tam otomatik | "firmware + companion GUI" işlerini skorla, sabaha kuyruğa al |
| İçerik taslağı (LinkedIn) | 🟢 Yarı (AI taslak → sen onayla) | |
| Inbox triyaj + teklif taslağı | 🟢 Yarı | Akşam 1 saatini 3 saate çevirir |
| LinkedIn otomatik bağlantı/mesaj | 🔴 **YAPMA** | Ban riski; ajan sadece hedefi bulur + mesajı kişiselleştirir, **sen** elle gönderirsin (günde ≤20–30 bağlantı, ≤50 mesaj) |
| Ödeme yönetimi | 🟠 Sadece raporlama | Wise/Payoneer/Stripe + mali müşavir; ajan **para hareketi yapmaz** |

### Veri akışı (günlük döngü)

```
Gündüz (sen işteyken, VPS cron):
  lead_research → yeni ilanları skorla → DB'ye "queued"
  inbox_triage  → gelen mailleri sınıfla + taslakla → DB'ye "needs_review"
  content_draft → 1 LinkedIn post taslağı → DB'ye "needs_review"

Akşam (sen, 1–2 saat, dashboard):
  yüksek skorlu lead'leri gözden geçir → proposal_draft üret → onayla → gönder
  mail taslaklarını onayla/düzelt → gönder
  post taslağını onayla → paylaş

Hafta sonu:
  reporter özetini oku → nişi/skorlama eşiklerini ayarla → portföyü büyüt
```

### Model kademeleme kararı

- **Haiku 4.5:** her ilan için ucuz skorlama, mail sınıflama (yüksek hacim).
- **Sonnet 5 / Opus 4.8:** yalnızca *insan görecek* kaliteli metin (teklif, outreach).

---

## 3. Portföy Vitrin Projesi — mimari

**Amaç:** Moat'ını (firmware + Windows companion) kanıtlayan tek açık kaynak demo.
İlk müşteri görüşmene somut bir şeyle girmek = en hızlı gelir kaldıracı.

```
portfolio-demo/
├── firmware/                 # ESP32 veya STM32
│   ├── main.c / main.cpp     # sensör oku (örn. IMU/sıcaklık) + seri/BLE protokolü
│   └── protocol.md           # PC ile konuşma protokolü (framing, komutlar)
└── companion-app/            # C# WPF
    ├── SerialService.cs      # seri/USB/BLE bağlantı
    ├── LiveChartView.xaml     # gerçek zamanlı grafik/dashboard
    └── DeviceConfigView.xaml  # cihaz yapılandırma/kalibrasyon arayüzü
```

**Demo senaryosu:** ESP32 sensör verisini seri/BLE üzerinden gönderir; WPF uygulaması
gerçek zamanlı grafikte gösterir + cihazı yapılandırır. Bu, "cihaz + onu yöneten
Windows aracı" değer önerini birebir gösterir.

---

## 4. Teknoloji yığını (özet)

| Katman | Seçim | Neden |
|---|---|---|
| Ajan dili | **Python** | En hızlı yazılır, scraping/veri/ajan ekosistemi en zengin, cron ile 7/24 |
| LLM | **Claude API** | §0'daki gerekçeler |
| Zamanlama | **cron** (VPS) veya Task Scheduler (ev PC) | Basit, güvenilir |
| Veritabanı | **SQLite** | Tek dosya, sunucu gerektirmez, tek kişilik iş için fazlasıyla yeter |
| Panel | Basit **Flask/FastAPI** yerel dashboard | Onay kapısı |
| Portföy firmware | **C/C++** (ESP-IDF / STM32 HAL) | Senin alanın |
| Portföy UI | **C# WPF** | Senin alanın |

---

## 5. Yol haritası — inşa sırası (onaydan sonra)

1. **Repo iskeleti + `core/llm.py`** — Claude API sarmalayıcı (model kademeleme, retry).
2. **`db/schema.sql` + `core/store.py`** — leads/drafts/outreach tabloları.
3. **`agents/lead_research.py`** — ilan tarama + skorlama (ilk çalışan ajan, en yüksek değer).
4. **`dashboard/app.py`** — skorlanmış lead'leri gör/onayla.
5. **`agents/proposal_draft.py` + `inbox_triage.py`** — taslak üretimi.
6. **`scheduler.py`** — cron entegrasyonu, VPS'e deploy.
7. **Portföy demo** — ESP32 + WPF vitrin projesi (paralel yürüyebilir).

> Her adım bağımsız test edilir; §2'deki "önce lead_research" sırası kasıtlı —
> en somut değeri en erken verir.

---

## 6. Maliyet (aylık, gerçek rakamlar)

| Kalem | Tutar |
|---|---|
| VPS (Hetzner CX22 / DO) | ~$5 (≈235₺) |
| Claude API (kademeli kullanım) | ~$30–80 (≈1.400–3.750₺) |
| Mali müşavir (şahıs şirketi, %80 istisna için şart) | ~2.000–3.500₺ |
| Domain / soğuk e-posta aracı / küçük reklam testi | kalan bütçe |
| **Toplam** | **10.000₺ bütçenin altında, rahatça** |

---

## 7. Güvenlik & sınırlar (tekrar, çünkü önemli)

- `.env` / API anahtarı **asla** commit edilmez (`.gitignore`).
- LinkedIn: ajan **göndermez**, sadece hedefler + taslaklar; sen güvenli limitlerde elle gönderirsin.
- Ödeme: ajan **para hareketi yapmaz**, sadece raporlar.
- Savunma sanayi bağlamı: sözleşmenin gizlilik/rekabet/yan-iş maddeleri + güvenlik
  statüsü **önce** netleşmeli; hiçbir işveren projesi/bilgisi kullanılmaz; niş savunma
  DIŞI tutulur (çıkar çatışması yok).

---

## Sıradaki adım

Bu plan onaylanınca §5'teki sıradan başlayarak inşa edilir. İlk somut çıktı:
`core/llm.py` + `agents/lead_research.py` + basit dashboard — yani "gündüz ajan
firmware+GUI işlerini bulur, akşam sen onaylarsın" döngüsünün çalışan v1'i.
