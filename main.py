import RPi.GPIO as GPIO
import requests
import os
import signal
import json
import time

STATUS_URL = 'https://hackaton.azurewebsites.net/status'
ACTION_URL = 'https://hackaton.azurewebsites.net/action'
PINS_OUT = [25, 8, 7, 11]
PIN_IN = 24

STATE = dict([(pin, 0) for pin in PINS_OUT])

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
            time.sleep(0.25)
            GPIO.output(11, GPIO.HIGH)

    [set_state(k,0) if k != pin else set_state(k, 1) for k,v in STATE.items()]
    [GPIO.output(k, GPIO.HIGH) if v is 0 else GPIO.output(k, GPIO.LOW) for k,v in STATE.items()]

def set_state(pin, value):
    STATE[pin] = value

def lamp_sigterm_handler(a1, a2):
    GPIO.cleanup(PINS_OUT)
    os.exit(0)

def button_sigterm_handler(a1, a2):
    GPIO.remove_event_detect(PIN_IN)
    GPIO.cleanup(PIN_IN)
    os.exit(0)

def on_button_pressed():
    print('Button pressed!')
    r = requests.post(ACTION_URL, data= {})

    if r.status_code != 200:
        print(f'NOPE! -  ${r.status_code}')

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(PINS, GPIO.OUT, initial=GPIO.HIGH)

    lamp_pid, button_pid = None, None
    try:
        lamp_pid = os.fork()
        if lamp_pid == 0:
            # lamp child
            signal.signal(signal.SIGTERM, lamp_sigterm_handler)
            GPIO.setup(PINS_OUT, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.output(11, GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(11, GPIO.HIGH)
            try:
                while True:
                    status = get_status()
                    show_status(status)
                    time.sleep(10)
            except KeyboardInterrupt:
                lamp_sigterm_handler()
        else:
            button_pid = os.fork()
            if button_pid == 0:
                # button child
                signal.signal(signal.SIGTERM, button_sigterm_handler)
                GPIO.setup(PIN_IN, GPIO.IN)

                try:
                    GPIO.add_event_detect(PIN_IN, GPIO.RISING, callback=on_button_pressed, bouncetime=10000)
                    while True:
                        time.sleep(1)

                except KeyboardInterrupt:
                    button_sigterm_handler()


            # parent
            for child in [lamp_pid, button_pid]:
                os.waitpid(child, 0)

    except KeyboardInterrupt:
        os.kill(lamp_pid, signal.SIGTERM)
        os.kill(button_pid, signal.SIGTERM)
        #GPIO.cleanup(PINS)

    #GPIO.cleanup(PINS)

