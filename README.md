# LeagueRats

## 🚀 Overview

**LeagueRats** is a frontend application that allows users to follow League of Legends pro players, their accounts, and games. Built with modern web technologies and powered by the Riot Games API, this app provides real-time tracking and detailed statistics for competitive League of Legends players.

Check it out on [leaguerats.net](https://leaguerats.net)

---

## 🌟 Features

- **Track Pro Players**: Follow your favorite League of Legends professional players and their game statistics
- **Detailed Match History**: View comprehensive match history with in-depth analytics
- **Multiple Account Support**: Follow and monitor multiple player accounts simultaneously
- **Real-time Updates**: Get live updates on games and player performance
- **Firebase Integration**: Secure data storage and authentication
- **Privacy First**: Your data is handled securely with Firebase's robust infrastructure
- **User Friendly UI**: Clean and intuitive interface built with modern frontend technologies

---

## 🛠️ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) installed on your machine
- Riot Games API Key (get one from [Riot Developer Portal](https://developer.riotgames.com/))
- Firebase project setup

### Firebase Setup

1. Create a new Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication and Firestore Database
3. Generate your Firebase configuration and service account credentials

## Running app with docker

#### 1. Clone the repository:

```bash
git clone https://github.com/JakubTuta/LeagueRats.git

cd LeagueRats
```

#### 2. Set up environment variables

Create `.env` files in the main directory, `/backend`, and `/scheduler` with the following content:

```bash
# Firebase Project Config
API_KEY=your_firebase_api_key
AUTH_DOMAIN=your_project.firebaseapp.com
PROJECT_ID=your_firebase_project_id
STORAGE_BUCKET=your_project.appspot.com
MESSAGING_SENDER_ID=your_messaging_sender_id
APP_ID=your_firebase_app_id

# Firebase Service Account
TYPE=service_account
PROJECT_ID=your_firebase_project_id
PRIVATE_KEY_ID=your_private_key_id
PRIVATE_KEY=your_private_key
CLIENT_EMAIL=your_service_account_email
CLIENT_ID=your_client_id
AUTH_URI=https://accounts.google.com/o/oauth2/auth
TOKEN_URI=https://oauth2.googleapis.com/token
AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
CLIENT_X509_CERT_URL=your_client_cert_url
UNIVERSE_DOMAIN=googleapis.com

# Riot Games API - Only in /backend and /scheduler
RIOT_API_KEY=your_riot_api_key
```

#### 3. Starting app

```bash
docker-compose up -d
```

FastAPI server runs on `http://localhost:8000`  
Frontend web app runs on `http://localhost:3000`

## Running each module separately

### 1. Starting FastAPI server

```bash
cd backend
```

Create virtual environment

```bash
python -m venv venv
```

Run virtual environment

```bash
# on Windows
venv/Scripts/activate

# on MacOS / Linux
source venv/bin/activate
```

Install the modules:

```bash
pip install -r requirements.txt
```

Make sure your `.env` file is properly configured in the `/backend` directory.

Now you can run the server

```bash
# with FastAPI CLI
fastapi run main.py

# or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

FastAPI server is running on `http://localhost:8000`

### 2. Starting Frontend app

```bash
cd frontend
```

Install the dependencies:

```bash
# replace npm with any package manager
npm install
```

```bash
# replace npm with any package manager
npm run dev
```

Frontend app is running on `http://localhost:3000`

### 3. Starting Scheduler (if applicable)

```bash
cd scheduler
```

Create virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # or venv/Scripts/activate on Windows
pip install -r requirements.txt
```

Make sure your `.env` file is properly configured in the `/scheduler` directory.

Run the scheduler:

```bash
# with FastAPI CLI
fastapi run main.py

# or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---
