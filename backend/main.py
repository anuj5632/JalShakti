"""
AquaGuard - Water Quality Monitoring System API
Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uvicorn

from config import settings, WATER_QUALITY_STANDARDS
from models import (
    GoogleAuthRequest, TokenResponse, UserProfile, UserProfileUpdate,
    HomeSetupRequest, WaterSourceCreate, WaterSource, WaterSourceUpdate,
    SensorReading, SensorDataWithMeta, SensorDataHistory,
    Alert, AlertCreate, AlertUpdate, AlertStatus,
    DashboardSummary, SourceStats, AnomalyDetectionResult, QualityPrediction
)
from auth_service import auth_service, get_current_user
from firebase_service import firebase_service
from ml_engine import ml_engine
from alert_service import alert_service
from mqtt_subscriber import mqtt_subscriber, handle_sensor_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting AquaGuard API...")
    
    # Connect MQTT subscriber
    mqtt_subscriber.set_message_callback(handle_sensor_data)
    mqtt_subscriber.connect()
    
    print("✓ AquaGuard API started successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AquaGuard API...")
    mqtt_subscriber.disconnect()
    print("✓ AquaGuard API shut down")


app = FastAPI(
    title=settings.APP_NAME,
    description="IoT Water Quality Monitoring System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health Check ====================

@app.get("/", tags=["Health"])
async def root():
    """API root - health check"""
    return {
        "name": settings.APP_NAME,
        "status": "healthy",
        "version": "1.0.0",
        "mqtt_connected": mqtt_subscriber.connected
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": True,
            "mqtt": mqtt_subscriber.connected,
            "firebase": firebase_service.firestore_db is not None,
            "ml_engine": ml_engine.model is not None
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== Authentication ====================

@app.post("/auth/google", response_model=Dict, tags=["Authentication"])
async def google_auth(request: GoogleAuthRequest):
    """Authenticate with Google OAuth - supports both ID token and access token flow"""
    if request.user_info:
        # Access token flow - user info already fetched by frontend
        result = await auth_service.authenticate_with_user_info(request.user_info.model_dump())
    elif request.token:
        # ID token flow - verify with Google
        result = await auth_service.authenticate_user(request.token)
    else:
        raise HTTPException(status_code=400, detail="Either token or user_info is required")
    return result


@app.get("/auth/me", response_model=Dict, tags=["Authentication"])
async def get_current_user_profile(user: dict = Depends(get_current_user)):
    """Get current authenticated user profile"""
    return user


# ==================== User & Home Setup ====================

@app.put("/user/profile", response_model=Dict, tags=["User"])
async def update_profile(
    update: UserProfileUpdate,
    user: dict = Depends(get_current_user)
):
    """Update user profile"""
    result = await firebase_service.update_user(user['uid'], update.model_dump(exclude_none=True))
    return {"status": "success", "data": result}


@app.post("/user/home-setup", response_model=Dict, tags=["User"])
async def setup_home(
    setup: HomeSetupRequest,
    user: dict = Depends(get_current_user)
):
    """Setup home details (required before adding water sources)"""
    result = await firebase_service.setup_home(user['uid'], setup.model_dump())
    return {"status": "success", "message": "Home setup complete", "data": result}


@app.get("/user/home-setup/status", response_model=Dict, tags=["User"])
async def get_home_setup_status(user: dict = Depends(get_current_user)):
    """Check if home setup is complete"""
    return {
        "home_setup_complete": user.get('home_setup_complete', False),
        "phone": user.get('phone'),
        "address": user.get('address'),
        "city": user.get('city')
    }


# ==================== Water Sources ====================

@app.post("/sources", response_model=Dict, tags=["Water Sources"])
async def create_water_source(
    source: WaterSourceCreate,
    user: dict = Depends(get_current_user)
):
    """Create a new water source (tank, tap, etc.)"""
    source_data = source.model_dump()
    source_data['user_id'] = user['uid']
    
    result = await firebase_service.create_source(source_data)
    return {"status": "success", "data": result}


@app.get("/sources", response_model=Dict, tags=["Water Sources"])
async def get_water_sources(user: dict = Depends(get_current_user)):
    """Get all water sources for the current user"""
    sources = await firebase_service.get_sources(user['uid'])
    return {"sources": sources, "count": len(sources)}


@app.get("/sources/{source_id}", response_model=Dict, tags=["Water Sources"])
async def get_water_source(
    source_id: str,
    user: dict = Depends(get_current_user)
):
    """Get a specific water source"""
    source = await firebase_service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source.get('user_id') != user['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get latest reading
    latest = await firebase_service.get_latest_reading(source_id)
    
    return {
        "source": source,
        "latest_reading": latest
    }


@app.put("/sources/{source_id}", response_model=Dict, tags=["Water Sources"])
async def update_water_source(
    source_id: str,
    update: WaterSourceUpdate,
    user: dict = Depends(get_current_user)
):
    """Update a water source"""
    source = await firebase_service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source.get('user_id') != user['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await firebase_service.update_source(source_id, update.model_dump(exclude_none=True))
    return {"status": "success", "data": result}


@app.delete("/sources/{source_id}", response_model=Dict, tags=["Water Sources"])
async def delete_water_source(
    source_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a water source"""
    source = await firebase_service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source.get('user_id') != user['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await firebase_service.delete_source(source_id)
    return {"status": "success", "message": "Source deleted"}


# ==================== Sensor Data ====================

@app.get("/sources/{source_id}/readings", response_model=Dict, tags=["Sensor Data"])
async def get_sensor_readings(
    source_id: str,
    limit: int = Query(100, ge=1, le=1000),
    user: dict = Depends(get_current_user)
):
    """Get sensor readings for a water source"""
    source = await firebase_service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source.get('user_id') != user['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    readings = await firebase_service.get_readings(source_id, limit)
    return {"readings": readings, "count": len(readings)}


@app.post("/sources/{source_id}/readings", response_model=Dict, tags=["Sensor Data"])
async def add_sensor_reading(
    source_id: str,
    reading: SensorReading,
    user: dict = Depends(get_current_user)
):
    """Manually add a sensor reading (for testing)"""
    source = await firebase_service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source.get('user_id') != user['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Analyze reading
    reading_data = reading.model_dump()
    analysis = ml_engine.analyze_reading(reading_data)
    
    # Prepare full reading
    full_reading = {
        **reading_data,
        'source_id': source_id,
        'user_id': user['uid'],
        'is_anomaly': analysis['is_anomaly'],
        'anomaly_score': analysis['anomaly_score'],
        'quality_score': analysis['quality_score']
    }
    
    # Store reading
    result = await firebase_service.store_sensor_reading(full_reading)
    
    # Process alerts if anomaly
    if analysis['is_anomaly'] and user.get('phone'):
        await alert_service.process_reading_alerts(
            reading_data, analysis, user['phone'], source.get('name', 'Unknown')
        )
    
    return {
        "status": "success",
        "reading": full_reading,
        "analysis": analysis
    }


# ==================== Alerts ====================

@app.get("/alerts", response_model=Dict, tags=["Alerts"])
async def get_alerts(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    user: dict = Depends(get_current_user)
):
    """Get alerts for the current user"""
    alerts = await firebase_service.get_alerts(user['uid'], status, limit)
    return {"alerts": alerts, "count": len(alerts)}


@app.put("/alerts/{alert_id}", response_model=Dict, tags=["Alerts"])
async def update_alert(
    alert_id: str,
    update: AlertUpdate,
    user: dict = Depends(get_current_user)
):
    """Update alert status (acknowledge or resolve)"""
    result = await firebase_service.update_alert(alert_id, update.model_dump())
    return {"status": "success", "data": result}


# ==================== Dashboard & Analytics ====================

@app.get("/dashboard", response_model=Dict, tags=["Dashboard"])
async def get_dashboard(user: dict = Depends(get_current_user)):
    """Get dashboard summary for the current user"""
    # Get all sources
    sources = await firebase_service.get_sources(user['uid'])
    
    # Get active alerts
    alerts = await firebase_service.get_alerts(user['uid'], 'active', 10)
    
    # Compile source stats
    source_stats = []
    total_quality = 0
    active_count = 0
    
    for source in sources:
        latest = await firebase_service.get_latest_reading(source['id'])
        
        if latest:
            quality = latest.get('quality_score', 0)
            status = "online"
            active_count += 1
        else:
            quality = 0
            status = "offline"
        
        total_quality += quality
        
        source_stats.append({
            "source_id": source['id'],
            "source_name": source.get('name', 'Unknown'),
            "source_type": source.get('source_type', 'unknown'),
            "current_reading": latest,
            "quality_score": quality,
            "status": status,
            "last_updated": latest.get('timestamp') if latest else None
        })
    
    overall_quality = total_quality / len(sources) if sources else 0
    
    return {
        "total_sources": len(sources),
        "active_sources": active_count,
        "overall_quality_score": round(overall_quality, 1),
        "active_alerts": len(alerts),
        "sources": source_stats,
        "recent_alerts": alerts,
        "user": {
            "name": user.get('name'),
            "home_setup_complete": user.get('home_setup_complete', False)
        }
    }


@app.get("/analytics/{source_id}", response_model=Dict, tags=["Dashboard"])
async def get_source_analytics(
    source_id: str,
    days: int = Query(7, ge=1, le=30),
    user: dict = Depends(get_current_user)
):
    """Get analytics for a specific water source"""
    source = await firebase_service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source.get('user_id') != user['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    readings = await firebase_service.get_readings(source_id, days * 24)  # Hourly readings
    
    if not readings:
        return {"source": source, "analytics": None, "message": "No data available"}
    
    # Calculate daily averages
    # (In production, this would be done with proper time aggregation)
    import statistics
    
    ph_values = [r.get('ph', 7) for r in readings if r.get('ph')]
    tds_values = [r.get('tds', 200) for r in readings if r.get('tds')]
    turb_values = [r.get('turbidity', 2) for r in readings if r.get('turbidity')]
    quality_values = [r.get('quality_score', 50) for r in readings if r.get('quality_score')]
    
    return {
        "source": source,
        "analytics": {
            "period_days": days,
            "total_readings": len(readings),
            "averages": {
                "ph": round(statistics.mean(ph_values), 2) if ph_values else None,
                "tds": round(statistics.mean(tds_values), 2) if tds_values else None,
                "turbidity": round(statistics.mean(turb_values), 2) if turb_values else None,
                "quality_score": round(statistics.mean(quality_values), 1) if quality_values else None
            },
            "anomaly_count": sum(1 for r in readings if r.get('is_anomaly')),
            "readings": readings[-100:]  # Last 100 readings for charts
        }
    }


# ==================== ML Endpoints ====================

@app.post("/analyze", response_model=Dict, tags=["ML Analysis"])
async def analyze_reading(
    reading: SensorReading,
    user: dict = Depends(get_current_user)
):
    """Analyze a sensor reading for anomalies and quality"""
    analysis = ml_engine.analyze_reading(reading.model_dump())
    return analysis


@app.get("/standards", response_model=Dict, tags=["Reference"])
async def get_water_standards():
    """Get water quality standards reference"""
    return WATER_QUALITY_STANDARDS


# ==================== Run Server ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
