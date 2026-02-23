# main.py — ESP32 Water Quality Monitor (Wokwi MicroPython)
# Reads pH, TDS, Turbidity, Flow, Water Level sensors
# Publishes data to MQTT broker every 10 seconds

import time
import json
import machine
from machine import Pin, ADC, time_pulse_us
from umqtt.simple import MQTTClient
from config import (
    MQTT_BROKER, MQTT_PORT, MQTT_CLIENT_ID,
    MQTT_TOPIC_TANK, MQTT_TOPIC_STORAGE, MQTT_TOPIC_TAP,
    PH_SENSOR_PIN, TDS_SENSOR_PIN, TURBIDITY_SENSOR_PIN,
    FLOW_SENSOR_PIN, LEVEL_TRIGGER_PIN, LEVEL_ECHO_PIN,
    SENSOR_READ_INTERVAL, PH_MIN, PH_MAX, TDS_MAX, TURBIDITY_MAX,
    STAGNATION_HOURS,
)

# ── Sensor Setup ──
ph_adc = ADC(Pin(PH_SENSOR_PIN))
ph_adc.atten(ADC.ATTN_11DB)      # Full 0-3.3V range
ph_adc.width(ADC.WIDTH_12BIT)

tds_adc = ADC(Pin(TDS_SENSOR_PIN))
tds_adc.atten(ADC.ATTN_11DB)
tds_adc.width(ADC.WIDTH_12BIT)

turb_adc = ADC(Pin(TURBIDITY_SENSOR_PIN))
turb_adc.atten(ADC.ATTN_11DB)
turb_adc.width(ADC.WIDTH_12BIT)

flow_pin = Pin(FLOW_SENSOR_PIN, Pin.IN, Pin.PULL_UP)

trigger = Pin(LEVEL_TRIGGER_PIN, Pin.OUT)
echo = Pin(LEVEL_ECHO_PIN, Pin.IN)

# ── Flow counter ──
flow_count = 0
last_flow_time = time.time()


def flow_callback(pin):
    """ISR: count flow sensor pulses."""
    global flow_count, last_flow_time
    flow_count += 1
    last_flow_time = time.time()


flow_pin.irq(trigger=Pin.IRQ_FALLING, handler=flow_callback)


# ──────────────────────────────────────
# Sensor Reading Functions
# ──────────────────────────────────────

def read_ph():
    """Convert ADC reading to pH value (0-14 scale)."""
    raw = ph_adc.read()
    voltage = raw / 4095 * 3.3
    # Linear calibration: pH = -5.70 * voltage + 21.34
    # Adjusted for simulation; calibrate with real sensors
    ph = -5.70 * voltage + 21.34
    return round(max(0, min(14, ph)), 2)


def read_tds():
    """Convert ADC reading to TDS (ppm)."""
    raw = tds_adc.read()
    voltage = raw / 4095 * 3.3
    # TDS conversion formula (simplified)
    tds = (133.42 * voltage ** 3 - 255.86 * voltage ** 2
           + 857.39 * voltage) * 0.5
    return round(max(0, tds), 1)


def read_turbidity():
    """Convert ADC reading to Turbidity (NTU)."""
    raw = turb_adc.read()
    voltage = raw / 4095 * 3.3
    # Simplified conversion: lower voltage = higher turbidity
    turbidity = max(0, (-1120.4 * voltage ** 2
                        + 5742.3 * voltage - 4352.9))
    return round(min(turbidity, 1000), 2)


def read_water_level():
    """Read ultrasonic sensor distance (cm) for water level."""
    trigger.off()
    time.sleep_us(2)
    trigger.on()
    time.sleep_us(10)
    trigger.off()

    try:
        duration = time_pulse_us(echo, 1, 30000)
        if duration < 0:
            return -1
        distance_cm = (duration / 2) / 29.1
        return round(distance_cm, 1)
    except Exception:
        return -1


def get_flow_rate():
    """Return flow pulse count and reset."""
    global flow_count
    count = flow_count
    flow_count = 0
    return count


def check_stagnation():
    """Check if water has been stagnant (no flow) for too long."""
    elapsed_hours = (time.time() - last_flow_time) / 3600
    return elapsed_hours >= STAGNATION_HOURS


def check_thresholds(ph, tds, turbidity):
    """Check if any values exceed safe thresholds."""
    alerts = []
    if ph < PH_MIN or ph > PH_MAX:
        alerts.append(f"pH out of range: {ph}")
    if tds > TDS_MAX:
        alerts.append(f"High TDS: {tds} ppm")
    if turbidity > TURBIDITY_MAX:
        alerts.append(f"High Turbidity: {turbidity} NTU")
    if check_stagnation():
        alerts.append("Water stagnation detected")
    return alerts


# ──────────────────────────────────────
# MQTT Connection
# ──────────────────────────────────────

def connect_mqtt():
    """Establish MQTT connection."""
    print(f"[MQTT] Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("[MQTT] Connected!")
    return client


def publish_data(client, topic, data):
    """Publish JSON data to MQTT topic."""
    payload = json.dumps(data)
    client.publish(topic, payload)
    print(f"[MQTT] Published to {topic}: {payload}")


# ──────────────────────────────────────
# Main Loop
# ──────────────────────────────────────

def main():
    print("=" * 50)
    print("  IoT Water Quality Monitor — Starting")
    print("=" * 50)

    client = connect_mqtt()
    reading_id = 0

    while True:
        reading_id += 1
        print(f"\n--- Reading #{reading_id} ---")

        # Read all sensors
        ph = read_ph()
        tds = read_tds()
        turbidity = read_turbidity()
        flow = get_flow_rate()
        water_level = read_water_level()

        # Check thresholds
        alerts = check_thresholds(ph, tds, turbidity)
        is_anomaly = len(alerts) > 0

        # Build payload
        payload = {
            "ph": ph,
            "tds": tds,
            "turbidity": turbidity,
            "flow": flow,
            "water_level_cm": water_level,
            "temperature": 27.0,  # Placeholder for DS18B20
            "anomaly": is_anomaly,
            "alerts": alerts,
            "stagnation": check_stagnation(),
            "timestamp": time.time(),
            "reading_id": reading_id,
        }

        # Print locally
        print(f"  pH: {ph} | TDS: {tds} | Turbidity: {turbidity}")
        print(f"  Flow: {flow} | Level: {water_level} cm")
        if alerts:
            print(f"  ⚠️  ALERTS: {alerts}")

        # Publish to all monitoring points
        # In production, each sensor cluster publishes to its own topic
        publish_data(client, MQTT_TOPIC_TANK, payload)
        publish_data(client, MQTT_TOPIC_TAP, payload)

        # Sleep before next reading
        time.sleep(SENSOR_READ_INTERVAL)


# Run
try:
    main()
except KeyboardInterrupt:
    print("\n[System] Monitor stopped by user.")
except Exception as e:
    print(f"\n[Error] {e}")
    machine.reset()
