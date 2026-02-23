"""
Configuration settings for the Water Quality Monitoring Backend
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "AquaGuard API"
    DEBUG: bool = True
    
    # MQTT Settings (HiveMQ Cloud)
    MQTT_BROKER: str = "broker.hivemq.com"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_TOPIC_PREFIX: str = "aquaguard"
    
    # Firebase Settings
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"
    FIREBASE_DATABASE_URL: str = ""
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # JWT Settings
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # SMS Alert Settings (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Fast2SMS (Alternative for India)
    FAST2SMS_API_KEY: str = ""
    
    # Water Quality Thresholds
    PH_MIN: float = 6.5
    PH_MAX: float = 8.5
    TDS_MAX: float = 500.0  # mg/L
    TURBIDITY_MAX: float = 5.0  # NTU
    FLOW_MIN: float = 0.5  # L/min
    WATER_LEVEL_MIN: float = 10.0  # percentage
    
    # ML Model Settings
    MODEL_PATH: str = "models/anomaly_detector.joblib"
    ANOMALY_THRESHOLD: float = -0.5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


# Water Quality Standards Reference
WATER_QUALITY_STANDARDS = {
    "ph": {
        "min": 6.5,
        "max": 8.5,
        "unit": "",
        "name": "pH Level",
        "description": "Measure of acidity/alkalinity"
    },
    "tds": {
        "min": 0,
        "max": 500,
        "unit": "mg/L",
        "name": "Total Dissolved Solids",
        "description": "Concentration of dissolved substances"
    },
    "turbidity": {
        "min": 0,
        "max": 5,
        "unit": "NTU",
        "name": "Turbidity",
        "description": "Cloudiness of water"
    },
    "flow_rate": {
        "min": 0.5,
        "max": 50,
        "unit": "L/min",
        "name": "Flow Rate",
        "description": "Water flow speed"
    },
    "water_level": {
        "min": 10,
        "max": 100,
        "unit": "%",
        "name": "Water Level",
        "description": "Tank fill percentage"
    }
}
