WITH session_data AS (
    SELECT
        sessionId,
        ts
    FROM {{ source('raw', 'session_timestamp') }}
    WHERE sessionId IS NOT NULL
)

SELECT
    sessionId,
    ts
FROM session_data