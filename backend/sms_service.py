"""
SMS Alert Service
Supports multiple SMS providers: Twilio, Fast2SMS, MSG91
"""

import os
import httpx
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """
    Multi-provider SMS service for sending alerts
    """
    
    def __init__(self):
        # Twilio credentials
        self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Fast2SMS (India)
        self.fast2sms_key = os.getenv('FAST2SMS_API_KEY')
        
        # MSG91 (India)
        self.msg91_key = os.getenv('MSG91_API_KEY')
        self.msg91_sender = os.getenv('MSG91_SENDER_ID', 'AQUAGD')
        
        # Determine which provider to use
        self.provider = self._detect_provider()
        
    def _detect_provider(self) -> Optional[str]:
        """Detect which SMS provider is configured"""
        if self.fast2sms_key:
            logger.info("SMS Provider: Fast2SMS")
            return 'fast2sms'
        elif self.twilio_sid and self.twilio_token:
            logger.info("SMS Provider: Twilio")
            return 'twilio'
        elif self.msg91_key:
            logger.info("SMS Provider: MSG91")
            return 'msg91'
        else:
            logger.warning("No SMS provider configured")
            return None
    
    async def send_sms(self, phone_number: str, message: str) -> dict:
        """
        Send SMS using configured provider
        
        Args:
            phone_number: Recipient phone number (with country code for international)
            message: Message text (max 160 chars for single SMS)
            
        Returns:
            Dict with success status and details
        """
        if not self.provider:
            return {
                'success': False,
                'error': 'No SMS provider configured',
                'provider': None
            }
        
        # Clean phone number
        phone_number = phone_number.strip().replace(' ', '').replace('-', '')
        
        try:
            if self.provider == 'fast2sms':
                return await self._send_fast2sms(phone_number, message)
            elif self.provider == 'twilio':
                return await self._send_twilio(phone_number, message)
            elif self.provider == 'msg91':
                return await self._send_msg91(phone_number, message)
        except Exception as e:
            logger.error(f"SMS send error: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider
            }
    
    async def _send_fast2sms(self, phone: str, message: str) -> dict:
        """Send SMS via Fast2SMS (India)"""
        # Remove +91 or 91 prefix if present
        if phone.startswith('+91'):
            phone = phone[3:]
        elif phone.startswith('91') and len(phone) > 10:
            phone = phone[2:]
        
        url = "https://www.fast2sms.com/dev/bulkV2"
        
        headers = {
            "authorization": self.fast2sms_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "route": "q",  # Quick SMS route
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": phone
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()
        
        if data.get('return'):
            return {
                'success': True,
                'message_id': data.get('request_id'),
                'provider': 'fast2sms',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': data.get('message', 'Unknown error'),
                'provider': 'fast2sms'
            }
    
    async def _send_twilio(self, phone: str, message: str) -> dict:
        """Send SMS via Twilio"""
        # Ensure phone has country code
        if not phone.startswith('+'):
            phone = '+91' + phone  # Default to India
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        
        auth = (self.twilio_sid, self.twilio_token)
        
        payload = {
            "From": self.twilio_phone,
            "To": phone,
            "Body": message
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, auth=auth)
            data = response.json()
        
        if response.status_code == 201:
            return {
                'success': True,
                'message_id': data.get('sid'),
                'provider': 'twilio',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': data.get('message', 'Unknown error'),
                'provider': 'twilio'
            }
    
    async def _send_msg91(self, phone: str, message: str) -> dict:
        """Send SMS via MSG91"""
        # Remove +91 prefix if present
        if phone.startswith('+91'):
            phone = phone[3:]
        elif phone.startswith('91') and len(phone) > 10:
            phone = phone[2:]
        
        url = "https://api.msg91.com/api/v5/flow/"
        
        headers = {
            "authkey": self.msg91_key,
            "Content-Type": "application/json"
        }
        
        # For transactional SMS
        payload = {
            "sender": self.msg91_sender,
            "route": "4",  # Transactional
            "country": "91",
            "sms": [{
                "message": message,
                "to": [phone]
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()
        
        if data.get('type') == 'success':
            return {
                'success': True,
                'message_id': data.get('request_id'),
                'provider': 'msg91',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': data.get('message', 'Unknown error'),
                'provider': 'msg91'
            }
    
    async def send_alert(
        self,
        phone_numbers: List[str],
        alert_type: str,
        source_name: str,
        values: dict,
        anomalies: List[str]
    ) -> List[dict]:
        """
        Send water quality alert to multiple numbers
        
        Args:
            phone_numbers: List of recipient phone numbers
            alert_type: 'warning' or 'critical'
            source_name: Name of the water source/tank
            values: Dict with 'ph', 'turbidity', 'tds' values
            anomalies: List of anomaly descriptions
        """
        # Format message
        emoji = "⚠️" if alert_type == 'warning' else "🚨"
        
        message = f"{emoji} AquaGuard Alert\n"
        message += f"Source: {source_name}\n"
        message += f"pH: {values.get('ph', 'N/A'):.2f}\n"
        message += f"Turbidity: {values.get('turbidity', 'N/A'):.1f} NTU\n"
        message += f"TDS: {values.get('tds', 'N/A'):.0f} ppm\n"
        message += f"Issues: {', '.join(anomalies[:2])}"  # Limit to 2 issues for SMS length
        
        # Truncate if too long (SMS limit ~160 chars)
        if len(message) > 160:
            message = message[:157] + "..."
        
        results = []
        for phone in phone_numbers:
            result = await self.send_sms(phone, message)
            result['phone'] = phone
            results.append(result)
        
        return results
    
    def get_status(self) -> dict:
        """Get SMS service status"""
        return {
            'configured': self.provider is not None,
            'provider': self.provider,
            'providers_available': {
                'fast2sms': bool(self.fast2sms_key),
                'twilio': bool(self.twilio_sid and self.twilio_token),
                'msg91': bool(self.msg91_key)
            }
        }


# Singleton instance
sms_service = SMSService()
