# boot.py -- run on boot-up
import network, utime
import socket

# Replace the following with your WIFI Credentials
SSID = #"Wi-Fi Name"
SSID_PASSWORD = #"Wi-fi Password"


def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSID_PASSWORD)
        while not sta_if.isconnected():
            print("Attempting to connect....")
            utime.sleep(1)
    print('Connected! Network config:', sta_if.ifconfig())
    
print("Connecting to your wifi...")
do_connect()
