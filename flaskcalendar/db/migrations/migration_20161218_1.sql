CREATE TABLE IF NOT EXISTS calendar_events (
    id BIGSERIAL PRIMARY KEY,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    person VARCHAR(512)
);
