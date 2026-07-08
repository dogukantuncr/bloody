"""Mock deneme — API/Agent SDK KULLANMADAN tüm boru hattını test eder.

Akış: örnek ilanları yükle → lead_research ajanı skorla → SQLite'a yaz → listele.
Çalıştır:  python3 run_demo.py
Maliyet:   0₺ (hiçbir API çağrılmaz; LLM_MODE=mock)
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import store
from agents import lead_research


def main():
    store.init_db()

    # İsteğe bağlı: python3 run_demo.py data/live_listings.json  (canlı çekilen gerçek ilanlar)
    default = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_listings.json")
    data_path = sys.argv[1] if len(sys.argv) > 1 else default
    with open(data_path, encoding="utf-8") as f:
        listings = json.load(f)

    print(f"\n{len(listings)} örnek ilan yüklendi. İlan Avcısı (mock) skorluyor...\n")
    scored = lead_research.run(listings)

    for s in scored:
        store.upsert_lead(s["title"], s.get("source", "demo"), s["score"], s["reason"], s["skills"])

    print("=" * 70)
    print("  SKORLANMIŞ LEAD'LER (yüksekten düşüğe) — akşam dashboard'da göreceğin şey")
    print("=" * 70)
    for r in store.top_leads():
        bar = "█" * (r["score"] // 10)
        print(f"\n[{r['score']:>3}] {bar}")
        print(f"      {r['title']}  ({r['source']})")
        print(f"      neden : {r['reason']}")
        print(f"      eşleşme: {json.loads(r['skills']) or '—'}")
        print(f"      durum : {r['status']}")
    print()


if __name__ == "__main__":
    main()
