-- Run once after terraform apply to initialise the sentinel database schema.
-- psql postgres://sentinel:<password>@<rds_endpoint>/sentinel -f migrate.sql

CREATE TABLE IF NOT EXISTS tasks (
    task_id      TEXT PRIMARY KEY,
    status       TEXT        NOT NULL,
    intent       TEXT,
    agent_result TEXT,
    error        TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id         BIGSERIAL PRIMARY KEY,
    task_id    TEXT        NOT NULL,
    entry      JSONB       NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS audit_log_task_id_idx ON audit_log (task_id);
