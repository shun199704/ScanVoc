import paho.mqtt.client as mqtt
import smbus
import time

TopicServerIP = "localhost"
TocpicServerPort = 1883
TopicName = "Letter"

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "python_pub")
mqttc.connect(TopicServerIP,TocpicServerPort)

I2C_SLAVE_ADDRESS = 0x08  # I2C address of the Arduino

# Initialize the I2C bus
bus = smbus.SMBus(1)

def request_from_arduino():
    try:
        # Request 16 bytes from the Arduino
        data = bus.read_i2c_block_data(I2C_SLAVE_ADDRESS, 0, 16)
        if (data[0] == 0):
            return None    
        datatouse = chr(data[0])
        return datatouse
    except IOError as e:
        print(f"I/O Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

while True:
    data = request_from_arduino()
    if data:
        print(f"Received: {data}")
        mqttc.publish(TopicName,data)
    time.sleep(1)  # Delay to prevent continuous reading