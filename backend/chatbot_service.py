"""
Multilingual Water Quality Chatbot Service
Supports English, Hindi, and Marathi
"""

from typing import Dict, List, Optional
from datetime import datetime
import re

class WaterQualityChatbot:
    def __init__(self):
        self.conversation_history: List[Dict] = []
        self.current_language = "english"
        
        # Knowledge base in all three languages
        self.knowledge_base = {
            "english": {
                "greetings": [
                    "Hello! I'm JalMitra, your water quality assistant. How can I help you today?",
                    "Hi there! I'm here to help you understand your water quality. What would you like to know?",
                    "Welcome! I can help you with water quality information, complaints, and safety tips."
                ],
                "ph": {
                    "question_patterns": ["ph", "acidity", "acidic", "alkaline"],
                    "answer": """**pH Level Information:**
                    
• **Safe Range:** 6.5 - 8.5
• **Below 6.5:** Water is acidic - can corrode pipes, may have metallic taste
• **Above 8.5:** Water is alkaline - may taste bitter, can cause skin irritation

**Health Effects:**
- Acidic water can leach metals from pipes
- Highly alkaline water can cause gastrointestinal issues
- Both extremes can affect taste and cooking

**What to do if pH is abnormal:**
1. Report to water authority immediately
2. Use water filters certified for pH correction
3. Avoid using for drinking until corrected"""
                },
                "tds": {
                    "question_patterns": ["tds", "dissolved solids", "minerals", "ppm"],
                    "answer": """**TDS (Total Dissolved Solids) Information:**

• **Excellent:** < 300 ppm
• **Good:** 300-500 ppm  
• **Fair:** 500-900 ppm
• **Poor:** 900-1200 ppm
• **Unacceptable:** > 1200 ppm

**What TDS measures:**
- Minerals (calcium, magnesium, potassium)
- Salts and metals
- Organic matter

**High TDS effects:**
- Unpleasant taste
- Scale buildup in pipes/appliances
- May indicate contamination

**Recommendation:** Use RO purifier if TDS > 500 ppm"""
                },
                "turbidity": {
                    "question_patterns": ["turbidity", "cloudy", "murky", "clear", "ntu"],
                    "answer": """**Turbidity Information:**

• **Safe Limit:** < 5 NTU (WHO standard)
• **Ideal:** < 1 NTU

**What causes turbidity:**
- Suspended particles (clay, silt)
- Algae and microorganisms  
- Rust from old pipes
- Construction runoff

**Health Risks of high turbidity:**
- Bacteria can hide in particles
- Reduces effectiveness of disinfection
- Indicates potential contamination

**Action Steps:**
1. Let water settle before use
2. Use sediment filters
3. Report persistent turbidity > 5 NTU"""
                },
                "complaint": {
                    "question_patterns": ["complaint", "report", "complain", "government", "authority"],
                    "answer": """**How to File a Water Quality Complaint:**

**Automatic Filing:** Our system can auto-file complaints when quality drops below 70%.

**Manual Options:**
1. **Jal Jeevan Mission Helpline:** 1800-180-5544
2. **CPGRAMS Portal:** pgportal.gov.in
3. **District Collector Office:** Contact local DC
4. **Municipal Corporation:** Local water department

**What to include:**
- Your location/address
- Specific water quality issues
- Duration of problem
- Photos if available

Click the "File Govt Complaint" button on dashboard for instant filing!"""
                },
                "safe_drinking": {
                    "question_patterns": ["safe", "drink", "drinking", "potable", "can i drink"],
                    "answer": """**Is Your Water Safe to Drink?**

**Check these parameters:**
✅ pH: 6.5-8.5
✅ TDS: < 500 ppm
✅ Turbidity: < 5 NTU
✅ No unusual smell or color
✅ No floating particles

**Warning Signs:**
⚠️ Chlorine smell (excess disinfection)
⚠️ Metallic taste (pipe corrosion)
⚠️ Rotten egg smell (hydrogen sulfide)
⚠️ Brown/yellow color (rust/iron)

**When NOT to drink directly:**
- Quality score < 70%
- Any visible particles
- Unusual taste/smell

**Always safer options:**
1. Boil for 1 minute
2. Use certified water purifier
3. UV treatment systems"""
                },
                "purifier": {
                    "question_patterns": ["purifier", "filter", "ro", "uv", "treatment"],
                    "answer": """**Water Purifier Guide:**

**Types of Purifiers:**

1. **RO (Reverse Osmosis)**
   - Best for: High TDS (>500 ppm)
   - Removes: Dissolved salts, heavy metals, bacteria
   - Wastage: 60-70% water

2. **UV (Ultraviolet)**
   - Best for: Low TDS (<500 ppm)
   - Removes: Bacteria, viruses
   - No wastage, no chemical change

3. **UF (Ultra Filtration)**
   - Best for: Municipal water
   - Removes: Bacteria, cysts
   - Works without electricity

4. **RO + UV + UF**
   - Best for: Unknown water quality
   - Complete protection

**Recommendation based on TDS:**
- < 200 ppm: UV filter sufficient
- 200-500 ppm: UV + UF
- > 500 ppm: RO + UV"""
                },
                "health": {
                    "question_patterns": ["health", "disease", "illness", "sick", "symptoms"],
                    "answer": """**Waterborne Diseases & Health Risks:**

**Common Waterborne Diseases:**
1. **Cholera** - Severe diarrhea, dehydration
2. **Typhoid** - High fever, weakness
3. **Hepatitis A** - Liver inflammation
4. **Dysentery** - Bloody diarrhea
5. **Giardiasis** - Stomach cramps, nausea

**Symptoms to watch:**
- Persistent diarrhea
- Stomach cramps
- Nausea/vomiting
- Fever
- Skin rashes

**Prevention:**
✅ Drink only purified water
✅ Wash hands before eating
✅ Clean water storage regularly
✅ Report water quality issues

**Seek medical help if:**
- Symptoms persist > 2 days
- Blood in stool
- High fever
- Severe dehydration"""
                },
                "default": "I'm not sure about that. You can ask me about:\n• pH levels\n• TDS (Total Dissolved Solids)\n• Turbidity\n• Filing complaints\n• Water safety\n• Purifier recommendations\n• Health effects\n\nOr type 'help' for more options!"
            },
            "hindi": {
                "greetings": [
                    "नमस्ते! मैं जलमित्र हूं, आपका जल गुणवत्ता सहायक। मैं आज आपकी कैसे मदद कर सकता हूं?",
                    "नमस्कार! मैं आपको पानी की गुणवत्ता समझने में मदद करने के लिए यहां हूं।",
                    "स्वागत है! मैं पानी की गुणवत्ता, शिकायतों और सुरक्षा सुझावों में मदद कर सकता हूं।"
                ],
                "ph": {
                    "question_patterns": ["ph", "अम्लीय", "क्षारीय", "पीएच"],
                    "answer": """**pH स्तर की जानकारी:**

• **सुरक्षित सीमा:** 6.5 - 8.5
• **6.5 से कम:** पानी अम्लीय है - पाइप को नुकसान पहुंचा सकता है
• **8.5 से अधिक:** पानी क्षारीय है - कड़वा स्वाद हो सकता है

**स्वास्थ्य प्रभाव:**
- अम्लीय पानी पाइप से धातु निकाल सकता है
- अधिक क्षारीय पानी पेट की समस्या कर सकता है

**असामान्य pH होने पर क्या करें:**
1. तुरंत जल प्राधिकरण को रिपोर्ट करें
2. pH सुधार के लिए प्रमाणित फिल्टर का उपयोग करें
3. सुधार होने तक पीने से बचें"""
                },
                "tds": {
                    "question_patterns": ["tds", "टीडीएस", "खनिज", "ppm"],
                    "answer": """**TDS (कुल घुलित ठोस) जानकारी:**

• **उत्कृष्ट:** < 300 ppm
• **अच्छा:** 300-500 ppm
• **ठीक:** 500-900 ppm
• **खराब:** 900-1200 ppm
• **अस्वीकार्य:** > 1200 ppm

**उच्च TDS के प्रभाव:**
- अप्रिय स्वाद
- पाइप में जमाव
- प्रदूषण का संकेत

**सुझाव:** TDS > 500 ppm होने पर RO प्यूरीफायर का उपयोग करें"""
                },
                "complaint": {
                    "question_patterns": ["शिकायत", "रिपोर्ट", "सरकार", "अधिकारी"],
                    "answer": """**पानी की गुणवत्ता की शिकायत कैसे दर्ज करें:**

**स्वचालित दर्ज:** जब गुणवत्ता 70% से कम हो तो हमारी प्रणाली स्वतः शिकायत दर्ज करती है।

**मैन्युअल विकल्प:**
1. **जल जीवन मिशन हेल्पलाइन:** 1800-180-5544
2. **CPGRAMS पोर्टल:** pgportal.gov.in
3. **जिला कलेक्टर कार्यालय**
4. **नगर निगम जल विभाग**

डैशबोर्ड पर "सरकारी शिकायत दर्ज करें" बटन क्लिक करें!"""
                },
                "default": "मुझे इसके बारे में पता नहीं है। आप मुझसे पूछ सकते हैं:\n• pH स्तर\n• TDS\n• टर्बिडिटी\n• शिकायत दर्ज करना\n• पानी की सुरक्षा\n• प्यूरीफायर सुझाव\n• स्वास्थ्य प्रभाव"
            },
            "marathi": {
                "greetings": [
                    "नमस्कार! मी जलमित्र आहे, तुमचा पाणी गुणवत्ता सहाय्यक. मी आज तुम्हाला कशी मदत करू शकतो?",
                    "नमस्ते! मी तुम्हाला पाण्याची गुणवत्ता समजून घेण्यास मदत करण्यासाठी येथे आहे.",
                    "स्वागत आहे! मी पाण्याची गुणवत्ता, तक्रारी आणि सुरक्षा टिप्समध्ये मदत करू शकतो."
                ],
                "ph": {
                    "question_patterns": ["ph", "आम्लता", "अल्कलाइन", "पीएच"],
                    "answer": """**pH पातळी माहिती:**

• **सुरक्षित श्रेणी:** 6.5 - 8.5
• **6.5 पेक्षा कमी:** पाणी आम्लयुक्त आहे - पाईप्स खराब होऊ शकतात
• **8.5 पेक्षा जास्त:** पाणी अल्कलाइन आहे - कडू चव येऊ शकते

**आरोग्य परिणाम:**
- आम्लयुक्त पाणी पाईप्समधून धातू काढू शकते
- जास्त अल्कलाइन पाणी पोटाच्या समस्या निर्माण करू शकते

**असामान्य pH असल्यास काय करावे:**
1. लगेच जल प्राधिकरणाला कळवा
2. pH सुधारणेसाठी प्रमाणित फिल्टर वापरा
3. सुधारणा होईपर्यंत पिणे टाळा"""
                },
                "complaint": {
                    "question_patterns": ["तक्रार", "रिपोर्ट", "सरकार", "अधिकारी"],
                    "answer": """**पाणी गुणवत्तेची तक्रार कशी नोंदवावी:**

**स्वयंचलित नोंदणी:** जेव्हा गुणवत्ता 70% पेक्षा कमी होते तेव्हा आमची प्रणाली आपोआप तक्रार नोंदवते.

**मॅन्युअल पर्याय:**
1. **जल जीवन मिशन हेल्पलाइन:** 1800-180-5544
2. **CPGRAMS पोर्टल:** pgportal.gov.in
3. **जिल्हाधिकारी कार्यालय**
4. **महानगरपालिका जल विभाग**

डॅशबोर्डवर "सरकारी तक्रार नोंदवा" बटण क्लिक करा!"""
                },
                "default": "मला याबद्दल माहिती नाही. तुम्ही मला विचारू शकता:\n• pH पातळी\n• TDS\n• टर्बिडिटी\n• तक्रार नोंदवणे\n• पाण्याची सुरक्षा\n• प्युरिफायर सूचना\n• आरोग्य परिणाम"
            }
        }
        
        # Quick replies for each language
        self.quick_replies = {
            "english": [
                "What is safe pH level?",
                "Is my water safe to drink?",
                "How to file complaint?",
                "Explain TDS",
                "Purifier recommendation",
                "Health risks"
            ],
            "hindi": [
                "सही pH स्तर क्या है?",
                "क्या मेरा पानी पीने योग्य है?",
                "शिकायत कैसे दर्ज करें?",
                "TDS समझाएं",
                "प्यूरीफायर सुझाव",
                "स्वास्थ्य जोखिम"
            ],
            "marathi": [
                "योग्य pH पातळी किती?",
                "माझे पाणी पिण्यायोग्य आहे का?",
                "तक्रार कशी नोंदवावी?",
                "TDS समजावून सांगा",
                "प्युरिफायर सूचना",
                "आरोग्य धोके"
            ]
        }
    
    def set_language(self, language: str) -> str:
        """Set the chatbot language"""
        if language in ["english", "hindi", "marathi"]:
            self.current_language = language
            greetings = self.knowledge_base[language]["greetings"]
            import random
            return random.choice(greetings)
        return "Language not supported. Available: English, Hindi, Marathi"
    
    def get_quick_replies(self) -> List[str]:
        """Get quick reply suggestions for current language"""
        return self.quick_replies.get(self.current_language, self.quick_replies["english"])
    
    def process_message(self, message: str, sensor_data: Optional[Dict] = None) -> Dict:
        """Process user message and return response"""
        message_lower = message.lower()
        lang_data = self.knowledge_base[self.current_language]
        
        # Check for greetings
        greeting_patterns = ["hi", "hello", "hey", "नमस्ते", "नमस्कार", "हाय"]
        if any(greet in message_lower for greet in greeting_patterns):
            import random
            response = random.choice(lang_data["greetings"])
            return {
                "response": response,
                "quick_replies": self.get_quick_replies(),
                "type": "greeting"
            }
        
        # Check knowledge base topics
        for topic, data in lang_data.items():
            if topic in ["greetings", "default"]:
                continue
            if isinstance(data, dict) and "question_patterns" in data:
                if any(pattern in message_lower for pattern in data["question_patterns"]):
                    return {
                        "response": data["answer"],
                        "quick_replies": self.get_quick_replies(),
                        "type": topic
                    }
        
        # Add sensor context if available
        if sensor_data and any(word in message_lower for word in ["current", "reading", "now", "मौजूदा", "वर्तमान", "सध्याचे"]):
            return self._get_current_reading_response(sensor_data)
        
        # Default response
        return {
            "response": lang_data["default"],
            "quick_replies": self.get_quick_replies(),
            "type": "default"
        }
    
    def _get_current_reading_response(self, sensor_data: Dict) -> Dict:
        """Generate response about current sensor readings"""
        responses = {
            "english": f"""**Current Water Quality Readings:**

• **pH:** {sensor_data.get('ph', 'N/A')} {'✅ Safe' if 6.5 <= sensor_data.get('ph', 7) <= 8.5 else '⚠️ Alert'}
• **TDS:** {sensor_data.get('tds', 'N/A')} ppm {'✅ Good' if sensor_data.get('tds', 0) < 500 else '⚠️ High'}
• **Turbidity:** {sensor_data.get('turbidity', 'N/A')} NTU {'✅ Clear' if sensor_data.get('turbidity', 0) < 5 else '⚠️ Cloudy'}
• **Temperature:** {sensor_data.get('temperature', 'N/A')}°C

Would you like more details about any parameter?""",
            "hindi": f"""**वर्तमान पानी गुणवत्ता रीडिंग:**

• **pH:** {sensor_data.get('ph', 'N/A')} {'✅ सुरक्षित' if 6.5 <= sensor_data.get('ph', 7) <= 8.5 else '⚠️ चेतावनी'}
• **TDS:** {sensor_data.get('tds', 'N/A')} ppm {'✅ अच्छा' if sensor_data.get('tds', 0) < 500 else '⚠️ उच्च'}
• **टर्बिडिटी:** {sensor_data.get('turbidity', 'N/A')} NTU {'✅ साफ' if sensor_data.get('turbidity', 0) < 5 else '⚠️ धुंधला'}
• **तापमान:** {sensor_data.get('temperature', 'N/A')}°C

क्या आप किसी पैरामीटर के बारे में अधिक जानकारी चाहते हैं?""",
            "marathi": f"""**सध्याचे पाणी गुणवत्ता रीडिंग:**

• **pH:** {sensor_data.get('ph', 'N/A')} {'✅ सुरक्षित' if 6.5 <= sensor_data.get('ph', 7) <= 8.5 else '⚠️ इशारा'}
• **TDS:** {sensor_data.get('tds', 'N/A')} ppm {'✅ चांगले' if sensor_data.get('tds', 0) < 500 else '⚠️ जास्त'}
• **टर्बिडिटी:** {sensor_data.get('turbidity', 'N/A')} NTU {'✅ स्वच्छ' if sensor_data.get('turbidity', 0) < 5 else '⚠️ धूसर'}
• **तापमान:** {sensor_data.get('temperature', 'N/A')}°C

तुम्हाला कोणत्याही पॅरामीटरबद्दल अधिक माहिती हवी आहे का?"""
        }
        
        return {
            "response": responses.get(self.current_language, responses["english"]),
            "quick_replies": self.get_quick_replies(),
            "type": "current_readings"
        }

# Global instance
chatbot = WaterQualityChatbot()

def get_chatbot_response(message: str, language: str = "english", sensor_data: Optional[Dict] = None) -> Dict:
    """Convenience function for chatbot response"""
    chatbot.set_language(language)
    return chatbot.process_message(message, sensor_data)
