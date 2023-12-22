UPDATE bkups
SET bkup_nm = ?,
    bkup_type = ?,
    bkup_object = ?
WHERE bkup_dttm = ?;
