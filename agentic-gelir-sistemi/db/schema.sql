-- Agentic gelir sistemi — SQLite şeması (v1)
-- Bu dosya boru hattının kalıcı hafızası. Demo yalnızca leads tablosunu kullanır;
-- diğerleri sonraki ajanlar için hazır duruyor.

CREATE TABLE IF NOT EXISTS leads (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  title       TEXT NOT NULL,
  source      TEXT,               -- upwork / toptal / linkedin ...
  score       INTEGER,            -- 0-100 niş uyum skoru
  reason      TEXT,               -- skorun kısa gerekçesi
  skills      TEXT,               -- JSON: eşleşen anahtar beceriler
  status      TEXT DEFAULT 'queued',   -- queued / reviewed / pursuing / dropped
  created_at  TEXT
);

-- İleride kullanılacak (proposal_draft / inbox_triage ajanları için) — şimdilik boş:
CREATE TABLE IF NOT EXISTS drafts (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  lead_id     INTEGER,
  kind        TEXT,               -- proposal / email_reply / linkedin_post
  body        TEXT,
  status      TEXT DEFAULT 'needs_review',  -- needs_review / approved / sent
  created_at  TEXT,
  FOREIGN KEY(lead_id) REFERENCES leads(id)
);
