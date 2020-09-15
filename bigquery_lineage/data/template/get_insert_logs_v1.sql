DECLARE start_date, end_date DATE;
SET start_date = DATE("{{ start_date }}");
SET end_date = DATE("{{ end_date }}");

WITH
insert_jobs AS (
  SELECT *
  FROM `{{ project }}.{{ dataset }}.cloudaudit_googleapis_com_data_access_*`
  WHERE
    _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', start_date)
                      AND FORMAT_DATE('%Y%m%d', end_date)
    AND resource.type = "bigquery_resource"
    AND protopayload_auditlog.methodName = "jobservice.insert"
    AND protopayload_auditlog.servicedata_v1_bigquery.jobInsertResponse.resource.jobStatus.state = "DONE"
)

SELECT * FROM insert_jobs
LIMIT {{ limit|default(100000, true)}}