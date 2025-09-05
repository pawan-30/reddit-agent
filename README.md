# Eon.Health Intelligence Agent

## Overview

The Eon.Health Intelligence Agent is a sophisticated Reddit intelligence platform designed to analyze health-related conversations across multiple communities. The system provides strategic insights for eon.health's Space-Time Health OS by monitoring discussions in longevity, AI, biohacking, and health optimization communities.

## Project Purpose

This application serves as a market intelligence tool that:
- Monitors 47 strategically selected subreddits aligned with health and longevity topics
- Analyzes posts using advanced theme detection across 12 focus areas
- Generates company-specific insights based on detailed business descriptions
- Provides strategic recommendations for community engagement
- Synthesizes trends and patterns from analyzed discussions

## System Architecture

The application consists of two main components:
- **Backend**: FastAPI server with MongoDB database for data storage and analysis
- **Frontend**: React-based web interface with modern UI components

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- MongoDB database (local or cloud instance)

## Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the backend directory with your MongoDB connection string:
```
MONGO_URL=mongodb://localhost:27017/reddit
```

4. Start the backend server:
```bash
python server.py
```

The backend server will start on `http://localhost:8001`

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend application will start on `http://localhost:3000`

## Application Workflow

### 1. Search Phase
- User enters search keywords related to health topics
- System searches across 47 target subreddits covering six health pillars:
  - Recovery (sleep, restoration)
  - Nutrition (diet, supplements)
  - Movement (fitness, exercise)
  - Connection (mental health, social)
  - Cognition (brain training, nootropics)
  - Aesthetics (skincare, wellness)

### 2. Analysis Phase
- Retrieved posts undergo sophisticated analysis using 12 focus area categories
- Company description influences relevance scoring and insight generation
- System detects themes such as AI personalization, longevity focus, data analytics
- Each post receives a relevance score and strategic takeaways

### 3. Synthesis Phase
- Analyzed posts are synthesized into trend reports
- System identifies key patterns across communities
- Generates community-specific targeting insights
- Provides strategic recommendations for engagement

### 4. Results Display
- Posts displayed with filtering and sorting capabilities
- Trend analysis presented in compact card format with detailed modal views
- Company-specific response strategies and targeting intelligence provided

## Key Features

- Advanced theme detection system with 12 focus areas
- Company-specific analysis based on detailed business descriptions
- Comprehensive subreddit coverage across health and technology communities
- Modern responsive interface with dark/light mode support
- Real-time analysis and trend synthesis capabilities

## Database Requirements

The system requires MongoDB for storing:
- Retrieved Reddit posts
- Analysis results and relevance scores
- Trend synthesis reports
- User search history

## API Endpoints

- `POST /api/search-reddit` - Search and retrieve Reddit posts
- `POST /api/analyze-posts` - Analyze posts for relevance and insights
- `POST /api/synthesize-trends` - Generate trend analysis reports
- `GET /api/posts` - Retrieve stored posts with analysis
- `GET /api/trends` - Retrieve trend synthesis reports

## Project Structure

```
├── backend/
│   ├── server.py          # Main FastAPI server
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React application
│   │   ├── App.css       # Custom styles
│   │   └── components/   # UI components
│   ├── package.json      # Node dependencies
│   └── public/           # Static assets
└── README.md             # This file
```

## Usage Instructions

1. Start both backend and frontend servers following the setup instructions
2. Navigate to `http://localhost:3000` in your web browser
3. Enter search keywords in the search interface
4. Optionally modify the company description for customized analysis
5. Click "Search Reddit" to retrieve relevant posts
6. Click "Analyze Posts" to generate insights and relevance scores
7. Click "Synthesize Trends" to create comprehensive trend reports
8. Use filtering and sorting options to refine results
9. Click on trend cards to view detailed analysis in modal windows

## Configuration Notes

- The system uses a pre-configured MongoDB connection string
- Reddit scraping is performed without API keys using web scraping techniques
- All analysis is performed locally without external API dependencies
- The application includes comprehensive error handling and logging