import time
import machine
import ubinascii
from umqttsimple import MQTTClient
import dht                 # import the builtin dht library
from machine import Pin    # library for pin access     
from machine import ADC, Pin 

client_id = ubinascii.hexlify(machine.unique_id()) #To create an MQTT client, we need to get the PICOW unique ID
mqtt_broker = "io.adafruit.com" # MQTT broker IP address or DNS  
port = 1883
adafruit_username = #"Adafruit username"
adafruit_password = #"Adafruit password" 
subscribe_topic = b"Mackedaman/f/led"
publish_topic_temp = b"Mackedaman/f/temperature"
publish_topic_hum = b"Mackedaman/f/humidity"
publish_topic_light = b"Mackedaman/f/light"


red = machine.Pin(16,machine.Pin.OUT) # Red LED Pin 16
green = machine.Pin(15,machine.Pin.OUT) #Green LED Pin 15

tempSensor = dht.DHT11(Pin(13))     # DHT11 Pin 13
photoPIN = 26  #The ADC pin of Pico W


# Publish MQTT messages after every set timeout
last_publish = time.time()  # last_publish variable will hold the last time a message was sent.
publish_interval = 6.5 #Publish interval in seconds, (60/publish_interval) * publish topics = amount of datapoints/min (Adafruit Free max 30/min)


# Received messages from subscriptions will be delivered to this callback
# Adafruit IO will publish messages to topic f/led to change state of the LEDs.
# Light >80 (open door) --> Green LED on
# Temperature over 10*C --> Red LED on
def sub_cb(topic, msg):
    print((topic, msg))
    if msg.decode() == "ON":
        red.value(1)
    if msg.decode() == "OFF":
        red.value(0)
    if msg.decode() == "GREEN":
        green.value(1)
    if msg.decode() == "GROFF":
        green.value(0)


# if PicoW Failed to connect to MQTT broker. Reconnecting...'
def reset():
    print("Reconnecting to MQTT Broker...")
    time.sleep(5)
    machine.reset()


def readLight(photoGP):
    photoRes = ADC(Pin(26))
    light = photoRes.read_u16() #16 bits which means 2 bytes. The range of 2 bytes is from 0 to 65535.
    light = round(light/65535*100,2)  # show the result in percentage
    return light

    
def main():
    print(f"Begin connection with MQTT Broker :: {mqtt_broker}")
    mqttClient = MQTTClient(client_id, mqtt_broker, port, adafruit_username, adafruit_password, keepalive=60)
    mqttClient.set_callback(sub_cb) # whenever a new message comes (to picoW), print the topic and message (The call back function will run whenever a message is published on a topic that the PicoW is subscribed to.)
    mqttClient.connect()
    mqttClient.subscribe(subscribe_topic)
    print(f"Connected to MQTT  Broker :: {mqtt_broker}, and waiting for callback function to be called!")
    while True:
            # Non-blocking wait for message
            mqttClient.check_msg()
            global last_publish
            if (time.time() - last_publish) >= publish_interval:
                tempSensor.measure()
                temperature = tempSensor.temperature()
                humidity = tempSensor.humidity()
                mqttClient.publish(publish_topic_temp, str(temperature).encode())
                mqttClient.publish(publish_topic_hum, str(humidity).encode())
                mqttClient.publish(publish_topic_light, str(readLight(photoPIN)).encode())
                last_publish = time.time()
                print("Sent stuff...")
            time.sleep(1)


if __name__ == "__main__":
    while True:
        try:
            main()
        except OSError as e:
            print("Error: " + str(e))
            reset()
