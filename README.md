# 🎯 CV Screener System

A high-performance AI-powered CV screening web application that processes PDF files in zip archives and generates comprehensive Excel reports with intelligent evaluations.

## 🎥 Demo Video

https://github.com/user-attachments/assets/290c8c9d-b4fa-4f2f-977b-1ef9690b2d5f


## ⚡ Features

- **🌐 Full Web Application**: React frontend + FastAPI backend
- **📤 Drag & Drop Upload**: Intuitive file upload interface
- **🤖 AI-Powered Analysis**: Advanced Gemini AI evaluation engine
- **📊 Real-time Progress**: Live status updates with animated feedback
- **📥 Instant Download**: One-click Excel report download
- **🔄 Background Processing**: Non-blocking CV screening
- **📱 Modern UI**: Responsive design with toast notifications
- **🛡️ Error Handling**: Graceful failure recovery with user feedback

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key
- Portkey (for logging and mentoring)

### Setup & Run
1. Clone the repository
2. Copy `.env.example` to `.env` and configure your API key
3. Run `./run-services.sh`
4. Access the web interface at http://localhost:7445

## 📖 Usage Guide

1. **Upload CVs**
   - Drag & drop a ZIP file containing PDF CVs
   - File validation happens in real-time

2. **Configure Job Role**
   - Enter job position
   - Add required and preferred skills
   - Start processing

3. **Monitor Progress**
   - Watch real-time status updates
   - View processing statistics

4. **Download Results**
   - Get Excel report with detailed analysis
   - Review AI-powered recommendations

## 🏗️ Project Structure

```
cv_screener/
├── backend/                 # FastAPI server
│   ├── main.py             # Server entry point
│   ├── cv_screener.py      # Core logic
│   ├── api_client.py       # AI integration
│   └── requirements.txt    # Dependencies
├── frontend/               # React application
│   ├── src/               # Source code
│   └── public/            # Static assets
└── docker-compose.yml     # Service config
```

## 📊 Report Structure

The generated Excel reports include:
- Candidate details
- Educational qualifications
- Experience summary
- Skills assessment
- AI-powered recommendations
- Confidence scores

## 🔧 Development

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

## 🐳 Docker Commands

```bash
# Build services
docker-compose build

# Run services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 
