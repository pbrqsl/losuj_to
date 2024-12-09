# losuj_to

## Overview
**losuj_to** is a Secret Santa application designed to streamline the process of organizing gift exchanges. Users can create events, invite participants, and have the app randomly assign gift-givers to recipients.

---

## Features
- User-friendly interface for creating Secret Santa events.
- Secure participant management.
- Randomized assignment of gift exchanges.
- Notifications for participants.
- Optimized for performance and reliability.

---

## Tech Stack

### Backend
- **Python**: Core programming language.
- **Django**: Framework used for building the application backend.
- **Django REST Framework (DRF)**: For creating robust and scalable APIs.
- **PostgreSQL**: Database for managing user and event data.

### Frontend
- **HTML5** and **CSS3**: For building the basic user interface.
- **JavaScript**: For enhancing interactivity.

### Infrastructure
- **Docker**: Containerization for consistent development and deployment environments.
- **Docker Compose**: Simplifies multi-container Docker applications.
- **AWS**: Hosting and managing the application in the cloud.
  - EC2 for hosting.
  - RDS for the PostgreSQL database.

### Additional Tools
- **Celery**: For handling background tasks like sending notifications.
- **RabbitMQ**: Message broker for Celery tasks.
- **GitHub Actions**: For Continuous Integration and Continuous Deployment (CI/CD).

### Domain and SSL
- **Cloudflare**: Domain registration and SSL/TLS certificate management.
- **AWS Certificate Manager (ACM)**: SSL/TLS for secure communications.
