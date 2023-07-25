#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, render_template, Response, flash, redirect, url_for
import time 
import threading
import RPi.GPIO as GPIO
import pygame
import random
import socket
import subprocess
import os

# Raspberry Pi camera module
from camera_pi import Camera      
GPIO.setwarnings(False)
app = Flask(__name__)
import datetime


# Define a variable to keep track of the last time the ringer was activated

cooldown_time = 10  # Cooldown period in seconds
cooldown_timer = None
buzzed_recently = False 
bluetooth_sound = True

#GPIO PIN Numbers

GPIO.setmode(GPIO.BCM)
TRIG = 17
ECHO = 27
speaker_gpio = 18
led_gpio = 22


#GPIO Initialization

GPIO.setup(led_gpio, GPIO.OUT)
GPIO.output(led_gpio, GPIO.LOW)
GPIO.setup(speaker_gpio, GPIO.OUT)
GPIO.output(speaker_gpio, GPIO.LOW)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)


current_distance = 0.0
distance_lock = threading.Lock()
consecutive_distance_count = 0

sound = ['test4.mp3']
#test with separate file and create separate function for the sound.#

pwm = GPIO.PWM(speaker_gpio, 500)


#Repeatedly attempt to connect to WiFi

def is_connected_to_wifi():
    try:
        host = "8.8.8.8"
        port = 53
        timeout = 3
        socket.create_connection((host,port),timeout = timeout)
        return True
    except OSError:
        pass
    return False


#Play sound for bluetooth

def play_sound():
    global sound
    path = '/home/shre/Downloads/'

    # rand = random.randrange(3)
    path += sound[0]
     
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.5)  # Set the volume to maximum (1.0)
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
buzzed_recently = False  # Flag to keep track of recent buzzing


def play_buzzer(duration):
        # Start the PWM with 50% duty cycle (half volume)
        pwm.start(100)
        

        # Play the buzzer for the specified duration
        
        time.sleep(duration)

        # Stop the PWM (turn off the buzzer)
        pwm.stop()     


def check_someone():
    global consecutive_distance_count
    global buzzed_recently
    global cooldown_timer

    while not is_connected_to_wifi():
        print("Waiting for WiFi connection...")
        time.sleep(5)

    if consecutive_distance_count >= 2:   #Two readings of someone close to the bell

        # Someone is at the door, and it has not buzzed recently

        # Set the flag to indicate that the buzzer has buzzed recently
        buzzed_recently = True

        # Activate the ringer and update the last ring time
        GPIO.output(led_gpio, GPIO.HIGH)
        play_buzzer(1.2)
        GPIO.output(led_gpio, GPIO.LOW)
        if bluetooth_sound == True:
            play_sound()
        
        # Run the bash file for notifications
        try:
            subprocess.run(['bash', 'send_notifications.sh'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing bash script: {e}")
        
        time.sleep(4)
        return 200  # Status code for "OK" (someone is at the door)
    
    else:
        # No one is at the door, or it has buzzed recently
        return 404 
    
def measure_distance():
    global consecutive_distance_count
    global current_distance
    while True:

        #get reading from SR04
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
        
        #check distance threshold 
        if 20 <= current_distance <=120:
            consecutive_distance_count += 1
        else:
            consecutive_distance_count = 0
        status_code = check_someone()
        print("Distance: {} cm, Status Code: {}".format(current_distance, status_code))   
        
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
    # Wait until the device is connected to WiFi before running the web server
    while not is_connected_to_wifi():
        print("Waiting for WiFi connection...")
        time.sleep(5)
    
    app.run(host='169.233.121.206', port=8080, debug=True, threaded=True)
    print("Connected to WiFi. Starting the web server.")
