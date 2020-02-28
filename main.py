import RPi.GPIO as GPIO
import requests

STATUS_URL = 'https://hackaton.azurewebsites.net/status'
PINS = [25, 8, 7, 11]

def get_status():
    res = requests(STATUS_URL)

    print(res.status_code)
    print(res.json())


if __name__ = "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PINS, GPIO.OUT, initial=GPIO.HIGH)

    try:
        get_status()
    except KeyboardInterrupt:
        GPIO.cleanup(PINS)

    GPIO.cleanup(PINS)

