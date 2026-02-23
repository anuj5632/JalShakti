# AquaGuard - IoT Water Quality Monitoring System

<div align="center">

![AquaGuard Logo](https://img.shields.io/badge/AquaGuard-IoT%20Water%20Quality-blue?style=for-the-badge&logo=water)

[![ESP32](https://img.shields.io/badge/ESP32-MicroPython-green?style=flat-square&logo=espressif)](https://micropython.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![Firebase](https://img.shields.io/badge/Firebase-Realtime%20DB-FFCA28?style=flat-square&logo=firebase)](https://firebase.google.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**A low-cost IoT solution for real-time household water quality monitoring with ML-powered anomaly detection**

[Live Demo](#) • [Documentation](#architecture) • [Quick Start](#-quick-start)

</div>

---

## 📋 Problem Statement

Access to clean drinking water remains a critical challenge. Traditional water quality testing is:

- **Expensive** - Lab tests cost ₹500-2000 per sample
- **Time-consuming** - Results take 2-7 days
- **Reactive** - Issues detected only after consumption
- **Inaccessible** - No real-time monitoring for households

**AquaGuard** solves this by providing continuous, automated water quality monitoring at a fraction of the cost.

---

## ✨ Features

### 🔬 Sensor Monitoring

- **pH Level** - Acidity/alkalinity detection (6.5-8.5 optimal)
- **TDS** - Total Dissolved Solids measurement
- **Turbidity** - Water clarity analysis
- **Flow Rate** - Water consumption tracking
- **Water Level** - Tank level monitoring
- **Temperature** - Thermal monitoring

### 🤖 ML-Powered Analysis

- **Anomaly Detection** - Isolation Forest algorithm
- **Quality Scoring** - Real-time 0-100 quality index
- **Trend Analysis** - Historical pattern recognition
- **Predictive Alerts** - Early warning system

### 📱 Smart Dashboard

- **Real-time Updates** - Live sensor data visualization
- **Multi-Tank Support** - Monitor multiple water sources
- **Interactive Charts** - Recharts-powered analytics
- **Dark/Light Mode** - User preference support
- **Mobile Responsive** - Works on all devices

### 🔔 Alert System

- **SMS Notifications** - Twilio & Fast2SMS integration
- **Configurable Thresholds** - Customizable alert levels
- **Alert History** - Track and manage notifications
- **Email Alerts** - (Coming soon)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AquaGuard System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐     MQTT      ┌──────────────┐                  │
│  │   ESP32     │──────────────▶│   HiveMQ     │                  │
│  │  Sensors    │               │   Broker     │                  │
│  └─────────────┘               └──────┬───────┘                  │
│                                       │                           │
│                                       ▼                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   FastAPI Backend                            │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐           │ │
│  │  │  Google  │  │   ML     │  │  Alert Service   │           │ │
│  │  │   Auth   │  │  Engine  │  │ (Twilio/Fast2SMS)│           │ │
│  │  └──────────┘  └──────────┘  └──────────────────┘           │ │
│  └───────────────────────┬─────────────────────────────────────┘ │
│                          │                                        │
│            ┌─────────────┴─────────────┐                         │
│            ▼                           ▼                          │
│  ┌──────────────────┐       ┌──────────────────┐                 │
│  │    Firestore     │       │  Realtime DB     │                 │
│  │  (User Profiles) │       │ (Sensor Data)    │                 │
│  └──────────────────┘       └──────────────────┘                 │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  React Dashboard                             │ │
│  │  • Google OAuth    • Real-time Charts                        │ │
│  │  • Multi-tank View • Alert Management                        │ │
│  │  • Analytics       • Settings                                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Firebase Project
- Google OAuth Client ID

### 1. Clone Repository

```bash
git clone https://github.com/ansh-bajaj1/NSS-Hackathon.git
cd NSS-Hackathon
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# Run server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Start development server
npm start
```

### 4. ML Model Training (Optional)

```bash
cd model
pip install -r requirements.txt
python generate_data.py
python train_model.py
```

### 5. Wokwi Simulation

1. Install [Wokwi VS Code Extension](https://marketplace.visualstudio.com/items?itemName=Wokwi.wokwi-vscode)
2. Open `simulation/diagram.json`
3. Click "Start Simulation"

---

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 📁 Project Structure

```
NSS-Hackathon/
├── firmware/              # ESP32 MicroPython code
│   ├── boot.py           # WiFi initialization
│   ├── config.py         # Configuration settings
│   └── main.py           # Main sensor loop
│
├── backend/              # FastAPI server
│   ├── main.py           # API endpoints
│   ├── config.py         # Settings management
│   ├── models.py         # Pydantic models
│   ├── firebase_service.py
│   ├── auth_service.py   # Google OAuth + JWT
│   ├── ml_engine.py      # Anomaly detection
│   ├── alert_service.py  # SMS notifications
│   └── mqtt_subscriber.py
│
├── frontend/             # React dashboard
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── context/      # React context (Auth, Theme)
│   │   └── App.js        # Router configuration
│   └── public/
│
├── model/                # ML training
│   ├── generate_data.py  # Synthetic data generator
│   └── train_model.py    # Isolation Forest training
│
├── simulation/           # Wokwi simulation
│   ├── diagram.json      # Circuit diagram
│   └── wokwi.toml        # Simulation config
│
└── docker-compose.yml    # Container orchestration
```

---

## 🔧 Configuration

### Environment Variables

| Variable                | Description            | Required |
| ----------------------- | ---------------------- | -------- |
| `GOOGLE_CLIENT_ID`      | Google OAuth client ID | ✅       |
| `JWT_SECRET_KEY`        | Secret for JWT tokens  | ✅       |
| `FIREBASE_PROJECT_ID`   | Firebase project ID    | ✅       |
| `FIREBASE_PRIVATE_KEY`  | Service account key    | ✅       |
| `FIREBASE_CLIENT_EMAIL` | Service account email  | ✅       |
| `MQTT_BROKER`           | MQTT broker address    | ❌       |
| `TWILIO_ACCOUNT_SID`    | Twilio account SID     | ❌       |
| `FAST2SMS_API_KEY`      | Fast2SMS API key       | ❌       |

### Water Quality Standards

| Parameter        | Optimal Range | Warning          | Critical   |
| ---------------- | ------------- | ---------------- | ---------- |
| pH               | 6.5 - 8.5     | 6.0-6.5, 8.5-9.0 | <6.0, >9.0 |
| TDS (ppm)        | < 300         | 300-500          | > 500      |
| Turbidity (NTU)  | < 1           | 1-5              | > 5        |
| Temperature (°C) | 20-30         | 15-20, 30-35     | <15, >35   |

---

## 🧪 Hardware Components

| Component          | Purpose             | GPIO Pin     |
| ------------------ | ------------------- | ------------ |
| pH Sensor          | Acidity measurement | GPIO 34      |
| TDS Sensor         | Dissolved solids    | GPIO 35      |
| Turbidity Sensor   | Water clarity       | GPIO 32      |
| Flow Sensor        | Water flow rate     | GPIO 33      |
| Ultrasonic Sensor  | Water level         | GPIO 25, 26  |
| Temperature Sensor | Water temperature   | ADC          |
| Green LED          | Power indicator     | GPIO 2       |
| Blue LED           | WiFi status         | GPIO 4       |
| Red LED            | Alert indicator     | GPIO 15      |
| LCD Display        | Local readings      | I2C (21, 22) |

---

## 📊 API Endpoints

### Authentication

- `POST /auth/google` - Google OAuth login
- `GET /user/profile` - Get user profile
- `PUT /user/profile` - Update profile

### Water Sources

- `GET /sources` - List all sources
- `POST /sources` - Add new source
- `PUT /sources/{id}` - Update source
- `DELETE /sources/{id}` - Remove source

### Dashboard

- `GET /dashboard/summary` - Overview metrics
- `GET /dashboard/latest/{source_id}` - Latest readings
- `GET /dashboard/history/{source_id}` - Historical data

### Alerts

- `GET /alerts` - List alerts
- `PUT /alerts/{id}/acknowledge` - Acknowledge alert
- `PUT /alerts/{id}/resolve` - Resolve alert

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**NSS Hackathon Team**

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI library
- [Firebase](https://firebase.google.com/) - Backend services
- [Wokwi](https://wokwi.com/) - IoT simulation platform
- [HiveMQ](https://www.hivemq.com/) - MQTT broker

---

<div align="center">

**Made with ❤️ for cleaner water**

</div>
