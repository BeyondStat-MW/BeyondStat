
-- All Data (Aggregated Sheet)
-- Columns: Player ID, Name, Date, Height, Weight, Hamstring_Ecc..., CMJ..., SJ...
CREATE OR REPLACE EXTERNAL TABLE `gangwonfc.vald_data.vald_all_data`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1TKxBm1wyTxLdhVmP8Q9xDKILmRDV_eYvqEjaDJSvIio/edit'],
  sheet_range = 'All Data',
  skip_leading_rows = 1,
  max_bad_records = 0
);
