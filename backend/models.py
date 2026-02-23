"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class SourceType(str, Enum):
    OVERHEAD_TANK = "overhead_tank"
    STORAGE_TANK = "storage_tank"
    KITCHEN_TAP = "kitchen_tap"
    BATHROOM_TAP = "bathroom_tap"
    GARDEN_TAP = "garden_tap"
    BOREWELL = "borewell"
    MUNICIPAL = "municipal"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


# ==================== Auth Models ====================

class GoogleUserInfo(BaseModel):
    sub: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: Optional[bool] = True


class GoogleAuthRequest(BaseModel):
    token: Optional[str] = Field(None, description="Google OAuth ID token")
    access_token: Optional[str] = Field(None, description="Google OAuth access token")
    user_info: Optional[GoogleUserInfo] = Field(None, description="User info from Google")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserProfile"


# ==================== User Models ====================

class UserProfile(BaseModel):
    uid: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None


class HomeSetupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{9,14}$")
    address: str = Field(..., min_length=5, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., pattern=r"^\d{5,6}$")


# ==================== Water Source Models ====================

class WaterSourceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    source_type: SourceType
    location: Optional[str] = None
    capacity_liters: Optional[float] = None
    description: Optional[str] = None
    is_active: bool = True


class WaterSource(WaterSourceCreate):
    id: str
    user_id: str
    mqtt_topic: str
    created_at: datetime
    updated_at: datetime


class WaterSourceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity_liters: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# ==================== Sensor Data Models ====================

class SensorReading(BaseModel):
    ph: float = Field(..., ge=0, le=14)
    tds: float = Field(..., ge=0)
    turbidity: float = Field(..., ge=0)
    flow_rate: float = Field(..., ge=0)
    water_level: float = Field(..., ge=0, le=100)
    temperature: Optional[float] = None
    timestamp: Optional[datetime] = None


class SensorDataWithMeta(SensorReading):
    source_id: str
    user_id: str
    is_anomaly: bool = False
    anomaly_score: Optional[float] = None
    quality_score: float = Field(..., ge=0, le=100)


class SensorDataHistory(BaseModel):
    source_id: str
    readings: List[SensorDataWithMeta]
    start_time: datetime
    end_time: datetime
    total_count: int


# ==================== Alert Models ====================

class AlertCreate(BaseModel):
    source_id: str
    title: str
    message: str
    severity: AlertSeverity
    metric: str
    value: float
    threshold: float


class Alert(AlertCreate):
    id: str
    user_id: str
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AlertUpdate(BaseModel):
    status: AlertStatus


# ==================== Analytics Models ====================

class DailyStats(BaseModel):
    date: str
    avg_ph: float
    avg_tds: float
    avg_turbidity: float
    total_flow: float
    anomaly_count: int
    quality_score: float


class SourceStats(BaseModel):
    source_id: str
    source_name: str
    current_reading: Optional[SensorReading] = None
    quality_score: float
    status: str
    last_updated: Optional[datetime] = None


class DashboardSummary(BaseModel):
    total_sources: int
    active_sources: int
    overall_quality_score: float
    active_alerts: int
    sources: List[SourceStats]
    recent_alerts: List[Alert]


# ==================== ML Models ====================

class AnomalyDetectionResult(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    confidence: float
    anomalous_metrics: List[str]


class QualityPrediction(BaseModel):
    quality_score: float
    category: str  # Excellent, Good, Fair, Poor, Critical
    recommendations: List[str]


# Forward reference update
TokenResponse.model_rebuild()
