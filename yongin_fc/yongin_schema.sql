-- Yongin FC BigQuery Schema Setup
-- Project ID: yonginfc
-- Sheet URL: https://docs.google.com/spreadsheets/d/1M7K8SwfAulrto3G9p97a4ENfYerHIh6VFpALvj17mf0/edit

-- 1. Nordbord
CREATE OR REPLACE EXTERNAL TABLE `yonginfc.vald_data.vald_nordbord`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1M7K8SwfAulrto3G9p97a4ENfYerHIh6VFpALvj17mf0/edit'],
  sheet_range = 'Nordbord',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 2. ForceFrame
CREATE OR REPLACE EXTERNAL TABLE `yonginfc.vald_data.vald_forceframe`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1M7K8SwfAulrto3G9p97a4ENfYerHIh6VFpALvj17mf0/edit'],
  sheet_range = 'Forceframe',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 3. CMJ
CREATE OR REPLACE EXTERNAL TABLE `yonginfc.vald_data.vald_cmj`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1M7K8SwfAulrto3G9p97a4ENfYerHIh6VFpALvj17mf0/edit'],
  sheet_range = 'CMJ',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 4. SJ
CREATE OR REPLACE EXTERNAL TABLE `yonginfc.vald_data.vald_sj`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1M7K8SwfAulrto3G9p97a4ENfYerHIh6VFpALvj17mf0/edit'],
  sheet_range = 'SJ',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 5. HopTest
CREATE OR REPLACE EXTERNAL TABLE `yonginfc.vald_data.vald_hoptest`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1M7K8SwfAulrto3G9p97a4ENfYerHIh6VFpALvj17mf0/edit'],
  sheet_range = 'HopTest',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 6. All Data
CREATE OR REPLACE EXTERNAL TABLE `yonginfc.vald_data.vald_all_data`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1M7K8SwfAulrto3G9p97a4ENfYerHIh6VFpALvj17mf0/edit'],
  sheet_range = 'All Data',
  skip_leading_rows = 1,
  max_bad_records = 0
);
