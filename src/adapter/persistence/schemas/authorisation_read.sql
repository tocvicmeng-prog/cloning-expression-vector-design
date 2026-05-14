CREATE TABLE IF NOT EXISTS authorisation_profiles (
    profile_id TEXT PRIMARY KEY,
    subject_user_id TEXT NOT NULL,
    profile_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_authorisation_profiles_subject
ON authorisation_profiles(subject_user_id);
