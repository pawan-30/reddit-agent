# Eon.Health Intelligence Agent

A sophisticated Reddit intelligence platform for eon.health's Space-Time Health OS. Analyzes multi-dimensional health conversations across longevity, AI, and biohacking communities with advanced theme detection and strategic positioning insights.

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python server.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🎯 Features

- **Advanced Theme Detection**: 12-category analysis system aligned with eon.health's Six Pillars Framework
- **Company-Specific Analysis**: Tailored insights based on comprehensive company descriptions
- **47 Target Communities**: Strategic subreddit coverage across health, AI, longevity, and biohacking
- **Modern UI/UX**: Dark/light mode, responsive design, smooth animations
- **Compact Trends View**: Modal-based trend analysis to reduce scrolling
- **Real-time Intelligence**: Live Reddit monitoring and analysis

## 📁 Project Structure

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

## 🔧 Configuration

The system uses MongoDB for data storage and requires environment variables for database connection. Update `backend/.env` with your MongoDB connection string.

## 🎨 UI Features

- **Search & Track**: Advanced Reddit search with company-specific analysis
- **Posts View**: Grid/list toggle with filtering and sorting
- **Trends Analysis**: Compact cards with detailed modal views
- **Dark Mode**: Professional dark theme by default
- **Responsive Design**: Optimized for all screen sizes

