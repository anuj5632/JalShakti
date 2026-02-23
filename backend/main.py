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


# ==================== Device Data Ingestion ====================

@app.post("/api/v1/sensor-data", response_model=Dict, tags=["Device Data"])
async def receive_sensor_data(
    reading: dict
):
    """
    Receive sensor data from ESP32/IoT devices
    No authentication required - uses device_id for identification
    """
    try:
        device_id = reading.get('device_id', 'unknown')
        
        # Analyze the reading
        analysis = ml_engine.analyze_reading(reading)
        
        # Store in memory buffer for real-time dashboard
        # In production, would store in Firebase/Redis
        if not hasattr(receive_sensor_data, 'data_buffer'):
            receive_sensor_data.data_buffer = {}
        
        receive_sensor_data.data_buffer[device_id] = {
            **reading,
            'analysis': analysis,
            'received_at': datetime.utcnow().isoformat()
        }
        
        # Keep last 100 readings per device
        if not hasattr(receive_sensor_data, 'history'):
            receive_sensor_data.history = {}
        
        if device_id not in receive_sensor_data.history:
            receive_sensor_data.history[device_id] = []
        
        receive_sensor_data.history[device_id].append({
            **reading,
            'analysis': analysis,
            'received_at': datetime.utcnow().isoformat()
        })
        
        # Keep only last 100
        receive_sensor_data.history[device_id] = receive_sensor_data.history[device_id][-100:]
        
        # Check for alerts and send SMS if critical
        if analysis.get('is_anomaly') and reading.get('severity') == 'critical':
            # Import SMS service
            try:
                from sms_service import sms_service
                # In production, get phone from user profile
                # For demo, log the alert
                print(f"🚨 CRITICAL ALERT from {device_id}: {reading.get('alerts', [])}")
            except ImportError:
                pass
        
        return {
            "status": "success",
            "device_id": device_id,
            "analysis": analysis,
            "message": "Data received successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/api/v1/live-data", response_model=Dict, tags=["Device Data"])
async def get_live_data(device_id: Optional[str] = None):
    """Get live data from IoT devices"""
    if not hasattr(receive_sensor_data, 'data_buffer'):
        return {"devices": {}, "message": "No data yet"}
    
    if device_id:
        data = receive_sensor_data.data_buffer.get(device_id)
        return {"device": data} if data else {"error": "Device not found"}
    
    return {"devices": receive_sensor_data.data_buffer}


@app.get("/api/v1/device-history/{device_id}", response_model=Dict, tags=["Device Data"])
async def get_device_history(device_id: str, limit: int = 50):
    """Get historical data for a device"""
    if not hasattr(receive_sensor_data, 'history'):
        return {"readings": [], "count": 0}
    
    history = receive_sensor_data.history.get(device_id, [])
    return {
        "device_id": device_id,
        "readings": history[-limit:],
        "count": len(history[-limit:])
    }


# ==================== ML Predictions ====================

@app.post("/api/v1/predict", response_model=Dict, tags=["ML Predictions"])
async def predict_future_values(
    device_id: str,
    steps: int = Query(5, ge=1, le=20)
):
    """
    Predict future water quality values using ML model
    Uses scikit-learn based predictor
    """
    try:
        # Import predictor
        import sys
        import os
        model_path = os.path.join(os.path.dirname(__file__), '..', 'model')
        sys.path.insert(0, model_path)
        
        from predictor import WaterQualityPredictor
        
        # Check if model exists
        model_file = os.path.join(model_path, 'water_quality_model.joblib')
        
        predictor = WaterQualityPredictor()
        
        if os.path.exists(model_file):
            predictor.load_model(model_file)
        else:
            # Train on synthetic data if no saved model
            predictor.train(verbose=False)
        
        # Get historical data for this device
        if not hasattr(receive_sensor_data, 'history') or device_id not in receive_sensor_data.history:
            # Generate predictions from synthetic baseline
            predictions = predictor.predict_all(
                ph_history=[7.0, 7.1, 7.2, 7.1, 7.0, 6.9, 7.0, 7.1, 7.2, 7.1],
                turbidity_history=[5, 5.2, 5.1, 5.3, 5.0, 4.9, 5.1, 5.2, 5.0, 5.1],
                tds_history=[250, 252, 251, 253, 250, 248, 251, 252, 250, 251],
                steps=steps
            )
        else:
            history = receive_sensor_data.history[device_id]
            
            # Need at least window_size readings
            if len(history) < predictor.window_size:
                return {
                    "error": f"Need at least {predictor.window_size} readings for prediction",
                    "current_count": len(history)
                }
            
            predictions = predictor.predict_all(
                ph_history=[r.get('ph', 7.0) for r in history],
                turbidity_history=[r.get('turbidity', 5) for r in history],
                tds_history=[r.get('tds', 250) for r in history],
                steps=steps
            )
        
        return {
            "device_id": device_id,
            "predictions": predictions,
            "model_type": "GradientBoosting + RandomForest",
            "prediction_intervals": [f"+{(i+1)*5} min" for i in range(steps)]
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Prediction failed"
        }


