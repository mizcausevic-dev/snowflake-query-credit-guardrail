-- Export a redacted Snowflake query-history sample for offline guardrail review.
-- Do not export raw query text or account identifiers into public fixtures.

select
  query_hash,
  warehouse_name as warehouse,
  warehouse_size,
  coalesce(user_name, 'unassigned') as owner,
  coalesce(query_tag, 'untagged') as tag_status,
  coalesce(role_name, 'unknown') as business_unit,
  credits_used_cloud_services + credits_used_compute as credits,
  bytes_scanned,
  total_elapsed_time / 1000 as execution_seconds,
  rows_produced,
  case
    when percentage_scanned_from_cache >= 75 then true
    else false
  end as cache_hit,
  case
    when query_type in ('COPY', 'UNLOAD') then 'regulated'
    else 'internal'
  end as classification
from snowflake.account_usage.query_history
where start_time >= dateadd(day, -30, current_timestamp())
  and warehouse_name is not null
  and execution_status = 'SUCCESS'
order by credits desc
limit 500;

