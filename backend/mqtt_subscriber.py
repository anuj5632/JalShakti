"""
MQTT Subscriber - Listens for sensor data from ESP32 devices
"""
import json
import paho.mqtt.client as mqtt
from typing import Callable, Dict, Optional
import asyncio
from datetime import datetime
from config import settings


class MQTTSubscriber:
    def __init__(self):
        self.client = mqtt.Client(client_id="aquaguard-backend")
        self.connected = False
        self.on_message_callback: Optional[Callable] = None
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Set credentials if available
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(
                settings.MQTT_USERNAME,
                settings.MQTT_PASSWORD
            )
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            print(f"✓ Connected to MQTT broker: {settings.MQTT_BROKER}")
            
            # Subscribe to all aquaguard topics
            topic = f"{settings.MQTT_TOPIC_PREFIX}/#"
            client.subscribe(topic, qos=1)
            print(f"✓ Subscribed to: {topic}")
        else:
            print(f"✗ MQTT connection failed with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker"""
        self.connected = False
        print(f"⚠ Disconnected from MQTT broker (code: {rc})")
        
        if rc != 0:
            print("Attempting to reconnect...")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"📨 Received: {topic}")
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = {"raw": payload}
            
            # Extract source info from topic
            # Topic format: aquaguard/{user_id}/{source_id}
            parts = topic.split('/')
            if len(parts) >= 3:
                data['user_id'] = parts[1]
                data['source_id'] = parts[2]
            
            data['received_at'] = datetime.utcnow().isoformat()
            data['topic'] = topic
            
            # Call the registered callback
            if self.on_message_callback:
                asyncio.create_task(self.on_message_callback(data))
                
        except Exception as e:
            print(f"✗ Error processing message: {e}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            print(f"Connecting to MQTT broker: {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
            self.client.connect(
                settings.MQTT_BROKER,
                settings.MQTT_PORT,
                keepalive=60
            )
            self.client.loop_start()
        except Exception as e:
            print(f"✗ Failed to connect to MQTT broker: {e}")
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
    
    def set_message_callback(self, callback: Callable):
        """Set callback for incoming messages"""
        self.on_message_callback = callback
    
    def publish(self, topic: str, payload: Dict):
        """Publish a message to a topic"""
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=1)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"✗ Failed to publish: {e}")
            return False


# Singleton instance
mqtt_subscriber = MQTTSubscriber()


# Message handler that will be called from main.py
async def handle_sensor_data(data: Dict):
    """
    Process incoming sensor data
    This function should be connected to the necessary services
    """
    from firebase_service import firebase_service
    from ml_engine import ml_engine
    from alert_service import alert_service
    
    try:
        source_id = data.get('source_id')
        user_id = data.get('user_id')
        
        if not source_id or not user_id:
            print("⚠ Missing source_id or user_id in data")
            return
        
        # Extract sensor readings
        reading = {
            'ph': data.get('ph', 7.0),
            'tds': data.get('tds', 200),
            'turbidity': data.get('turbidity', 2.0),
            'flow_rate': data.get('flow_rate', 5.0),
            'water_level': data.get('water_level', 50),
            'temperature': data.get('temperature'),
            'source_id': source_id,
            'user_id': user_id,
            'timestamp': data.get('received_at')
        }
        
        # Analyze with ML
        analysis = ml_engine.analyze_reading(reading)
        
        # Add analysis to reading
        reading['is_anomaly'] = analysis['is_anomaly']
        reading['anomaly_score'] = analysis['anomaly_score']
        reading['quality_score'] = analysis['quality_score']
        
        # Store in Firebase
        await firebase_service.store_sensor_reading(reading)
        
        # Send alerts if anomaly detected
        if analysis['is_anomaly']:
            # Get user and source info
            user = await firebase_service.get_user(user_id)
            source = await firebase_service.get_source(source_id)
            
            if user and source:
                phone = user.get('phone')
                source_name = source.get('name', 'Unknown Source')
                
                if phone:
                    await alert_service.process_reading_alerts(
                        reading, analysis, phone, source_name
                    )
                
                # Create alert record
                await firebase_service.create_alert({
                    'user_id': user_id,
                    'source_id': source_id,
                    'title': 'Water Quality Anomaly Detected',
                    'message': f"Anomalous readings detected: {', '.join(analysis['anomalous_metrics'])}",
                    'severity': 'critical' if analysis['quality_score'] < 25 else 'warning',
                    'metric': ', '.join(analysis['anomalous_metrics']),
                    'value': analysis['quality_score'],
                    'threshold': 50
                })
        
        print(f"✓ Processed reading for {source_id}: Quality={analysis['quality_score']}, Anomaly={analysis['is_anomaly']}")
        
    except Exception as e:
        print(f"✗ Error handling sensor data: {e}")