# ==================== SMS Alerts ====================

@app.post("/api/v1/test-sms", response_model=Dict, tags=["SMS"])
async def test_sms(
    phone: str,
    message: str = "Test alert from AquaGuard"
):
    """Test SMS sending (for development)"""
    try:
        from sms_service import sms_service
        
        result = await sms_service.send_sms(phone, message)
        return result
        
    except ImportError:
        return {"error": "SMS service not available"}


@app.get("/api/v1/sms-status", response_model=Dict, tags=["SMS"])
async def get_sms_status():
    """Get SMS service status"""
    try:
        from sms_service import sms_service
        return sms_service.get_status()
    except ImportError:
        return {"configured": False, "error": "SMS service not imported"}


@app.post("/api/v1/send-alert-sms", response_model=Dict, tags=["SMS"])
async def send_alert_sms(
    phone_numbers: List[str],
    alert_type: str = "warning",
    source_name: str = "Main Tank",
    ph: float = 7.0,
    turbidity: float = 5.0,
    tds: float = 250,
    anomalies: List[str] = []
):
    """Send water quality alert SMS to specified numbers"""
    try:
        from sms_service import sms_service
        
        values = {"ph": ph, "turbidity": turbidity, "tds": tds}
        results = await sms_service.send_alert(
            phone_numbers, alert_type, source_name, values, anomalies
        )
        
        return {
            "status": "sent",
            "results": results
        }
        
    except ImportError:
        return {"error": "SMS service not available"}


# ==================== Email Alerts ====================

@app.post("/api/v1/test-email", response_model=Dict, tags=["Email"])
async def test_email(
    recipient: str
):
    """Test email sending - sends a test alert email"""
    try:
        from email_service import email_service
        
        result = email_service.send_test_email(recipient)
        
        return {
            "success": result,
            "message": "Test email sent successfully" if result else "Failed to send test email",
            "recipient": recipient
        }
        
    except ImportError as e:
        return {"error": f"Email service not available: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v1/email-status", response_model=Dict, tags=["Email"])
async def get_email_status():
    """Get email service configuration status"""
    try:
        from email_service import email_service
        
        return {
            "configured": True,
            "smtp_server": email_service.smtp_server,
            "sender_email": email_service.sender_email,
            "app_password_set": bool(email_service.app_password)
        }
    except ImportError:
        return {"configured": False, "error": "Email service not imported"}


