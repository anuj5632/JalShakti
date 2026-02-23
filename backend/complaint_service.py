"""
Auto Government Complaint Service
Automatically files complaints to government water authorities when water quality is poor
"""

import random
import string
from datetime import datetime
from typing import Dict, List, Optional
import json

class ComplaintService:
    def __init__(self):
        self.complaints: List[Dict] = []
        self.govt_departments = [
            {"name": "Jal Jeevan Mission", "code": "JJM", "contact": "1800-180-5544"},
            {"name": "Municipal Water Supply", "code": "MWS", "contact": "1800-233-4567"},
            {"name": "Public Health Engineering", "code": "PHE", "contact": "1800-180-1551"},
            {"name": "District Collector Office", "code": "DCO", "contact": "1800-180-1234"}
        ]
        
    def generate_complaint_id(self) -> str:
        """Generate unique complaint tracking ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"WQ-{timestamp}-{random_suffix}"
    
    def get_complaint_template(self, language: str, sensor_data: Dict, quality_score: float, location: str) -> Dict:
        """Get complaint text in specified language"""
        
        templates = {
            "english": {
                "subject": f"Urgent: Poor Water Quality Alert - Score {quality_score:.1f}%",
                "body": f"""
Dear Sir/Madam,

I am writing to report a serious water quality issue in our area.

COMPLAINT DETAILS:
------------------
Location: {location}
Date/Time: {datetime.now().strftime("%d/%m/%Y %H:%M")}
Water Quality Score: {quality_score:.1f}% (Below Safe Limit)

SENSOR READINGS:
----------------
• pH Level: {sensor_data.get('ph', 'N/A')} (Safe: 6.5-8.5)
• TDS: {sensor_data.get('tds', 'N/A')} ppm (Safe: <500 ppm)
• Turbidity: {sensor_data.get('turbidity', 'N/A')} NTU (Safe: <5 NTU)
• Temperature: {sensor_data.get('temperature', 'N/A')}°C

ISSUE DESCRIPTION:
------------------
The water supply in our locality has been contaminated for an extended period. Despite multiple informal complaints, no action has been taken. The water is unfit for drinking and poses serious health risks to residents, especially children and elderly.

We request immediate investigation and corrective action.

Regards,
Concerned Citizen
(via JalShakti Water Monitoring System)
                """,
                "urgency": "HIGH" if quality_score < 50 else "MEDIUM"
            },
            "hindi": {
                "subject": f"अत्यावश्यक: खराब पानी की गुणवत्ता - स्कोर {quality_score:.1f}%",
                "body": f"""
माननीय महोदय/महोदया,

मैं हमारे क्षेत्र में पानी की गुणवत्ता की गंभीर समस्या की शिकायत दर्ज करना चाहता/चाहती हूं।

शिकायत विवरण:
--------------
स्थान: {location}
दिनांक/समय: {datetime.now().strftime("%d/%m/%Y %H:%M")}
पानी गुणवत्ता स्कोर: {quality_score:.1f}% (सुरक्षित सीमा से नीचे)

सेंसर रीडिंग:
-------------
• pH स्तर: {sensor_data.get('ph', 'N/A')} (सुरक्षित: 6.5-8.5)
• TDS: {sensor_data.get('tds', 'N/A')} ppm (सुरक्षित: <500 ppm)
• टर्बिडिटी: {sensor_data.get('turbidity', 'N/A')} NTU (सुरक्षित: <5 NTU)
• तापमान: {sensor_data.get('temperature', 'N/A')}°C

समस्या विवरण:
-------------
हमारे इलाके में पानी की आपूर्ति लंबे समय से दूषित है। कई अनौपचारिक शिकायतों के बावजूद, कोई कार्रवाई नहीं हुई है। पानी पीने योग्य नहीं है और निवासियों, विशेषकर बच्चों और बुजुर्गों के लिए गंभीर स्वास्थ्य खतरा है।

कृपया तत्काल जांच और सुधारात्मक कार्रवाई करें।

सादर,
चिंतित नागरिक
(जलशक्ति जल निगरानी प्रणाली द्वारा)
                """,
                "urgency": "उच्च" if quality_score < 50 else "मध्यम"
            },
            "marathi": {
                "subject": f"तातडीचे: खराब पाण्याची गुणवत्ता - स्कोअर {quality_score:.1f}%",
                "body": f"""
माननीय महोदय/महोदया,

मी आमच्या परिसरातील पाण्याच्या गुणवत्तेच्या गंभीर समस्येबद्दल तक्रार नोंदवू इच्छितो/इच्छिते.

