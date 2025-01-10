# Manga Alerts Database Schema Documentation

**Last DB Update**: 2024-11-27

This documentation describes the database schema for managing manga releases, subscribers, and alerts. The schema includes tables for storing release and subscriber data, as well as a trigger function that enforces a subscriber limit.

---

## 1. Table: `manga_releases`
**Creation Date**: 2024-10-06  
**Purpose**: Holds information about upcoming manga releases.

| Column         | Type            | Description                                                            |
|----------------|-----------------|------------------------------------------------------------------------|
| `id`           | `SERIAL`        | Primary key (auto-increment)                                          |
| `manga_title`  | `VARCHAR(255)`  | Name of the manga series (required)                                   |
| `volume_number`| `VARCHAR(50)`   | Volume identifier (required, e.g., "Vol. 1", "Volume 10")             |
| `release_date` | `DATE`          | Date of the manga’s release (optional)                                |
| `publisher`    | `VARCHAR(255)`  | Publisher name (required)                                             |
| `page_link`    | `VARCHAR(255)`  | URL linking to more information (required)                            |
| `alert_sent`   | `BOOLEAN`       | Defaults to `FALSE`; indicates if an overall alert was sent (not individual alerts) |
| **Constraint** | `UNIQUE`        | `(manga_title, volume_number, release_date)` prevents duplicates      |

**Use Cases**  
- Central record of all manga releases.  
- Key reference in sending alerts or listing upcoming volumes.

---

## 2. Table: `subscribers`
**Creation Date**: 2024-10-06  
**Purpose**: Holds basic subscriber data (email addresses).

| Column            | Type           | Description                                          |
|-------------------|---------------|------------------------------------------------------|
| `id`              | `SERIAL`       | Primary key (auto-increment)                        |
| `email_address`   | `VARCHAR(255)` | Unique, required email address of the subscriber    |

**Use Cases**  
- Stores each user who wants to receive manga alerts.  
- Used in conjunction with subscriptions and alerts tracking.

---

## 3. Table: `subscribers_subscriptions`
**Creation Date**: 2024-10-06  
**Purpose**: Connects subscribers to the manga titles they follow.

| Column           | Type            | Description                                                                            |
|------------------|-----------------|----------------------------------------------------------------------------------------|
| `subscriber_id`  | `INTEGER`       | References `subscribers(id)`, indicates which subscriber is following a manga          |
| `email_address`  | `VARCHAR(255)`  | Stores subscriber’s email again for convenience                                        |
| `manga_title`    | `VARCHAR(255)`  | The manga title the subscriber wants updates for                                       |
| **Constraint**   | `PRIMARY KEY`   | `(subscriber_id, manga_title)` ensures one unique subscription entry per subscriber-title pair |

**Use Cases**  
- Determines which subscribers need alerts for specific manga releases.  

---

## 4. Table: `alerts_sent`
**Creation Date**: 2024-10-10  
**Purpose**: Tracks individual alerts sent out for each manga release to each subscriber.

| Column            | Type            | Description                                                                 |
|-------------------|-----------------|-----------------------------------------------------------------------------|
| `id`              | `SERIAL`        | Primary key (auto-increment)                                               |
| `subscriber_id`   | `INTEGER`       | References `subscribers(id)`, identifies the subscriber                     |
| `manga_release_id`| `INTEGER`       | References `manga_releases(id)`, identifies the specific manga release      |
| `alert_type`      | `VARCHAR(20)`   | Provides context for the alert (e.g., `on_subscription`, `1_month`, etc.)    |
| `alert_sent`      | `BOOLEAN`       | Defaults to `FALSE`; indicates if the alert was successfully sent           |
| **Constraint**    | `UNIQUE`        | `(subscriber_id, manga_release_id, alert_type)` prevents duplicated alerts  |

**Use Cases**  
- Verifies if a subscriber has already been notified about a particular release.  

---

## 5. Trigger Function: `enforce_subscribers_limit`
**Purpose**: Limits the number of subscribers to a maximum threshold (15 in this example).

### 5.1 Function Definition
```sql
CREATE FUNCTION enforce_subscribers_limit() RETURNS trigger AS $$
BEGIN
    IF (SELECT COUNT(*) FROM subscribers) >= 15 THEN
        RAISE EXCEPTION 'Subscription limit reached.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```
**Logic**:
- Checks the total number of rows in the subscribers table.
- Throws an exception if the total is 15 or more, disallowing new inserts.

### 5.2 Trigger: subscribers_limit_trigger
```sql
CREATE TRIGGER subscribers_limit_trigger
BEFORE INSERT ON subscribers
FOR EACH ROW EXECUTE FUNCTION enforce_subscribers_limit();
```
- Activated before each insert on subscribers.
- Ensures no new subscriber can be added once the limit is reached.

**Use Cases**:
- Protects against an excessive number of subscriptions.



