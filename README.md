## Manga Alert Italia - Manga Releases Tracker and Notification System ##

<p align="center"> <a href="https://mangaalertitalia.it/">
   <img src="./assets/logo-with-white-bg-crop.png" align="center" width="225" />
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

3. **Notification Emails**:  
   - Sends reminder emails through **SendGrid** (with AWS Secrets Manager storing the API key).
   - Three notifications per volume:  
     - 1 month before release  
     - 1 week before release  
     - 1 day before release  
   - Includes an unsubscribe link tokenizing user identities for secure one-click unsubscription.

4. **Unsubscribe Flow**:  
   - Users can unsubscribe via a unique token representing user identities embedded in each email.  
   - A dedicated endpoint on the backend (`/unsubscribe/<token>`) handles user removal and subscription data cleanup.

5. **SSL Certificate Management**:
   - Integrates **Let’s Encrypt** with **AWS Lambda** for automated certificate renewal.
   - Stores certificates in **AWS Secrets Manager**.


## Architecture ##

1. **Scraper** (Python):
   - Periodically runs to fetch new manga volume info and populates a `manga_releases` table in PostgreSQL.
   - Marks upcoming releases to identify when to send notifications.

2. **Backend (Flask API)**:
   - **Endpoints**:
     - `/subscribe`: Subscribes a user to the newsletter; enforces limit of 15 subscribers.
     - `/unsubscribe/<token>`: Unsubscribes a user via their unique token.
   - **Database**: Communicates with PostgreSQL to store subscribers, subscriptions, and release alerts.
   - **Email Handling**: Uses SendGrid for sending out notifications based on the `manga_releases` schedule.

3. **Front-End (React)**:
   - Deployed on AWS S3 as a static site with a client-side router (`BrowserRouter`).
   - Subscription form for entering email and selecting manga series.
   - Unsubscribe page handling the `unsubscribe_token`.
   - Informazioni page (FAQ-like accordion) explaining the site, privacy policy, and contact info.

4. **CI/CD & Deployment**:
   - **GitHub Actions**: Automated testing with pytest, building Docker images, pushing to AWS ECR.
   - **Terraform**: Defines AWS resources (ECS tasks, ECR repos, S3 buckets, Secrets Manager, etc.).
   - **ECS**: Orchestrates Docker containers for the Flask API and any worker processes.
   - **Let’s Encrypt**: SSL certificates automatically managed via Lambda, stored in Secrets Manager.



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


## Contacts ##
- [aloisi.lorenzo99@gmail.com](mailto:aloisi.lorenzo99@gmail.com)
- [LinkedIn](https://www.linkedin.com/in/aloilor/)
- [GitHub](https://github.com/aloilor)