तक्रार तपशील:
--------------
ठिकाण: {location}
दिनांक/वेळ: {datetime.now().strftime("%d/%m/%Y %H:%M")}
पाणी गुणवत्ता स्कोअर: {quality_score:.1f}% (सुरक्षित मर्यादेपेक्षा कमी)

सेन्सर रीडिंग:
-------------
• pH पातळी: {sensor_data.get('ph', 'N/A')} (सुरक्षित: 6.5-8.5)
• TDS: {sensor_data.get('tds', 'N/A')} ppm (सुरक्षित: <500 ppm)
• टर्बिडिटी: {sensor_data.get('turbidity', 'N/A')} NTU (सुरक्षित: <5 NTU)
• तापमान: {sensor_data.get('temperature', 'N/A')}°C

समस्या वर्णन:
-------------
आमच्या परिसरातील पाणी पुरवठा बराच काळ दूषित आहे. अनेक अनौपचारिक तक्रारी करूनही काहीच कारवाई झाली नाही. पाणी पिण्यायोग्य नाही आणि रहिवाशांना, विशेषतः मुले आणि वृद्धांना गंभीर आरोग्य धोका आहे.

कृपया तातडीने तपासणी आणि सुधारात्मक कारवाई करा.

आदरपूर्वक,
चिंतित नागरिक
(जलशक्ती जल निगरानी प्रणाली द्वारे)
                """,
                "urgency": "उच्च" if quality_score < 50 else "मध्यम"
            }
        }
        
        return templates.get(language, templates["english"])
    
    def file_complaint(self, sensor_data: Dict, quality_score: float, location: str, 
                       language: str = "english", user_email: Optional[str] = None) -> Dict:
        """File an automatic government complaint"""
        
        complaint_id = self.generate_complaint_id()
        template = self.get_complaint_template(language, sensor_data, quality_score, location)
        
        # Select appropriate government department based on severity
        if quality_score < 50:
            dept = self.govt_departments[3]  # District Collector for critical
        elif quality_score < 70:
            dept = self.govt_departments[0]  # Jal Jeevan Mission for warning
        else:
            dept = self.govt_departments[1]  # Municipal Water Supply
        
        complaint = {
            "complaint_id": complaint_id,
            "filed_at": datetime.now().isoformat(),
            "status": "SUBMITTED",
            "department": dept,
            "subject": template["subject"],
            "body": template["body"],
            "urgency": template["urgency"],
            "sensor_data": sensor_data,
            "quality_score": quality_score,
            "location": location,
            "language": language,
            "user_email": user_email,
            "timeline": [
                {"status": "SUBMITTED", "timestamp": datetime.now().isoformat(), "note": "Complaint registered in government portal"}
            ]
        }
        
        self.complaints.append(complaint)
        
        return {
            "success": True,
            "complaint_id": complaint_id,
            "department": dept["name"],
            "department_code": dept["code"],
            "helpline": dept["contact"],
            "status": "SUBMITTED",
            "urgency": template["urgency"],
            "message": self._get_success_message(language, complaint_id, dept["name"])
        }
    
    def _get_success_message(self, language: str, complaint_id: str, dept_name: str) -> str:
        messages = {
            "english": f"Complaint {complaint_id} successfully filed with {dept_name}. You will receive updates on your registered email.",
            "hindi": f"शिकायत {complaint_id} सफलतापूर्वक {dept_name} में दर्ज की गई। आपको अपने पंजीकृत ईमेल पर अपडेट मिलेंगे।",
            "marathi": f"तक्रार {complaint_id} {dept_name} मध्ये यशस्वीरित्या नोंदवली गेली. तुम्हाला तुमच्या नोंदणीकृत ईमेलवर अपडेट्स मिळतील."
        }
        return messages.get(language, messages["english"])
    
    def get_complaint_status(self, complaint_id: str) -> Optional[Dict]:
        """Get status of a filed complaint"""
        for complaint in self.complaints:
            if complaint["complaint_id"] == complaint_id:
                return complaint
        return None
    
    def get_all_complaints(self) -> List[Dict]:
        """Get all filed complaints"""
        return self.complaints

# Global instance
complaint_service = ComplaintService()

def file_govt_complaint(sensor_data: Dict, quality_score: float, location: str,
                        language: str = "english", user_email: Optional[str] = None) -> Dict:
    """Convenience function to file complaint"""
    return complaint_service.file_complaint(sensor_data, quality_score, location, language, user_email)
