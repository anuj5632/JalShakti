"""
Email Alert Service using Gmail SMTP
Sends detailed water quality alerts via email
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Gmail SMTP Email Service for Water Quality Alerts
    """
    
    def __init__(self):
        # Gmail SMTP Configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Gmail credentials (use App Password, not regular password)
        self.sender_email = os.getenv('GMAIL_EMAIL', 'adityaralhan786@gmail.com')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD', 'zzzbbetkyyqjyxwm')  # Remove spaces
        
        # Default recipients (can be overridden)
        self.default_recipients = os.getenv('ALERT_RECIPIENTS', '').split(',')
        
        logger.info(f"Email Service initialized with sender: {self.sender_email}")
    
    def send_alert(
        self,
        subject: str,
        alert_type: str,
        sensor_data: dict,
        quality_score: float,
        recipients: Optional[List[str]] = None,
        location: str = "Main Water Tank"
    ) -> bool:
        """
        Send a detailed water quality alert email
        
        Args:
            subject: Email subject
            alert_type: 'critical', 'warning', or 'info'
            sensor_data: Current sensor readings
            quality_score: Overall quality score
            recipients: List of email addresses
            location: Location of the sensor
        
        Returns:
            bool: True if email sent successfully
        """
        
        if recipients is None:
            recipients = self.default_recipients
        
        recipients = [r.strip() for r in recipients if r.strip()]
        
        if not recipients:
            logger.warning("No recipients configured for email alerts")
            return False
        
        # Create the email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 JalShakti Alert: {subject}"
        msg['From'] = f"JalShakti Water Monitor <{self.sender_email}>"
        msg['To'] = ', '.join(recipients)
        
        # Generate email content
        text_content = self._generate_text_content(alert_type, sensor_data, quality_score, location)
        html_content = self._generate_html_content(alert_type, sensor_data, quality_score, location)
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        try:
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, recipients, msg.as_string())
            
            logger.info(f"Alert email sent successfully to {len(recipients)} recipients")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {e}")
            logger.error("Check Gmail email and App Password configuration")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _generate_text_content(
        self, 
        alert_type: str, 
        sensor_data: dict, 
        quality_score: float,
        location: str
    ) -> str:
        """Generate plain text email content"""
        
        timestamp = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
        
        alert_emoji = "🔴" if alert_type == "critical" else "🟡" if alert_type == "warning" else "🟢"
        
        status = "CRITICAL - Immediate Action Required" if quality_score < 50 else "WARNING - Review Required" if quality_score < 70 else "Normal"
        
        # Recommended actions based on alert type
        if alert_type == "critical":
            actions = """• STOP water consumption immediately
• Contact water treatment facility
• Arrange for water testing"""
        elif alert_type == "warning":
            actions = """• Monitor water quality closely
• Check water source for contamination
• Consider filtration if issue persists"""
        else:
            actions = "• Continue normal monitoring"
        
        return f"""
{alert_emoji} JALSHAKTI WATER QUALITY ALERT
{'='*50}

Alert Type: {alert_type.upper()}
Location: {location}
Time: {timestamp}

OVERALL QUALITY SCORE: {quality_score:.1f}%
Status: {status}

SENSOR READINGS:
----------------
pH Level: {sensor_data.get('ph', 'N/A')} 
  (Safe range: 6.5 - 8.5)
  
TDS (Total Dissolved Solids): {sensor_data.get('tds', 'N/A')} ppm
  (Safe range: < 500 ppm)
  
Turbidity: {sensor_data.get('turbidity', 'N/A')} NTU
  (Safe range: < 5 NTU)
  
Temperature: {sensor_data.get('temperature', 'N/A')}°C
Water Level: {sensor_data.get('waterLevel', 'N/A')}%
Flow Rate: {sensor_data.get('flowRate', 'N/A')} L/min

RECOMMENDED ACTIONS:
-------------------
{actions}

---
This is an automated alert from JalShakti Water Quality Monitoring System.
Dashboard: http://localhost:3000
"""

    def _generate_html_content(
        self, 
        alert_type: str, 
        sensor_data: dict, 
        quality_score: float,
        location: str
    ) -> str:
        """Generate HTML email content with professional styling"""
        
        timestamp = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
        
        # Colors based on alert type
        if alert_type == "critical":
            primary_color = "#dc2626"
            bg_color = "#fef2f2"
            status_text = "CRITICAL - Immediate Action Required"
            icon = "🔴"
        elif alert_type == "warning":
            primary_color = "#f59e0b"
            bg_color = "#fffbeb"
            status_text = "WARNING - Review Required"
            icon = "🟡"
        else:
            primary_color = "#10b981"
            bg_color = "#ecfdf5"
            status_text = "Normal"
            icon = "🟢"
        
        # Calculate individual parameter status
        ph = sensor_data.get('ph', 7.0)
        tds = sensor_data.get('tds', 200)
        turbidity = sensor_data.get('turbidity', 2.0)
        
        ph_status = "✅" if 6.5 <= ph <= 8.5 else "❌"
        tds_status = "✅" if tds < 500 else "❌"
        turb_status = "✅" if turbidity < 5 else "❌"
        
        # Recommended actions HTML based on alert type
        if alert_type == "critical":
            actions_html = "<li><strong>STOP</strong> water consumption immediately</li><li>Contact water treatment facility</li><li>Arrange for professional water testing</li><li>Check for contamination sources</li>"
        elif alert_type == "warning":
            actions_html = "<li>Monitor water quality closely</li><li>Check water source for potential contamination</li><li>Consider using water filtration</li><li>Schedule professional inspection if issue persists</li>"
        else:
            actions_html = "<li>Continue normal monitoring schedule</li><li>Regular maintenance recommended</li>"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f3f4f6;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: white;">
        <!-- Header -->
        <tr>
            <td style="background: linear-gradient(135deg, {primary_color}, {primary_color}cc); padding: 30px 40px; text-align: center;">
                <h1 style="margin: 0; color: white; font-size: 28px;">
                    {icon} JalShakti Alert
                </h1>
                <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">
                    Water Quality Monitoring System
                </p>
            </td>
        </tr>
        
        <!-- Alert Banner -->
        <tr>
            <td style="background: {bg_color}; padding: 20px 40px; border-left: 4px solid {primary_color};">
                <p style="margin: 0; color: {primary_color}; font-weight: 600; font-size: 16px;">
                    {status_text}
                </p>
                <p style="margin: 8px 0 0; color: #6b7280; font-size: 13px;">
                    📍 {location} &nbsp;|&nbsp; 🕐 {timestamp}
                </p>
            </td>
        </tr>
        
        <!-- Quality Score -->
        <tr>
            <td style="padding: 30px 40px; text-align: center;">
                <div style="display: inline-block; width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, {primary_color}20, {primary_color}10); border: 4px solid {primary_color}; line-height: 112px;">
                    <span style="font-size: 36px; font-weight: 700; color: {primary_color};">{quality_score:.0f}</span>
                    <span style="font-size: 16px; color: {primary_color};">%</span>
                </div>
                <p style="margin: 15px 0 0; color: #374151; font-weight: 600;">Overall Quality Score</p>
            </td>
        </tr>
        
        <!-- Sensor Readings -->
        <tr>
            <td style="padding: 0 40px 30px;">
                <h3 style="margin: 0 0 20px; color: #1f2937; font-size: 16px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">
                    📊 Sensor Readings
                </h3>
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="padding: 12px; background: #f9fafb; border-radius: 8px; margin-bottom: 8px;">
                            <table width="100%">
                                <tr>
                                    <td style="color: #374151; font-weight: 500;">pH Level {ph_status}</td>
                                    <td style="text-align: right; font-weight: 600; color: #1f2937;">{ph}</td>
                                </tr>
                                <tr>
                                    <td colspan="2" style="color: #9ca3af; font-size: 12px; padding-top: 4px;">Safe range: 6.5 - 8.5</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr><td style="height: 8px;"></td></tr>
                    <tr>
                        <td style="padding: 12px; background: #f9fafb; border-radius: 8px;">
                            <table width="100%">
                                <tr>
                                    <td style="color: #374151; font-weight: 500;">TDS {tds_status}</td>
                                    <td style="text-align: right; font-weight: 600; color: #1f2937;">{tds} ppm</td>
                                </tr>
                                <tr>
                                    <td colspan="2" style="color: #9ca3af; font-size: 12px; padding-top: 4px;">Safe range: &lt; 500 ppm</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr><td style="height: 8px;"></td></tr>
                    <tr>
                        <td style="padding: 12px; background: #f9fafb; border-radius: 8px;">
                            <table width="100%">
                                <tr>
                                    <td style="color: #374151; font-weight: 500;">Turbidity {turb_status}</td>
                                    <td style="text-align: right; font-weight: 600; color: #1f2937;">{turbidity} NTU</td>
                                </tr>
                                <tr>
                                    <td colspan="2" style="color: #9ca3af; font-size: 12px; padding-top: 4px;">Safe range: &lt; 5 NTU</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr><td style="height: 8px;"></td></tr>
                    <tr>
                        <td style="padding: 12px; background: #f9fafb; border-radius: 8px;">
                            <table width="100%">
                                <tr>
                                    <td style="color: #374151; font-weight: 500;">Temperature</td>
                                    <td style="text-align: right; font-weight: 600; color: #1f2937;">{sensor_data.get('temperature', 'N/A')}°C</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr><td style="height: 8px;"></td></tr>
                    <tr>
                        <td style="padding: 12px; background: #f9fafb; border-radius: 8px;">
                            <table width="100%">
                                <tr>
                                    <td style="color: #374151; font-weight: 500;">Water Level</td>
                                    <td style="text-align: right; font-weight: 600; color: #1f2937;">{sensor_data.get('waterLevel', 'N/A')}%</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- Recommended Actions -->
        <tr>
            <td style="padding: 0 40px 30px;">
                <div style="background: {bg_color}; border-radius: 12px; padding: 20px; border: 1px solid {primary_color}33;">
                    <h3 style="margin: 0 0 12px; color: {primary_color}; font-size: 14px;">
                        ⚡ Recommended Actions
                    </h3>
                    <ul style="margin: 0; padding-left: 20px; color: #374151; font-size: 14px; line-height: 1.8;">
                        {actions_html}
                    </ul>
                </div>
            </td>
        </tr>
        
        <!-- CTA Button -->
        <tr>
            <td style="padding: 0 40px 30px; text-align: center;">
                <a href="http://localhost:3000" style="display: inline-block; padding: 14px 32px; background: {primary_color}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">
                    View Dashboard →
                </a>
            </td>
        </tr>
        
        <!-- Footer -->
        <tr>
            <td style="background: #1f2937; padding: 25px 40px; text-align: center;">
                <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                    This is an automated alert from JalShakti Water Quality Monitoring System
                </p>
                <p style="margin: 8px 0 0; color: #6b7280; font-size: 11px;">
                    © 2026 JalShakti | NSS Hackathon Project
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    def send_test_email(self, recipient: str) -> bool:
        """Send a test email to verify configuration"""
        
        test_sensor_data = {
            'ph': 7.2,
            'tds': 245,
            'turbidity': 2.1,
            'temperature': 26.5,
            'waterLevel': 72,
            'flowRate': 5.2
        }
        
        return self.send_alert(
            subject="Test Alert - Email Configuration Verified",
            alert_type="info",
            sensor_data=test_sensor_data,
            quality_score=85.0,
            recipients=[recipient],
            location="Test Location"
        )


# Global instance
email_service = EmailService()


def send_water_quality_alert(
    alert_type: str,
    sensor_data: dict,
    quality_score: float,
    recipients: List[str],
    location: str = "Main Water Tank"
) -> bool:
    """
    Convenience function to send water quality alerts
    
    Args:
        alert_type: 'critical', 'warning', or 'info'
        sensor_data: Current sensor readings
        quality_score: Overall quality score (0-100)
        recipients: List of email addresses
        location: Sensor location
    
    Returns:
        bool: True if email sent successfully
    """
    
    if alert_type == "critical":
        subject = f"CRITICAL: Water Quality at {quality_score:.0f}% - Immediate Action Required"
    elif alert_type == "warning":
        subject = f"WARNING: Water Quality Dropped to {quality_score:.0f}%"
    else:
        subject = f"Water Quality Update: {quality_score:.0f}%"
    
    return email_service.send_alert(
        subject=subject,
        alert_type=alert_type,
        sensor_data=sensor_data,
        quality_score=quality_score,
        recipients=recipients,
        location=location
    )
