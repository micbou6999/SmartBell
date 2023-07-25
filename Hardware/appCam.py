#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  	appCam.py
#  	based on tutorial ==> https://blog.miguelgrinberg.com/post/video-streaming-with-flask
# 	PiCam Local Web Server with Flask
# MJRoBot.org 19Jan18

from flask import Flask, render_template, Response
import time 
import threading
import RPi.GPIO as GPIO
# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
TRIG = 17
ECHO = 27
speaker_gpio = 18
GPIO.setup(speaker_gpio, GPIO.OUT)
GPIO.output(speaker_gpio, GPIO.LOW)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
current_distance = 0.0
distance_lock = threading.Lock()
consecutive_distance_count = 0

def check_someone():
    global consecutive_distance_count
    global current_distance

    if consecutive_distance_count >= 2:
        # Someone is at the door
        print("Someone is here", current_distance, consecutive_distance_count)
        GPIO.output(speaker_gpio, GPIO.HIGH)
        time.sleep(2.4)
        GPIO.output(speaker_gpio, GPIO.LOW)
        consecutive_distance_count = 0
        return 200  # Status code for "OK" (someone is at the door)
    else:
        # No one is at the door
        print("No one is here", current_distance, consecutive_distance_count)
        return 404  # Status code for "Not Found" (no one is at the door)

def measure_distance():
    global consecutive_distance_count
    global current_distance
    while True:
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        pulse_start = time.time()
        pulse_end = time.time()
        
        while GPIO.input(ECHO) == 0:
            pulse_start =time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end =time.time()
        
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration *17150
        distance = round(distance,2)
        with distance_lock:
            current_distance = distance
        
        
        if 15.5 <= current_distance <=200:
            consecutive_distance_count += 1
        else:
            consecutive_distance_count = 0
            
        
        check_someone()
        time.sleep(.6)

    
distance_thread =  threading.Thread(target=measure_distance)
distance_thread.daemon = True
distance_thread.start()

@app.route('/livestream')
def livestream():
    """Route to display the live streaming video."""
    return render_template('livestream.html')
@app.route('/')
def index():
    """Video streaming home page."""
    with distance_lock:
        distance = current_distance

    # Get the status code based on whether someone is at the door
    status_code = check_someone()

    # Define the status codes and their corresponding messages
    status_codes = {
        200: "OK (Someone is at the door)",
        404: "Not Found (No one is at the door)",
    }

    # Get the status message corresponding to the status code
    status_message = status_codes.get(status_code, "Unknown Status")

    # Create a dictionary containing both the distance and status message
    data = {
        "distance": distance,
        "status_message": status_message,
    }

    return render_template('index.html', **data)




    
    
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 80, debug=True, threaded=True)
