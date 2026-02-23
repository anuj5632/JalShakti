"""
Firebase Service - Handles Firestore and Realtime Database operations
"""
import firebase_admin
from firebase_admin import credentials, firestore, db
from typing import Optional, Dict, List, Any
from datetime import datetime
import json
import os
from config import settings


class FirebaseService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FirebaseService._initialized:
            self._init_firebase()
            FirebaseService._initialized = True
    
    def _init_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': settings.FIREBASE_DATABASE_URL
                })
                self.firestore_db = firestore.client()
                print("✓ Firebase initialized successfully")
            else:
                print("⚠ Firebase credentials file not found. Running in mock mode.")
                self.firestore_db = None
        except Exception as e:
            print(f"⚠ Firebase initialization error: {e}. Running in mock mode.")
            self.firestore_db = None
    
    # ==================== User Operations ====================
    
    async def create_user(self, user_data: Dict) -> Dict:
        """Create or update user profile in Firestore"""
        if not self.firestore_db:
            return {"status": "mock", "data": user_data}
        
        user_ref = self.firestore_db.collection('users').document(user_data['uid'])
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        user_ref.set(user_data, merge=True)
        return user_data
    
    async def get_user(self, uid: str) -> Optional[Dict]:
        """Get user profile from Firestore"""
        if not self.firestore_db:
            return None
        
        user_ref = self.firestore_db.collection('users').document(uid)
        doc = user_ref.get()
        return doc.to_dict() if doc.exists else None
    
    async def update_user(self, uid: str, update_data: Dict) -> Dict:
        """Update user profile in Firestore"""
        if not self.firestore_db:
            return {"status": "mock", "data": update_data}
        
        user_ref = self.firestore_db.collection('users').document(uid)
        update_data['updated_at'] = datetime.utcnow()
        user_ref.update(update_data)
        return update_data
    
    async def setup_home(self, uid: str, home_data: Dict) -> Dict:
        """Setup home details for user"""
        if not self.firestore_db:
            return {"status": "mock", "data": home_data}
        
        user_ref = self.firestore_db.collection('users').document(uid)
        home_data['home_setup_complete'] = True
        home_data['updated_at'] = datetime.utcnow()
        user_ref.update(home_data)
        return home_data
    
    # ==================== Water Source Operations ====================
    
    async def create_source(self, source_data: Dict) -> Dict:
        """Create a new water source"""
        if not self.firestore_db:
            source_data['id'] = f"mock_{datetime.utcnow().timestamp()}"
            return source_data
        
        source_ref = self.firestore_db.collection('water_sources').document()
        source_data['id'] = source_ref.id
        source_data['created_at'] = datetime.utcnow()
        source_data['updated_at'] = datetime.utcnow()
        source_data['mqtt_topic'] = f"{settings.MQTT_TOPIC_PREFIX}/{source_data['user_id']}/{source_ref.id}"
        source_ref.set(source_data)
        return source_data
    
    async def get_sources(self, user_id: str) -> List[Dict]:
        """Get all water sources for a user"""
        if not self.firestore_db:
            return []
        
        sources = self.firestore_db.collection('water_sources')\
            .where('user_id', '==', user_id)\
            .stream()
        return [doc.to_dict() for doc in sources]
    
    async def get_source(self, source_id: str) -> Optional[Dict]:
        """Get a specific water source"""
        if not self.firestore_db:
            return None
        
        source_ref = self.firestore_db.collection('water_sources').document(source_id)
        doc = source_ref.get()
        return doc.to_dict() if doc.exists else None
    
    async def update_source(self, source_id: str, update_data: Dict) -> Dict:
        """Update a water source"""
        if not self.firestore_db:
            return {"status": "mock", "data": update_data}
        
        source_ref = self.firestore_db.collection('water_sources').document(source_id)
        update_data['updated_at'] = datetime.utcnow()
        source_ref.update(update_data)
        return update_data
    
    async def delete_source(self, source_id: str) -> bool:
        """Delete a water source"""
        if not self.firestore_db:
            return True
        
        source_ref = self.firestore_db.collection('water_sources').document(source_id)
        source_ref.delete()
        return True
    
    # ==================== Sensor Data Operations ====================
    
    async def store_sensor_reading(self, reading: Dict) -> Dict:
        """Store sensor reading in Realtime Database"""
        if not self.firestore_db:
            return {"status": "mock", "data": reading}
        
        try:
            # Store in Realtime Database for real-time updates
            ref = db.reference(f"readings/{reading['source_id']}")
            reading['timestamp'] = datetime.utcnow().isoformat()
            ref.push(reading)
            
            # Also store latest reading
            latest_ref = db.reference(f"latest/{reading['source_id']}")
            latest_ref.set(reading)
            
            return reading
        except Exception as e:
            print(f"Error storing reading: {e}")
            return reading
    
    async def get_readings(self, source_id: str, limit: int = 100) -> List[Dict]:
        """Get sensor readings for a source"""
        if not self.firestore_db:
            return []
        
        try:
            ref = db.reference(f"readings/{source_id}")
            readings = ref.order_by_key().limit_to_last(limit).get()
            if readings:
                return list(readings.values())
            return []
        except Exception as e:
            print(f"Error getting readings: {e}")
            return []
    
    async def get_latest_reading(self, source_id: str) -> Optional[Dict]:
        """Get latest sensor reading for a source"""
        if not self.firestore_db:
            return None
        
        try:
            ref = db.reference(f"latest/{source_id}")
            return ref.get()
        except Exception as e:
            print(f"Error getting latest reading: {e}")
            return None
    
    # ==================== Alert Operations ====================
    
    async def create_alert(self, alert_data: Dict) -> Dict:
        """Create a new alert"""
        if not self.firestore_db:
            alert_data['id'] = f"mock_{datetime.utcnow().timestamp()}"
            return alert_data
        
        alert_ref = self.firestore_db.collection('alerts').document()
        alert_data['id'] = alert_ref.id
        alert_data['created_at'] = datetime.utcnow()
        alert_data['status'] = 'active'
        alert_ref.set(alert_data)
        return alert_data
    
    async def get_alerts(self, user_id: str, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get alerts for a user"""
        if not self.firestore_db:
            return []
        
        query = self.firestore_db.collection('alerts')\
            .where('user_id', '==', user_id)
        
        if status:
            query = query.where('status', '==', status)
        
        query = query.order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)
        
        return [doc.to_dict() for doc in query.stream()]
    
    async def update_alert(self, alert_id: str, update_data: Dict) -> Dict:
        """Update an alert"""
        if not self.firestore_db:
            return {"status": "mock", "data": update_data}
        
        alert_ref = self.firestore_db.collection('alerts').document(alert_id)
        
        if update_data.get('status') == 'acknowledged':
            update_data['acknowledged_at'] = datetime.utcnow()
        elif update_data.get('status') == 'resolved':
            update_data['resolved_at'] = datetime.utcnow()
        
        alert_ref.update(update_data)
        return update_data


# Singleton instance
firebase_service = FirebaseService()
