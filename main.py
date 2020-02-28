import RPi.GPIO as GPIO
import requests
import os
import signal
import time

STATUS_URL = 'https://hackaton.azurewebsites.net/status'
PINS = [25, 8, 7, 11]

def get_status():
    r = requests.get(STATUS_URL)

    if r.status_code == 200:
        res = json.loads(r.json())
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

    GPIO.output(pin, GPIO.LOW)
    time.sleep(1)
    GPIO.output(pin, GPIO.HIGH)

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PINS, GPIO.OUT, initial=GPIO.HIGH)

    try:
        child_pid = os.fork()
        if child_pid == 0:
            try:
                while True:
                    status = get_status()
                    show_status(status)
                    time.sleep(10)
            except KeyboardInterrupt:
                os.exit(0)
    except KeyboardInterrupt:
        GPIO.cleanup(PINS)

    GPIO.cleanup(PINS)

