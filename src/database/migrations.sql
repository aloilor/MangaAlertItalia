-- 2024-10-06
-- Create the manga_releases table
CREATE TABLE IF NOT EXISTS manga_releases (
    id SERIAL PRIMARY KEY,
    manga_title VARCHAR(255) NOT NULL,
    volume_number VARCHAR(50) NOT NULL,
    release_date DATE,
    publisher VARCHAR(255) NOT NULL,
    page_link VARCHAR(255) NOT NULL,
    alert_sent BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(manga_title, volume_number, release_date)
);

-- Create the subscribers table
CREATE TABLE IF NOT EXISTS subscribers (
    id SERIAL PRIMARY KEY,
    email_address VARCHAR(255) NOT NULL UNIQUE
);

-- Create map subscribers to their subscriptions
CREATE TABLE IF NOT EXISTS subscribers_subscriptions (
    subscriber_id INTEGER NOT NULL REFERENCES subscribers(id),
    email_address VARCHAR(255) NOT NULL UNIQUE,
    manga_title VARCHAR(255) NOT NULL,
    PRIMARY KEY (subscriber_id, manga_title)
);

-- 2024-10-10
CREATE TABLE IF NOT EXISTS alerts_sent (
    id SERIAL PRIMARY KEY,
    subscriber_id INTEGER NOT NULL REFERENCES subscribers(id),
    manga_release_id INTEGER NOT NULL REFERENCES manga_releases(id),
    alert_type VARCHAR(20) NOT NULL,  -- e.g., 'on_subscription', '1_month', '1_week', '1_day'
    alert_sent BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (subscriber_id, manga_release_id, alert_type)
);

