# config.py — ESP32 Configuration for Wokwi Simulation

# ── WiFi Settings ──
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

# ── Backend API Settings ──
# Change this to your backend URL
API_BASE_URL = "http://localhost:8000"  # Local development
# API_BASE_URL = "https://your-api.railway.app"  # Production
API_ENDPOINT = "/api/v1/sensor-data"
DEVICE_ID = "esp32-tank-main"
API_KEY = ""  # Optional: for authentication

# ── MQTT Broker Settings (backup) ──
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "esp32-water-monitor"

# ── MQTT Topics ──
MQTT_TOPIC_TANK = "home/water/tank"
MQTT_TOPIC_STORAGE = "home/water/storage"
MQTT_TOPIC_TAP = "home/water/tap"

# ── Sensor Pin Configuration ──
PH_SENSOR_PIN = 34          # Analog input — pH sensor
TDS_SENSOR_PIN = 35         # Analog input — TDS sensor
TURBIDITY_SENSOR_PIN = 32   # Analog input — Turbidity sensor
FLOW_SENSOR_PIN = 27        # Digital input — Water flow sensor
LEVEL_TRIGGER_PIN = 5       # Ultrasonic Trigger
LEVEL_ECHO_PIN = 18         # Ultrasonic Echo
TEMP_SENSOR_PIN = 4         # DS18B20 Temperature (optional)

# ── Reading Interval ──
SENSOR_READ_INTERVAL = 10   # seconds

# ── Water Quality Thresholds ──
PH_MIN = 6.5
PH_MAX = 8.5
TDS_MAX = 1200
TURBIDITY_MAX = 5.0
STAGNATION_HOURS = 8
