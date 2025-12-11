-- Verify raw_data_tracking_by_year exists and see what fields it has
SELECT
  data_year,
  total_bills,

  -- Key tracking percentages that would be useful for a dashboard
  abortion_tracking_pct,
  contraception_tracking_pct,
  bill_type_tracking_pct,
  introduced_date_tracking_pct,
  intent_tracking_pct

FROM `guttmacher-legislative-tracker.legislative_tracker_historical.raw_data_tracking_by_year`
WHERE data_year >= 2020
ORDER BY data_year DESC
LIMIT 5;
