import RPi.GPIO as GPIO
import requests
import os
import signal
import json
import time

STATUS_URL = 'https://hackaton.azurewebsites.net/status'
PINS = [25, 8, 7, 11]

STATE = dict([(25,0), (8,0), (7,0)])

def get_status():
    r = requests.get(STATUS_URL)

    if r.status_code == 200:
        res = r.json()
        return res['status']


def show_status(status):
    print(status)
    pin = None
    if status == "Failure":
        pin = 25
    elif status == "InProgress":
        pin = 8
    elif status == "Success":
        pin = 7

    if status == "Failure" and STATE[25] == 0:
            GPIO.output(11, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(11, GPIO.HIGH)

    STATE[pin] = 1
    [GPIO.output(k, GPIO.HIGH) if v is 0 else GPIO.output(k, GPIO.LOW) for k,v in STATE.items()]

def sigterm_handler(a1, a2):
    GPIO.cleanup(PINS)
    os.exit(0)

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(PINS, GPIO.OUT, initial=GPIO.HIGH)

    child_pid = None
    try:
        child_pid = os.fork()
        if child_pid == 0:
            signal.signal(signal.SIGTERM, sigterm_handler)
            #GPIO.setmode(GPIO.BCM)
            GPIO.setup(PINS, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.output(11, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(11, GPIO.HIGH)
            try:
                while True:
                    status = get_status()
                    show_status(status)
                    time.sleep(10)
            except KeyboardInterrupt:
                sigterm_handler()
        else:
            pid, status = os.waitpid(child_pid, 0)
    except KeyboardInterrupt:
        os.kill(child_pid, signal.SIGTERM)
        #GPIO.cleanup(PINS)

    #GPIO.cleanup(PINS)

