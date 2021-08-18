#!/usr/bin/env python3
# 
# AUTHOR: PAPUUTEK

from selenium import webdriver
from pyvirtualdisplay import Display
import paho.mqtt.client as mqtt
import json
import argparse
argsparser = argparse.ArgumentParser()
argsparser.add_argument("-tm","--type_of_meter", help="Typ licznika: 1 dla jednokierunkowego, 2 dla dwukierunkowego",type=int,choices=[1,2],required=True)
argsparser.add_argument("-ms","--mqtt_server", help="Serwer MQTT",required=True)
argsparser.add_argument("-mu","--mqtt_username", help="Uzytkownik MQTT",required=False)
argsparser.add_argument("-mp","--mqtt_password", help="Haslo MQTT",required=False)
argsparser.add_argument("-mt","--mqtt_topic", help="Temat MQTT",required=True)
argsparser.add_argument("-eu","--energa_username", help="Login Energa S.A ",required=True)
argsparser.add_argument("-ep","--energa_password", help="Haslo Energa S.A ",required=True)
args = argsparser.parse_args()

#ENERGA
energa_username = args.energa_username
energa_password = args.energa_password

#MQTT
serverUrl   = args.mqtt_server
clientId    = "energascript"
username    = args.mqtt_username
password    = args.mqtt_password
topic       = args.mqtt_topic
print("Wait...")
display = Display(visible=0, size=(800, 600))
display.start()
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
driver = webdriver.Chrome('/usr/bin/chromedriver', options=options)
driver.get('https://mojlicznik.energa-operator.pl/dp/UserLogin.do')
driver.find_element_by_id("loginRadio").click()
driver.find_element_by_id("j_username").send_keys(energa_username)
driver.find_element_by_id ("j_password").send_keys(energa_password)
driver.find_element_by_name("loginNow").click()
try:
    element_used = driver.find_element_by_id("right").find_elements_by_tag_name("tr")[0].find_element_by_class_name("last").text
except:
    print("PROBLEM Z POBRANIEM DANYCH Z ENERGA S.A - SPRAWDZ DANE LOGOWANIA")
    driver.quit()
    display.stop()
    exit()
if args.type_of_meter ==2: element_produced = driver.find_element_by_id("right").find_elements_by_tag_name("tr")[2].find_element_by_class_name("last").text
driver.quit()
display.stop()
element_used = element_used.replace(" ","")
element_used = element_used.replace(",",".")
val_used = float(element_used)
if args.type_of_meter ==2:
    element_produced = element_produced.replace(" ","")
    element_produced = element_produced.replace(",",".")
    val_produced = float(element_produced)
    mqtt_msg = json.dumps({"used": val_used, "produced": val_produced})
else:
    mqtt_msg = json.dumps({"used": val_used})

print(mqtt_msg)

def on_connect(client, userdata, flags, rc):
    client.publish(topic, mqtt_msg)
    client.disconnect()
client = mqtt.Client(clientId)
if(username != None): client.username_pw_set(username, password)
try:
    client.connect(serverUrl)
except:
    print("BŁĄD MQTT - Sprawdz dane MQTT")
    exit()
client.on_connect = on_connect
client.loop_forever()




