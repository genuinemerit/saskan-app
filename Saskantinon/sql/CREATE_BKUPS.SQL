CREATE TABLE IF NOT EXISTS bkups (
    bkup_dttm TEXT PRIMARY KEY,
    bkup_nm TEXT NOT NULL,
    bkup_type TEXT NOT NULL,
    bkup_object BLOB NOT NULL
);
