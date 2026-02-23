# boot.py — Runs on ESP32 boot (Wokwi simulation)
# Connects to WiFi network

import network
import time
from config import WIFI_SSID, WIFI_PASSWORD


def connect_wifi():
    """Connect ESP32 to WiFi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("[WiFi] Already connected")
        print("[WiFi] IP:", wlan.ifconfig()[0])
        return

    print(f"[WiFi] Connecting to {WIFI_SSID}...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        print(".", end="")

    if wlan.isconnected():
        print(f"\n[WiFi] Connected! IP: {wlan.ifconfig()[0]}")
    else:
        print("\n[WiFi] Connection failed!")


connect_wifi()
