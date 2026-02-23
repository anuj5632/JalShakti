"""
Alert Service - SMS notifications via Twilio and Fast2SMS
"""
from twilio.rest import Client
import requests
from typing import Dict, List, Optional
from config import settings
import asyncio


class AlertService:
    def __init__(self):
        self.twilio_client = None
        self._init_twilio()
    
    def _init_twilio(self):
        """Initialize Twilio client"""
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                print("✓ Twilio client initialized")
            except Exception as e:
                print(f"⚠ Twilio initialization error: {e}")
        else:
            print("⚠ Twilio credentials not configured")
    
    async def send_sms_twilio(self, to_number: str, message: str) -> Dict:
        """Send SMS via Twilio"""
        if not self.twilio_client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            msg = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            return {
                "success": True,
                "sid": msg.sid,
                "status": msg.status
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_sms_fast2sms(self, to_number: str, message: str) -> Dict:
        """Send SMS via Fast2SMS (India)"""
        if not settings.FAST2SMS_API_KEY:
            return {"success": False, "error": "Fast2SMS not configured"}
        
        try:
            url = "https://www.fast2sms.com/dev/bulkV2"
            
            # Remove country code if present
            phone = to_number.replace("+91", "").replace(" ", "")
            
            payload = {
                "route": "q",  # Quick SMS route
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": phone
            }
            
            headers = {
                "authorization": settings.FAST2SMS_API_KEY,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            
            if result.get("return"):
                return {"success": True, "request_id": result.get("request_id")}
            else:
                return {"success": False, "error": result.get("message")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_alert(
        self, 
        phone_number: str, 
        alert_type: str, 
        source_name: str,
        metric: str,
        value: float,
        threshold: float,
        severity: str = "warning"
    ) -> Dict:
        """
        Send alert SMS to user
        """
        # Format message based on severity
        emoji = "⚠️" if severity == "warning" else "🚨"
        
        message = f"""
{emoji} AquaGuard Alert

Source: {source_name}
Issue: {alert_type}
{metric}: {value:.2f} (Threshold: {threshold:.2f})

Action required. Check your water quality dashboard.
""".strip()
        
        # Try Twilio first, then Fast2SMS
        if self.twilio_client:
            result = await self.send_sms_twilio(phone_number, message)
        elif settings.FAST2SMS_API_KEY:
            result = await self.send_sms_fast2sms(phone_number, message)
        else:
            # Log alert instead
            print(f"ALERT (no SMS configured): {message}")
            result = {"success": True, "method": "console"}
        
        return result
    
    def generate_alert_message(
        self,
        anomalous_metrics: List[str],
        reading: Dict,
        source_name: str
    ) -> str:
        """Generate comprehensive alert message"""
        lines = [f"🚨 Water Quality Alert - {source_name}", ""]
        
        metric_names = {
            'ph': 'pH Level',
            'tds': 'TDS',
            'turbidity': 'Turbidity',
            'flow_rate': 'Flow Rate',
            'water_level': 'Water Level'
        }
        
        units = {
            'ph': '',
            'tds': ' mg/L',
            'turbidity': ' NTU',
            'flow_rate': ' L/min',
            'water_level': '%'
        }
        
        for metric in anomalous_metrics:
            name = metric_names.get(metric, metric)
            value = reading.get(metric, 0)
            unit = units.get(metric, '')
            lines.append(f"• {name}: {value:.2f}{unit}")
        
        lines.extend([
            "",
            "Please check your water source immediately.",
            "- AquaGuard"
        ])
        
        return "\n".join(lines)
    
    async def process_reading_alerts(
        self,
        reading: Dict,
        analysis: Dict,
        user_phone: str,
        source_name: str
    ) -> List[Dict]:
        """
        Process a reading and send alerts if needed
        """
        sent_alerts = []
        
        if not analysis['is_anomaly']:
            return sent_alerts
        
        # Determine severity
        severity = "warning"
        if analysis['quality_score'] < 25:
            severity = "critical"
        elif len(analysis['anomalous_metrics']) >= 3:
            severity = "critical"
        
        # Send consolidated alert
        if analysis['anomalous_metrics']:
            message = self.generate_alert_message(
                analysis['anomalous_metrics'],
                reading,
                source_name
            )
            
            result = await self.send_alert(
                phone_number=user_phone,
                alert_type="Water Quality Anomaly",
                source_name=source_name,
                metric=", ".join(analysis['anomalous_metrics']),
                value=analysis['quality_score'],
                threshold=50,
                severity=severity
            )
            
            sent_alerts.append({
                "type": "anomaly",
                "severity": severity,
                "metrics": analysis['anomalous_metrics'],
                "result": result
            })
        
        return sent_alerts


# Singleton instance
alert_service = AlertService()
