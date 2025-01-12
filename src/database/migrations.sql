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
    email_address VARCHAR(255) NOT NULL,
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

-- 2024-11-27
CREATE FUNCTION enforce_subscribers_limit() RETURNS trigger AS $$
BEGIN
    IF (SELECT COUNT(*) FROM subscribers) >= 15 THEN
        RAISE EXCEPTION 'Subscription limit reached.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER subscribers_limit_trigger
BEFORE INSERT ON subscribers
FOR EACH ROW EXECUTE FUNCTION enforce_subscribers_limit();


-- 2025-01-12
ALTER TABLE subscribers
ADD COLUMN unsubscribe_token VARCHAR(255) NOT NULL DEFAULT 'initial_token';

ALTER TABLE alerts_sent
ADD COLUMN email_address VARCHAR(255) NOT NULL;

ALTER TABLE alerts_sent
DROP COLUMN subscriber_id;

ALTER TABLE alerts_sent
ADD CONSTRAINT alerts_sent_manga_alert_email_unique
UNIQUE (manga_release_id, alert_type, email_address);


