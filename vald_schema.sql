
-- 1. CMJ (Counter Movement Jump)
CREATE OR REPLACE EXTERNAL TABLE `ycgcenter.YCGCenter_db.vald_cmj`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1GEcs_PjxASKdMbOwmgMbk9NjimpiYxd0ql-RyN5FZ6g/edit?usp=sharing'],
  sheet_range = 'CMJ',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 2. Nordbord
CREATE OR REPLACE EXTERNAL TABLE `ycgcenter.YCGCenter_db.vald_nordbord`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1GEcs_PjxASKdMbOwmgMbk9NjimpiYxd0ql-RyN5FZ6g/edit?usp=sharing'],
  sheet_range = 'Nordbord',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 3. ForceFrame
CREATE OR REPLACE EXTERNAL TABLE `ycgcenter.YCGCenter_db.vald_forceframe`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1GEcs_PjxASKdMbOwmgMbk9NjimpiYxd0ql-RyN5FZ6g/edit?usp=sharing'],
  sheet_range = 'ForceFrame',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 4. SJ (Squat Jump)
CREATE OR REPLACE EXTERNAL TABLE `ycgcenter.YCGCenter_db.vald_sj`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1GEcs_PjxASKdMbOwmgMbk9NjimpiYxd0ql-RyN5FZ6g/edit?usp=sharing'],
  sheet_range = 'SJ',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 5. HJ (Hop Jump / Other)
CREATE OR REPLACE EXTERNAL TABLE `ycgcenter.YCGCenter_db.vald_hj`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1GEcs_PjxASKdMbOwmgMbk9NjimpiYxd0ql-RyN5FZ6g/edit?usp=sharing'],
  sheet_range = 'HJ',
  skip_leading_rows = 1,
  max_bad_records = 0
);
