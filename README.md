## Manga Alert Italia - Manga Releases Tracker and Notification System ##
![visitors](https://visitor-badge.laobi.icu/badge?page_id=aloilor/MangaAlertItalia)  

<p align="center"> <a href="https://mangaalertitalia.it/">
   <img src="./assets/logo-with-white-bg-crop.png" align="right" width="150" />
</a></p>

Manga Alert Italia is a full-stack application that tracks physical manga releases in Italy by scraping publishers’ websites, storing upcoming releases in a database, and sending out timely email notifications to subscribers. The service ensures readers never miss a volume release by automatically sending reminders at key intervals: one month, one week, and one day before a manga volume hits the shelves. 

---

## TODO ##
- [x] CDN ACM Certificates
- [x] Request AWS SES production access - Rejected by AWS, gotta find another way
- [x] Respawn main backend instances after generating the new SSL certificates
- [x] Setup SendGrid to replace AWS SES
- [x] Footer with rights and links to LinkedIn and GitHub
- [x] Unsubscribe API and link inside the emails
- [x] Informazioni page on the frontend
- [ ] Telegram Bot to send notifications
- [ ] Finish to write documentation


## Table of Contents ##
1. [Features](#features)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
6. [Setup & Installation](#setup--installation)
7. [Usage](#usage)
8. [Testing](#testing)
9. [CI/CD & Deployment](#cicd--deployment)
10. [License](#license)
11. [Contacts](#contacts)


## Features ##
1. **Scraping**: 
   - Uses Python’s `requests` and `BeautifulSoup` to scrape official publisher websites.
   - Automates the data extraction process, storing manga titles, release dates, publishers, and relevant page links.

2. **Subscription Service**: 
   - Users subscribe via a **React** front-end hosted on AWS S3.  
   - They choose their favorite manga titles (e.g., *Solo Leveling*, *Chainsaw Man*, *Jujutsu Kaisen*).
   - The system enforces a maximum subscriber limit (e.g., 15) with a trigger in PostgreSQL.

3. **Unsubscription Service**:  
   - Users can unsubscribe via a unique token representing user identities embedded in each email.  
   - A dedicated endpoint on the backend (`/unsubscribe/<token>`) handles user removal and subscription data cleanup.

4. **Notification Emails**:  
   - Sends reminder emails through **SendGrid** (with AWS Secrets Manager storing the API key).
   - Three notifications per volume:  
     - 1 month before release  
     - 1 week before release  
     - 1 day before release  

5. **SSL Certificate Management**:
   - Integrates **Let’s Encrypt** with **AWS Lambda** for automated certificate renewal.
   - Stores certificates in **AWS Secrets Manager**.


## Architecture ##

1. **Scraper** (Python):
   - Periodically runs to fetch new manga volume information from publisher websites.
   - Uses Python libraries `requests` and `BeautifulSoup` for HTML parsing and data extraction.
   - Populates the `manga_releases` table in PostgreSQL with titles, release dates, publishers, and links.
   - Runs as a scheduled task using **AWS EventBridge** to ensure periodic execution.
   - Hosted through **AWS ECS** as a containerized task.

2. **Backend (Flask API)**:
   - Provides RESTful endpoints for user interactions and data retrieval.
     - `/subscribe`: Allows users to subscribe to manga release alerts, enforcing a maximum of 15 subscribers per title.
     - `/unsubscribe/<token>`: Handles secure unsubscriptions using a unique token.
   - Communicates with PostgreSQL to manage subscribers, subscriptions, and release schedules.
   - Secures sensitive credentials such as the database connection string using **AWS Secrets Manager**.
   - Deployed as a containerized Flask application running on **AWS ECS**, with high availability through auto-scaling.

3. **Email Notifier**:
   - Sends automated notification emails to subscribers at three key intervals:
     - 1 month before release.
     - 1 week before release.
     - 1 day before release.
   - Utilizes **SendGrid** for email delivery, with API keys securely stored in **AWS Secrets Manager**.
   - Each email contains a unique, tokenized unsubscribe link to facilitate secure one-click opt-out.
   - Runs as a scheduled job using **AWS EventBridge**, triggering an ECS task to process notifications.
   - Ensures compliance with email best practices by integrating with **AWS Route 53** for domain verification and SPF/DKIM/DMARC email authentication.

4. **Database**:
   - Uses **PostgreSQL**, hosted on **AWS RDS**, to store and manage:
     - User subscriptions and preferences.
     - Manga release schedules and notifications.
   - Schema includes tables for tracking subscribers, upcoming releases, and email logs.
   - Enforces a subscription limit of 15 users through database triggers.

5. **Front-End (React)**:
   - Developed using **React**, providing a user-friendly interface for managing subscriptions.
   - Deployed as a static website on **AWS S3**, utilizing **AWS CloudFront** for global content delivery and caching.
   - Implements a client-side router (`BrowserRouter`) to handle navigation seamlessly.
   - Key features include:
     - Subscription form for entering email and selecting manga titles.
     - Unsubscribe page that processes secure opt-outs via tokenized links.
     - Informazioni page with an FAQ section, privacy policy, and contact details.

6. **CI/CD & Deployment**:
   - **GitHub Actions** handles automated testing, Docker image builds, and deployments.
   - CI/CD pipeline includes:
     - Unit tests with `pytest` and `unittest.mock`  to achieve 85%+ code coverage.
     - Docker images built and pushed to **AWS ECR**.
     - Deployment to **AWS ECS**, ensuring zero downtime with rolling updates.
   - **Terraform** is used to define and manage AWS infrastructure.
   - SSL certificates are managed with **Let’s Encrypt**, using AWS Lambda for automatic renewal and storage in **AWS Secrets Manager**.


## Tech Stack ## 

| **Technology**       | **Purpose**                                                     |
|----------------------|-----------------------------------------------------------------|
| **Python**           | Main backend language for web scraping, data handling, and notifications. |
| **Requests**         | Library for HTTP requests during publisher website scraping.    |
| **BeautifulSoup**    | Library for HTML parsing and data extraction from publisher pages. |
| **Flask**            | Python web framework providing RESTful endpoints (subscribe, unsubscribe, etc.). |
| **pytest / unittest.mock** | Testing libraries for Python, ensuring 85%+ code coverage.|
| **React** / **React Router** | Front-end library for building a single-page application (SPA), including subscription forms and unsubscribe pages. |
| **React-Bootstrap**  | UI styling and responsive layout for the SPA.                   |
| **PostgreSQL (AWS RDS)** | AWS-hosted database storing subscribers, manga releases, and alerts. |
| **AWS Route 53**     | Handles domain management, DNS, and DMARC TXT records for email authentication. |
| **AWS CloudWatch**   | Monitors logs and application performance for debugging and alerts. |
| **AWS CloudFront**   | Content Delivery Network (CDN) caching the front-end website. |
| **AWS EC2**          | Hosts the main backend and cron jobs for scheduled tasks. |
| **AWS EventBridge**  | Triggers cron jobs for the scraper and email notifications. |
| **AWS Secrets Manager** | Secure storage for SendGrid API key, SSL certificates, RDS authentication and other sensitive data. |
| **AWS ECR**          | Hosting Docker images.                                          |
| **AWS ECS**          | Orchestration of Docker containers with rolling deployments.    |
| **AWS S3**           | Static hosting for the React front-end.                         |
| **AWS VPC**          | Private networking for ECS tasks and secure communication.      |
| **Docker**           | Containerization of backend services for consistent deployment. |
| **GitHub Actions**   | CI/CD pipeline for automatic testing, building, and deploying.  |
| **Terraform**        | Infrastructure as Code (IaC) to provision and manage AWS resources. |
| **Let’s Encrypt**    | SSL certificate provider integrated via AWS Lambda for automated renewal. |
| **SendGrid**         | Email service used to send notifications to subscribers.        |

## Setup & Installation ##


## Usage ##


## Testing ## 


## CI/CD & Deployment ##


## License ##
This project is open-source. Please see the [LICENSE](LICENSE) file for details.



## Contacts ##
- [aloisi.lorenzo99@gmail.com](mailto:aloisi.lorenzo99@gmail.com)
- [LinkedIn](https://www.linkedin.com/in/aloilor/)
- [GitHub](https://github.com/aloilor)



