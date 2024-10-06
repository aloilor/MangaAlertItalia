---- 2024-10-06
-- Create the manga_releases table
CREATE TABLE IF NOT EXISTS manga_releases (
    id SERIAL PRIMARY KEY,
    manga_title VARCHAR(255) NOT NULL,
    volume_number VARCHAR(50) NOT NULL,
    release_date DATE,
    publisher VARCHAR(255),
    alert_sent BOOLEAN NOT NULL DEFAULT FALSE
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
    manga_title VARCHAR(255) NOT NULL,
    PRIMARY KEY (subscriber_id, manga_title)
);