@app.post("/api/v1/send-alert-email", response_model=Dict, tags=["Email"])
async def send_alert_email(
    recipients: str = Query(..., description="Comma-separated email addresses"),
    alert_type: str = Query("warning"),
    location: str = Query("Main Water Tank"),
    ph: float = Query(7.0),
    tds: float = Query(250.0),
    turbidity: float = Query(2.5),
    temperature: float = Query(26.0),
    water_level: float = Query(75.0),
    flow_rate: float = Query(5.0),
    quality_score: float = Query(75.0)
):
    """
    Send water quality alert email with full sensor details
    
    - alert_type: 'critical', 'warning', or 'info'
    - recipients: Comma-separated email addresses
    - All sensor readings for detailed report
    """
    try:
        from email_service import send_water_quality_alert
        
        # Convert comma-separated string to list
        recipient_list = [email.strip() for email in recipients.split(',') if email.strip()]
        
        sensor_data = {
            'ph': ph,
            'tds': tds,
            'turbidity': turbidity,
            'temperature': temperature,
            'waterLevel': water_level,
            'flowRate': flow_rate
        }
        
        result = send_water_quality_alert(
            alert_type=alert_type,
            sensor_data=sensor_data,
            quality_score=quality_score,
            recipients=recipient_list,
            location=location
        )
        
        return {
            "success": result,
            "message": f"Alert email sent to {len(recipient_list)} recipients" if result else "Failed to send email",
            "alert_type": alert_type,
            "quality_score": quality_score,
            "recipients": recipient_list
        }
        
    except ImportError as e:
        return {"error": f"Email service not available: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


# ==================== Government Complaint Endpoints ====================

@app.post("/api/v1/file-complaint", response_model=Dict, tags=["Complaints"])
async def file_government_complaint(
    location: str = Query("Main Water Tank"),
    quality_score: float = Query(...),
    ph: float = Query(7.0),
    tds: float = Query(250.0),
    turbidity: float = Query(2.5),
    temperature: float = Query(26.0),
    water_level: float = Query(75.0),
    flow_rate: float = Query(5.0),
    language: str = Query("english"),
    user_email: Optional[str] = Query(None)
):
    """
    File an automatic government complaint about poor water quality
    Supports English, Hindi, and Marathi
    """
    try:
        from complaint_service import file_govt_complaint
        
        sensor_data = {
            'ph': ph,
            'tds': tds,
            'turbidity': turbidity,
            'temperature': temperature,
            'waterLevel': water_level,
            'flowRate': flow_rate
        }
        
        result = file_govt_complaint(
            sensor_data=sensor_data,
            quality_score=quality_score,
            location=location,
            language=language,
            user_email=user_email
        )
        
        return result
        
    except ImportError as e:
        return {"error": f"Complaint service not available: {str(e)}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.get("/api/v1/complaint-status/{complaint_id}", response_model=Dict, tags=["Complaints"])
async def get_complaint_status(complaint_id: str):
    """Get status of a filed complaint by ID"""
    try:
        from complaint_service import complaint_service
        
        complaint = complaint_service.get_complaint_status(complaint_id)
        if complaint:
            return {"success": True, "complaint": complaint}
        return {"success": False, "error": "Complaint not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/v1/my-complaints", response_model=Dict, tags=["Complaints"])
async def get_all_complaints():
    """Get all filed complaints"""
    try:
        from complaint_service import complaint_service
        
        complaints = complaint_service.get_all_complaints()
        return {"success": True, "complaints": complaints, "count": len(complaints)}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== Chatbot Endpoints ====================

@app.post("/api/v1/chatbot", response_model=Dict, tags=["Chatbot"])
async def chatbot_message(
    message: str = Query(..., description="User message"),
    language: str = Query("english", description="Language: english, hindi, marathi"),
    ph: Optional[float] = Query(None),
    tds: Optional[float] = Query(None),
    turbidity: Optional[float] = Query(None),
    temperature: Optional[float] = Query(None)
):
    """
    Send message to multilingual water quality chatbot
    Supports English, Hindi, and Marathi
    """
    try:
        from chatbot_service import get_chatbot_response
        
        sensor_data = None
        if any([ph, tds, turbidity, temperature]):
            sensor_data = {
                'ph': ph or 7.0,
                'tds': tds or 250,
                'turbidity': turbidity or 2.5,
                'temperature': temperature or 26
            }
        
        response = get_chatbot_response(message, language, sensor_data)
        return {"success": True, **response}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/v1/chatbot/quick-replies", response_model=Dict, tags=["Chatbot"])
async def get_quick_replies(language: str = Query("english")):
    """Get quick reply suggestions for the chatbot"""
    try:
        from chatbot_service import chatbot
        
        chatbot.set_language(language)
        replies = chatbot.get_quick_replies()
        return {"success": True, "quick_replies": replies, "language": language}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== Run Server ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
