DECLARE start_date, end_date DATE;
SET start_date = DATE("{{ start_date }}");
SET end_date = DATE("{{ end_date }}");

WITH
auditlog AS (
  SELECT *
  FROM `{{ project }}.{{ dataset }}.cloudaudit_googleapis_com_data_access_*`
  WHERE
    _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', start_date)
                      AND FORMAT_DATE('%Y%m%d', end_date)
    AND resource.type = "bigquery_resource"
)
, job_compoeted AS (
  SELECT *
  FROM auditlog
  WHERE
    protopayload_auditlog.methodName = "jobservice.jobcompleted"
    AND protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatus.state = "DONE"
)
, insert AS (
  SELECT *
  FROM auditlog
  WHERE
    protopayload_auditlog.methodName = "jobservice.insert"
    AND protopayload_auditlog.servicedata_v1_bigquery.jobInsertResponse.resource.jobStatus.state = "DONE"
)
, unioned AS (
  SELECT * FROM job_compoeted
  UNION ALL
  SELECT * FROM insert
)

SELECT * FROM unioned
ORDER BY timestamp
LIMIT {{ limit|default(100000, true)}}