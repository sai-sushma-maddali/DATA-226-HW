
## Airflow ETL & ELT DAGs for Snowflake

### Overview

This project contains two Airflow DAGs that demonstrate a complete ETL + ELT pipeline using Snowflake:

- **ETL DAG (`etl_session_data_to_snowflake`)**:  
  Loads raw CSV data from an S3 bucket into Snowflake staging tables.
  
- **ELT DAG (`elt_snowflake_dag`)**:  
  Transforms the raw data by joining two tables and creating a cleaned, analytics-ready table with integrity checks.

---

### DAG 1: ETL — Load Raw Data into Snowflake

**DAG ID**: `etl_session_data_to_snowflake`  
**Schedule**: Every 15 minutes (`*/15 * * * *`)  
**Purpose**:  
- Create raw tables: `raw.user_session_channel` and `raw.session_timestamp`
- Create a Snowflake stage pointing to S3
- Load CSV files into Snowflake using `COPY INTO`

**Key Features**:
- Uses `SnowflakeHook` for secure connection
- Wraps operations in a transaction (`BEGIN`, `COMMIT`, `ROLLBACK`)
- Handles errors gracefully with rollback and logging

---

### DAG 2: ELT — Transform and Validate Data

**DAG ID**: `elt_snowflake_dag`  
**Schedule**: Daily at 2:45 AM (`45 2 * * *`)  
**Purpose**:  
- Join raw tables to create `analytics.session_summary`
- Validate data integrity before publishing

**Transformation Logic**:
```sql
SELECT u.*, s.ts
FROM raw.user_session_channel u
JOIN raw.session_timestamp s ON u.sessionId = s.sessionId
```

**Validation Steps**:
1. **Primary Key Uniqueness Check** on `sessionId`
2. **Full Row Duplicate Check** using:
   ```sql
   SELECT COUNT(*) AS total_rows,
          COUNT(DISTINCT USERID, SESSIONID, CHANNEL, TS) AS distinct_rows
   ```

**Publishing Logic**:
- Creates a temp table via `CREATE OR REPLACE`
- Swaps it atomically into place using `ALTER TABLE ... SWAP`

---

### Setup Instructions

1. **Airflow Connection**:
   - Add a Snowflake connection in Airflow UI:
     - `Conn Id`: `snowflake_conn`
     - `Conn Type`: `Snowflake`
     - Fill in account, user, password, database, warehouse, etc.

2. **S3 Access**:
   - Ensure Snowflake has access to the S3 bucket: `s3://s3-geospatial/readonly/`
   - Files expected:
     - `user_session_channel.csv`
     - `session_timestamp.csv`

3. **Deploy DAGs**:
   - Place both Python files in your Airflow `dags/` directory.
   - Start Airflow scheduler and webserver.

---



