import sys
import time
import serial 
from Adafruit_IO import MQTTClient

# CONFIGURACIÓN
ADAFRUIT_IO_USERNAME = "nav22250"
ADAFRUIT_IO_KEY      = "aio_czUp75QPmXwwhUwop2rsgCxOH9x2"

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
client.connect()

# Feeds
feedPot0 = 'pot0'
feedPot1 = 'pot1'
feedPot2 = 'pot2'
feedPot3 = 'pot3'

# Valores actuales
Pot0 = "000"
Pot1 = "000"
Pot2 = "000"
Pot3 = "000"

# Valores desde la nube
fPot0 = "000"
fPot1 = "000"
fPot2 = "000"
fPot3 = "000"

# Inicializar cliente MQTT
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

def test(value):
    global Pot0, Pot1, Pot2, Pot3
    try:
        value = int(value)
    except ValueError:
        print("Valor inválido:", value)
        return

    if value == 0:
        print("Pot0 =", Pot0)
        client.publish(feedPot0, Pot0)
    elif value == 1:
        print("Pot1 =", Pot1)
        client.publish(feedPot1, Pot1)
    elif value == 2:
        print("Pot2 =", Pot2)
        client.publish(feedPot2, Pot2)
    elif value == 3:
        print("Pot3 =", Pot3)
        client.publish(feedPot3, Pot3)
    else:
        print("Cambio inválido:", value)

def prueba(feed, payload):
    global fPot0, fPot1, fPot2, fPot3
    formatted = payload.zfill(3)

    if feed == 'pot0':
        fPot0 = formatted
        print("Pot0 =", fPot0)
    elif feed == 'pot1':
        fPot1 = formatted
        print("Pot1 =", fPot1)
    elif feed == 'pot2':
        fPot2 = formatted
        print("Pot2 =", fPot2)
    elif feed == 'pot3':
        fPot3 = formatted
        print("Pot3 =", fPot3)
    else:
        print("Feed desconocido:", feed)

def connected(client):
    client.subscribe(feedPot0)
    client.subscribe(feedPot1)
    client.subscribe(feedPot2)
    client.subscribe(feedPot3)
    print("Conectado y suscrito a los feeds.")

def disconnected(client):
    print("Desconectado de Adafruit IO")
    sys.exit(1)

def message(client, feed_id, payload):
    global serialArduino, fPot0, fPot1, fPot2, fPot3
    print('Feed {} recibió: {}'.format(feed_id, payload))
    prueba(feed_id, payload)
    
    bus = fPot0 + fPot1 + fPot2 + fPot3
    print("Datos a enviar por serial:", bus)

    if serialArduino and serialArduino.is_open:
        serialArduino.write(bus.encode('ascii'))

# CONFIGURAR MQTT
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

try:
    client.connect()
    client.loop_background()

    serialArduino = serial.Serial("COM5", 9600, timeout=0.05)
    time.sleep(1)

    while True:
        cad = serialArduino.readline().decode('ascii').strip()

        if len(cad) == 15:
            Pot0 = cad[0:3]
            Pot1 = cad[3:6]
            Pot2 = cad[6:9]
            Pot3 = cad[9:12]
            cambio = cad[12]

            print("Pot0 =", Pot0)
            print("Pot1 =", Pot1)
            print("Pot2 =", Pot2)
            print("Pot3 =", Pot3)

            test(cambio)

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Terminando programa...")
    if serialArduino and serialArduino.is_open:
        serialArduino.close()
    sys.exit(0)
