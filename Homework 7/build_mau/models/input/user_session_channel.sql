WITH user_data AS (
    SELECT
	userId, sessionId, channel
	FROM {{ source('raw', 'user_session_channel') }}
	WHERE sessionId IS NOT NULL
)

SELECT
    userId,
    sessionId,
    channel
FROM user_data


