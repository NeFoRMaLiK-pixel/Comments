-- PostgreSQL schema snapshot for the Comments SPA test task.

CREATE TABLE comments_comment (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT NULL REFERENCES comments_comment(id) ON DELETE CASCADE,
    username VARCHAR(64) NOT NULL,
    email VARCHAR(254) NOT NULL,
    homepage VARCHAR(200) NOT NULL DEFAULT '',
    text_raw TEXT NOT NULL,
    text_html TEXT NOT NULL,
    attachment VARCHAR(100) NULL,
    attachment_type VARCHAR(10) NOT NULL DEFAULT 'none',
    attachment_name VARCHAR(255) NOT NULL DEFAULT '',
    ip_address INET NULL,
    user_agent VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX comments_comment_created_idx ON comments_comment(created_at);
CREATE INDEX comments_comment_username_idx ON comments_comment(username);
CREATE INDEX comments_comment_email_idx ON comments_comment(email);
CREATE INDEX comments_comment_parent_created_idx ON comments_comment(parent_id, created_at);

CREATE TABLE comments_commentevent (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(64) NOT NULL,
    comment_id BIGINT NOT NULL REFERENCES comments_comment(id) ON DELETE CASCADE,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX comments_commentevent_created_idx ON comments_commentevent(created_at);
CREATE INDEX comments_commentevent_type_idx ON comments_commentevent(event_type);
