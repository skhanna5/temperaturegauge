import network
from machine import Pin, ADC
from time import sleep
import ubinascii
import urequests as requests
from math import log
import controller as gamepad
import simple as mqtt
import uasyncio as asyncio

def starting():
    #initialize all values needed. connect to wifi and Adafruit.
    print('Booting Up')
    print('-------------------------------------------------------------------------------------------')
    sleep(1)
    global client, tempF_feedname, tempC_feedname, image_feedname, airtabletoken, baseid, tablename, url, headers
    USERNAME = b'' #omitted
    AIOKEY = b'' #omitted
    airtabletoken = '' #omitted
    baseid = '' #omitted
    tablename = '' #omitted
    ssid = 'Tufts_Wireless'
    password = ''
    adaurl = b'io.adafruit.com' 
    tempF_key =  b'' #omitted
    tempC_key = b'' #omitted
    image_key = b'' #omitted
    mqtt_client_id = b'shiv'
    client = mqtt.MQTTClient(client_id=mqtt_client_id, server=adaurl, user=USERNAME, password=AIOKEY, ssl=False)
    tempF_feedname = bytes('{:s}/feeds/{:s}'.format(USERNAME, tempF_key), 'utf-8')
    tempC_feedname = bytes('{:s}/feeds/{:s}'.format(USERNAME, tempC_key), 'utf-8')
    image_feedname = bytes('{:s}/feeds/{:s}'.format(USERNAME, image_key), 'utf-8')
    url = "https://api.airtable.com/v0/%s/%s" % (baseid, tablename)
    headers = {"Authorization": f"Bearer {airtabletoken}",}
    station = network.WLAN(network.STA_IF)
    station.active(True)
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    #connect pico to wifi
    print('Testing Wifi...')
    sleep(1)
    station.connect(ssid, password)
    while station.isconnected() == False:
        sleep(1)
    print('Wifi connection successful!')
    #print(station.ifconfig())
    sleep(1)
    print('Next, test Adafruit MQTT...')
    sleep(1)
    #connect pico to adafruit
    try:            
        client.connect()
        print('Adafruit connection successful!')
        sleep(1)
    except Exception as e:
        print('Could not connect to MQTT server {}{}'.format(type(e).__name__, e))
    print('-------------------------------------------------------------------------------------------')
#----------------------------------------------------------------------------------------------------------------------------------#
async def publish():
    #send data to Adafruit
    publishingperiod = 5
    while True:
        if unit == '1':
            client.publish(tempF_feedname,    
                        bytes(str(ts_F), 'utf-8'), 
                        qos=0)  
            print('...Publishing %s to Adafruit' % ts_F)
        if unit == '0':
            client.publish(tempC_feedname,    
                        bytes(str(ts_C), 'utf-8'), 
                        qos=0)
            print('...Publishing %s to Adafruit' % ts_C)
        client.publish(image_feedname,    
                    bytes(str(unit), 'utf-8'), 
                    qos=0)
        await asyncio.sleep(publishingperiod)
async def read():
    #read data from Airtable
    delay =  0.1
    index = 0
    led_in = 5
    led_out = 0
    global unit, currunit
    unit = ''
    while True:
        for i in leds:
            i.value(1)
        for i in border:
            i.value(1)
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
        await asyncio.sleep(15)
#----------------------------------------------------------------------------------------------------------------------------------#       
async def physical():
    #get readings from thermistor and control all LEDS. also create coroutines
    global ts_F, ts_C, leds, border
    gamepad.digital_setup()
    leds = [Pin(0,Pin.OUT), Pin(1,Pin.OUT), Pin(2,Pin.OUT), 
            Pin(3,Pin.OUT), Pin(4,Pin.OUT), Pin(5,Pin.OUT), 
            Pin(6,Pin.OUT), Pin(7,Pin.OUT), Pin(8,Pin.OUT), 
            Pin(9,Pin.OUT), Pin(10,Pin.OUT), Pin(11,Pin.OUT)]
    border = [Pin(16,Pin.OUT), Pin(17,Pin.OUT), Pin(18,Pin.OUT), Pin(19, Pin.OUT)]
    adc = ADC(27)
    flashtime = 0.01
    #Ro, To, beta were calibrated according to ambient temperature in Nolop
    Ro = 10000.0
    To = 24.5
    beta = 3975
    await asyncio.sleep(0.5)
    asyncio.create_task(read())
    asyncio.create_task(publish())
    while True:
        x, y, button = gamepad.read_everything()
        #math from online using a 10k resistor and thermistor, Steinhart-Hart
        #https://learn.adafruit.com/thermistor/circuitpython
        r = Ro / (65535 / float(adc.read_u16()) - 1)
        steinhart = log(r / Ro) / beta      # log(R/Ro) / beta
        steinhart += 1.0 / (To + 273.15)    # log(R/Ro) / beta + 1/To
        ts_C = (1.0 / steinhart) - 273.15   # Invert, convert to C
        ts_F = ts_C*(9/5) + 32
        #print('%5.1f C or %F F' % (ts_C, ts_F))
        await asyncio.sleep(flashtime)
        #physical display toggles
        if ts_F < 67:
            leds[0].toggle()
            for i in leds[1:]:
                i.value(0)
        if 67 < ts_F < 68:
            leds[1].toggle()
            leds[0].value(0)
            for i in leds[2:]:
                i.value(0)
        if 68 < ts_F < 70:
            leds[2].toggle()
            leds[0].value(0)
            for i in leds[2:]:
                i.value(0)
        if 70 < ts_F < 72:
            leds[3].toggle()
            for i in leds[0:2]:
                i.value(0) 
            for i in leds[4:]:
                i.value(0)
        if 72 < ts_F < 73:
            leds[4].toggle()
            for i in leds[0:3]:
                i.value(0)
            for i in leds[5:]:
                i.value(0)
        if 73 < ts_F < 76:
            leds[5].toggle()
            for i in leds[0:4]:
                i.value(0)
            for i in leds[6:]:
                i.value(0)
        if 76 < ts_F < 78:
            leds[6].toggle()
            for i in leds[0:5]:
                i.value(0)
            for i in leds[7:]:
                i.value(0)
        if 78 < ts_F < 80:
            leds[7].toggle()
            for i in leds[0:6]:
                i.value(0)
            for i in leds[8:]:
                i.value(0)
        if 80 < ts_F < 81:
            leds[8].toggle()
            for i in leds[0:7]:
                i.value(0)
            for i in leds[9:]:
                i.value(0)
        if 81 < ts_F < 83:
            leds[9].toggle()
            for i in leds[0:8]:
                i.value(0)
            for i in leds[10:]:
                i.value(0)
        if 83 < ts_F < 85:
            leds[10].toggle()
            for i in leds[0:9]:
                i.value(0)
            for i in leds[11:]:
                i.value(0)
        if 85 < ts_F:
            leds[11].toggle()
            for i in leds[0:10]:
                i.value(0)
        if y > 1000 and currunit == "F":
            border[0].toggle()
            border[1].toggle()
        if y > 1000 and currunit == "C":
            border[2].toggle()
            border[3].toggle()
        # if currunit == 'F':
        #     for i in border:
        #             i.value(0)
        if y < 1000:
            for i in border:
                i.value(0)
#----------------------------------------------------------------------------------------------------------------------------------#
#running everything
try:
    starting()
    asyncio.run(physical())
except KeyboardInterrupt:
    print('-------------------------------------------------------------------------------------------')
    print("Quitting")
    #turning off the lights
    for i in leds:
        i.value(0)
    for i in border:
        i.value(0)
