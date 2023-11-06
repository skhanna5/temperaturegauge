import network
from machine import Pin, ADC
from time import sleep
import ubinascii
import urequests as requests
from math import log
import controller as gamepad
import simple as mqtt
import uasyncio as asyncio

airtabletoken = 'patRpTzy9QRwXTAl5.72ea248582c08626b98d88141a931c6b18029c6640b569f7e3b0f6d45025ed9b'
baseid = 'app742BjiRlmmPEao'
tablename = 'Tasks'
url = "https://api.airtable.com/v0/%s/%s" % (baseid, tablename)
headers = {"Authorization": f"Bearer {airtabletoken}",}

USERNAME = b'shivkhanna'
AIOKEY = b'aio_Ggux61X9jfePOVT8OVjDDXpIsa59'
image_key = b'image_processing'
image_feedname = bytes('{:s}/feeds/{:s}'.format(USERNAME, image_key), 'utf-8')
adaurl = b'io.adafruit.com'
mqtt_client_id = b'shiv' 
client = mqtt.MQTTClient(client_id=mqtt_client_id, server=adaurl, user=USERNAME, password=AIOKEY, ssl=False)
print('Testing Adafruit Connection')
sleep(1)
try:            
        client.connect()
        print('Adafruit connection successful!')
        sleep(1)
except Exception as e:
        print('Could not connect to MQTT server {}{}'.format(type(e).__name__, e))

unit = ''
while True:
        print('Reading Airtable API...')
        response = requests.get(url, headers=headers)#, params=params)
        # if response.status_code == 200:
        #     print('Airtable connection successful!')
        try:
                data = response.json()
                records = data.get('records', [])
                for record in records:
                        fields = record['fields']
                        status = fields['Color']
                        if status == 'No':
                                unit = '1'
                                currunit = 'F'
                        if status == 'Yes':
                                unit = '0'
                                currunit = 'C'
                        print('Current units: %s' % currunit)
        except Exception as e:
                print(f"An error occurred: {e}")
        client.publish(image_feedname,    
                bytes(str(unit), 'utf-8'), 
                qos=0)
        print('...Publishing current units to Adafruit')
        sleep(5)