"""LLM adaptörü — mock ve (ileride) api modu.

MOCK modda HİÇBİR API çağrılmaz, kuruş harcanmaz; sadece boru hattını test etmek için
kural-tabanlı sahte bir "beyin" çalıştırır. Gerçek moda geçiş TEK YERDEN olur:
  1) LLM_MODE=api ortam değişkeni + ANTHROPIC_API_KEY
  2) aşağıdaki _call_api() fonksiyonunu doldur
Ajan kodları değişmez — sadece bu dosya. "Dişliyi test et, sonra motoru bağla" mantığı.
"""
import os

MODE = os.getenv("LLM_MODE", "mock")  # "mock" | "api"

# Niş anahtar kelimeleri (skorlama sezgisi) — gerçek modda bunun yerine Claude karar verir
FIRMWARE_KW = ["stm32", "esp32", "firmware", "embedded", "gömülü", "gomulu", "rtos",
               "fpga", "microcontroller", "mcu", "bare metal", "bare-metal", "freertos"]
GUI_KW = ["wpf", "desktop", "masaüstü", "masaustu", "gui", "c#", ".net", "companion",
          "config tool", "configuration tool", "dashboard", "arayüz", "arayuz"]


# Olumsuzlama işaretleri — "no embedded", "no GUI", "without desktop", "GUI yok" ...
# NOT: bu bile kırılgan bir sezgi. Gerçek modda Claude bağlamı okuyup doğru karar verir.
_NEG = ["no ", "no-", "without", "n't", "yok", "değil", "olmadan", "gerekmez", "gerekli değil"]


def _present(t: str, kw: str) -> bool:
    """kw metinde geçiyor mu — ama hemen öncesinde olumsuzlama yoksa."""
    idx = t.find(kw)
    while idx != -1:
        window = t[max(0, idx - 20):idx]
        if not any(n in window for n in _NEG):
            return True
        idx = t.find(kw, idx + 1)
    return False


def _score_lead(text: str) -> dict:
    """Sahte skorlama: gerçek modda Claude Haiku'nun yapacağı işi kabaca taklit eder."""
    t = text.lower()
    matched_fw = [k for k in FIRMWARE_KW if _present(t, k)]
    matched_gui = [k for k in GUI_KW if _present(t, k)]
    fw, gui = bool(matched_fw), bool(matched_gui)

    if fw and gui:
        score, reason = 90, "Firmware + companion GUI birlikte — tam niş uyumu (senin moat'ın)."
    elif fw:
        score, reason = 55, "Firmware var ama companion GUI yok — kısmi uyum."
    elif gui:
        score, reason = 40, "Masaüstü/GUI var ama gömülü taraf yok — kısmi uyum."
    else:
        score, reason = 10, "Niş dışı — firmware/companion GUI eşleşmesi yok."

    skills = list(dict.fromkeys(matched_fw + matched_gui))  # tekrarsız, sıralı
    return {"score": score, "reason": reason, "skills": skills}


_MOCK_HANDLERS = {
    "score_lead": _score_lead,
    # ileride: "draft_proposal", "triage_email", ...
}


def complete_json(*, task: str, user: str, model: str = "mock", system: str = "") -> dict:
    """Tek giriş noktası. Ajanlar hep bunu çağırır; mod farkını fark etmezler."""
    if MODE == "mock":
        return _MOCK_HANDLERS[task](user)
    return _call_api(task=task, model=model, system=system, user=user)


def _call_api(*, task, model, system, user):
    """Gerçek moda geçince doldurulacak. Şu an bilerek bağlı değil (mock ile test ediyoruz).

    Doldurulacak hali (Claude API):
        from anthropic import Anthropic
        client = Anthropic()
        resp = client.messages.create(
            model=model, system=system, max_tokens=512,
            output_config={"format": {"type": "json_schema", "schema": SCHEMAS[task]}},
            messages=[{"role": "user", "content": user}],
        )
        import json
        return json.loads(next(b.text for b in resp.content if b.type == "text"))
    """
    raise NotImplementedError(
        "API modu henüz bağlı değil — önce mock ile boru hattını doğruluyoruz. "
        "Hazır olunca _call_api doldurulacak ve LLM_MODE=api yapılacak."
    )
