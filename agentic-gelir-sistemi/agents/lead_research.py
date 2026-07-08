"""Ajan #1 — İlan Avcısı.

İş ilanlarını 'firmware + companion GUI' nişine uyumuna göre skorlar.
Mock modda kural-tabanlı, api modda Claude Haiku ile — ama bu kod her iki modda AYNI.
"""
from core import llm

SYSTEM = ("Sen bir freelance iş ilanı skorlama ajanısın. Uzmanlık nişi: gömülü firmware "
          "(STM32/ESP32/FPGA/RTOS) + bu cihazlarla entegre C# WPF masaüstü/companion araçları. "
          "Her ilanı bu nişe uyumuna göre 0-100 arası skorla.")


def score_listing(listing: dict) -> dict:
    text = f"{listing['title']}\n{listing.get('description', '')}"
    result = llm.complete_json(
        task="score_lead",
        user=text,
        model="claude-haiku-4-5",
        system=SYSTEM,
    )
    return {**listing, **result}


def run(listings: list[dict]) -> list[dict]:
    return [score_listing(l) for l in listings]
