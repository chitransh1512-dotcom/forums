# StudyDeck Forum Module

A community-driven academic discussion forum built using **Django**, designed for students of BITS Pilani to collaborate, ask doubts, and share resources.

This project was developed as part of a backend evaluation task, with a focus on clean architecture, permission-based access control, and scalability.


##  Features

- Email & Google OAuth authentication using **django-allauth**
- Strict BITS Pilani email restriction
- Permission-based roles (Student / Moderator)
- Thread creation with categories, tags, courses & resources
- Replies with **soft delete**
- Like system for threads and posts
- Reporting & moderation workflow
- Rate limiting to prevent spam
- Pagination for thread listings
- **Fuzzy search** for threads
- **Tag-based thread filtering**
- Clean UI using Django templates + Bootstrap
- Fully deployed to a **production environment**


##  Tech Stack

**Backend:** Django 5.2.x
**Language:** Python 3.13
**Database:** SQLite (development), PostgreSQL (production)
**Authentication:** django-allauth
**Frontend:** Django Templates + Bootstrap
**Deployment:** Docker + AWS EC2


##  Setup Instructions

## Clone The repository
git clone <your-repository-url>
cd forums

## Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

## Install dependencies
pip install -r requirements.txt

## Apply migrations
python manage.py migrate

## Populate base data
python manage.py populate_courses

## Run the development server
python manage.py runserver

# User roles and permissions
Student:     Create threads, reply, like, report
Moderator:   Lock threads, delete any post, resolve reports
uperuser:    Full access

## Authentication Rules
Only BITS Pilani student emails are allowed
Format: fYYYYXXXX@pilani.bits-pilani.ac.in

Google OAuth is restricted before user creation

Email verification is enabled

## Rate Limiting
Rate limiting is applied manually in views for non-trusted users:
Thread creation:3/hour
Post creation: 10/min
Reporting: 5/hour

Trusted users (moderators and superusers) bypass rate limits.

## Search and Tags
Fuzzy search implemented using Python’s difflib.SequenceMatcher
Tag-based filtering allows users to browse threads by selected tags
Slug collisions are explicitly handled to prevent database integrity errors

## Design and Decisions
Function-based views for clarity and explicit control
Permission checks handled in views, not templates
Soft delete used instead of hard delete to preserve moderation history and allowing future recovery if needed.
Database-agnostic search implementation;search is implemented without db specific extensions,ensuring portability.
SQLite used for development, PostgreSQL for production deployment since it supports concurrency better

## Deployment
The application is containerized using Docker
PostgreSQL is used as the production database
Deployed on AWS EC2 with a public URL: http://forum.elcodigo.me
