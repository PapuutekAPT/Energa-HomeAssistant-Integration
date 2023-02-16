#!/usr/bin/env python3
#
# AUTHOR: PAPUUTEK

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
import paho.mqtt.client as mqtt
import json
import argparse
argsparser = argparse.ArgumentParser()
argsparser.add_argument("-tm", "--type_of_meter",
                        help="Typ licznika: 1 dla jednokierunkowego, 2 dla dwukierunkowego", type=int, choices=[1, 2], required=True)
argsparser.add_argument("-ms", "--mqtt_server",
                        help="Serwer MQTT", required=True)
argsparser.add_argument("-msp", "--mqtt_server_port",
                        help="Serwer MQTT port", type=int, default=1883, required=False)
argsparser.add_argument("-mu", "--mqtt_username",
                        help="Uzytkownik MQTT", required=False)
argsparser.add_argument("-mp", "--mqtt_password",
                        help="Haslo MQTT", required=False)
argsparser.add_argument("-mt", "--mqtt_topic",
                        help="Temat MQTT", required=True)
argsparser.add_argument("-eu", "--energa_username",
                        help="Login Energa S.A ", required=True)
argsparser.add_argument("-ep", "--energa_password",
                        help="Haslo Energa S.A ", required=True)
args = argsparser.parse_args()

# ENERGA
energa_username = args.energa_username
energa_password = args.energa_password

# MQTT
serverUrl = args.mqtt_server
serverPort = args.mqtt_server_port
clientId = "energascript"
username = args.mqtt_username
password = args.mqtt_password
topic = args.mqtt_topic

chrome = Service(r"/usr/bin/chromedriver")

print("Wait...")

display = Display(visible=0, size=(800, 600))
display.start()
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(service=chrome, options=options)
driver.get('https://mojlicznik.energa-operator.pl/dp/UserLogin.do')
driver.find_element(By.ID, "loginRadio").click()
driver.find_element(By.ID, "j_username").send_keys(energa_username)
driver.find_element(By.ID, "j_password").send_keys(energa_password)
driver.find_element(By.NAME, "loginNow").click()

logged_user = driver.find_element(By.ID, "topMenu").find_element(By.CLASS_NAME, "userLogged").text
print("LOGOWANIE")
if logged_user == energa_username:
    print("SUKCES")
    print("Zalogowany user: "+logged_user)
else:
    print("NIEPOWODZENIE,sprawdz dane logowania")

try:
    element_used = driver.find_element(By.ID, "right").find_element(By.TAG_NAME, "tr").find_element(By.CLASS_NAME, "last").text

except:

    print("PROBLEM Z POBRANIEM DANYCH Z ENERGA S.A - SPRAWDZ DANE LOGOWANIA")
    driver.quit()
    display.stop()
    exit()
if args.type_of_meter == 2:
    element_produced = driver.find_element(By.ID, "right").find_elements(By.TAG_NAME, "tr").find_element(By.CLASS_NAME,"last").text

driver.quit()
display.stop()

element_used = element_used.replace(" ", "")
element_used = element_used.replace(",", ".")

val_used = float(element_used)
if args.type_of_meter == 2:
    element_produced = element_produced.replace(" ", "")
    element_produced = element_produced.replace(",", ".")
    val_produced = float(element_produced)
    mqtt_msg = json.dumps({"used": val_used, "produced": val_produced})
else:
    mqtt_msg = json.dumps({"used": val_used})
print(mqtt_msg)

def on_connect(client, userdata, flags, rc):
    client.publish(topic, mqtt_msg)
    client.disconnect()


client = mqtt.Client(clientId)
if(username != None):
    client.username_pw_set(username, password)
try:
    client.connect(serverUrl, port=serverPort)
except:
    print("BŁĄD MQTT - Sprawdz dane MQTT")
    exit()

client.on_connect = on_connect
client.loop_forever()
