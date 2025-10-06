#!/usr/bin/env python3
"""
Raspberry Pi script that manages physical buttons and communicates with the Flask app.
This script must be run on the Raspberry Pi.
"""

import RPi.GPIO as GPIO
import requests
import time
import json
from threading import Thread

# GPIO Configuration
BUTTON_1_PIN = 18  # GPIO 18 for "Choose Variant 1"
BUTTON_2_PIN = 19  # GPIO 19 for "Choose Variant 2"

# Flask application URL (modify with the IP of the computer running the app)
FLASK_APP_URL = "http://144.178.100.238:65500"  # Replace with the correct IP

class PhysicalButtonController:
    def __init__(self):
        self.setup_gpio()
        self.button_pressed = False
        self.last_press_time = 0
        self.debounce_time = 0.3  # 300ms debounce
        
    def setup_gpio(self):
        """Configure GPIO pins"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configure buttons with internal pull-down (no external resistors needed!)
        GPIO.setup(BUTTON_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(BUTTON_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # Callback for button interrupts
        GPIO.add_event_detect(BUTTON_1_PIN, GPIO.RISING, 
                             callback=self.button_1_callback, bouncetime=300)
        GPIO.add_event_detect(BUTTON_2_PIN, GPIO.RISING, 
                             callback=self.button_2_callback, bouncetime=300)
        
        print("GPIO configured. Button 1: GPIO 18, Button 2: GPIO 19")
        
    def button_1_callback(self, channel):
        """Callback for button 1 (Choose Variant 1)"""
        current_time = time.time()
        if current_time - self.last_press_time > self.debounce_time:
            self.last_press_time = current_time
            print("Button 1 pressed - Choose Variant 1")
            self.send_button_press(1)
            
    def button_2_callback(self, channel):
        """Callback for button 2 (Choose Variant 2)"""
        current_time = time.time()
        if current_time - self.last_press_time > self.debounce_time:
            self.last_press_time = current_time
            print("Button 2 pressed - Choose Variant 2")
            self.send_button_press(2)
            
    def send_button_press(self, button_number):
        """Send button press to Flask app"""
        try:
            url = f"{FLASK_APP_URL}/physical-button-press"
            data = {
                'button': button_number,
                'timestamp': time.time()
            }
            
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                print(f"Button {button_number} signal sent successfully")
            else:
                print(f"Send error: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            
    def cleanup(self):
        """GPIO cleanup"""
        GPIO.cleanup()
        
    def run(self):
        """Main loop"""
        print("Physical button controller started...")
        print(f"Connecting to: {FLASK_APP_URL}")
        print("Press Ctrl+C to terminate")
        
        try:
            # Heartbeat to verify connection
            self.check_connection()
            
            while True:
                time.sleep(0.1)  # Light main loop
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
            
    def check_connection(self):
        """Check connection with Flask app"""
        try:
            response = requests.get(f"{FLASK_APP_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✓ Connection with Flask app established")
            else:
                print("⚠ Flask app reachable but with issues")
        except:
            print("✗ Unable to connect to Flask app")
            print(f"Verify that the app is running on {FLASK_APP_URL}")

if __name__ == "__main__":
    controller = PhysicalButtonController()
    controller.run()