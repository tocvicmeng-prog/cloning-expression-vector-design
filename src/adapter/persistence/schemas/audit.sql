CREATE TABLE IF NOT EXISTS audit_entries (
    entry_id TEXT PRIMARY KEY,
    sequence_number INTEGER NOT NULL UNIQUE,
    entry_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    occurred_at_utc TEXT NOT NULL,
    key_version INTEGER NOT NULL,
    prev_mac BLOB NOT NULL,
    row_mac BLOB NOT NULL
);
