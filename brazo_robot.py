#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import serial
import RPi.GPIO as GPIO

CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class BrazoRobot(object):
    """Class used to wrap action code with mqtt connection

        Please change the name refering to your application
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)
        pin18state = False
        pin23state = False

        # start listening to MQTT
        self.start_blocking()

    # --> Sub callback function, one per intent
    def MoveAxis_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)
        if pin18state == True:
            pin18state = False
            GPIO.output(18, GPIO.LOW)
        else:
            pin18state = True
            GPIO.output(18, GPIO.HIGH)

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, "Moving axis ... ", "")

    def Park_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)
        if pin23state == True:
            pin23state = False
            GPIO.output(23, GPIO.LOW)
        else:
            pin23state = True
            GPIO.output(23, GPIO.HIGH)

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, "Parking ...", "")

    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'Owen:MoveAxis':
            self.MoveAxis_callback(hermes, intent_message)
        if coming_intent == 'Owen:Park':
            self.Park_callback(hermes, intent_message)
        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    BrazoRobot()
