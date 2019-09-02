# First iteration:  just send the 64 samples with MQTT

import pyaudio
import struct

import paho.mqtt.client as mqtt
import time

CHUNK = 1024 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
DEV_INDEX = 0

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input_device_index=DEV_INDEX,input=True,output=False,frames_per_buffer=CHUNK)
 
#sample_jump = CHUNK/64
sample_jump = 2
sample_scale = 100

total_rows = 32
total_columns = 32
sample_bias = total_rows / 2 

def on_message(client, userdata, message):
  global total_rows
  global total_columns
  global sample_bias

  if message.topic == "display/columns":
    total_columns = int(message.payload)
    print("setting total columns to "+str(total_columns))
  elif message.topic == "display/rows":
    total_rows = int(message.payload)
    sample_bias = total_rows / 2
    print("setting total rows to "+str(total_rows))
  else:
    print("Unknown message on display topic:"+message.topic)
    print("Payload: "+message.payload)

broker_address="10.0.0.17"
client = mqtt.Client("Microphone")
client.on_message=on_message
client.connect(broker_address)
client.loop_start()
client.subscribe("display/#")

try:
  print("Hit ctl-c to exit")
  while (True):
    data = stream.read(CHUNK,exception_on_overflow = False)
    data_int = struct.unpack(str(CHUNK) +'h', data)  
    
    scaled_data = []
 
    for point in range(0,total_columns-1):
       point_index = point*sample_jump
       scaled_point = sample_bias + data_int[point_index]/sample_scale
       if scaled_point < 0:
          scaled_point = 0
       if scaled_point > 255:
          scaled_point = 255 
       scaled_data.append(scaled_point)

    packed_data = bytearray(scaled_data)
    client.publish("audio/time_samples",packed_data) 
    #print("write done")
    time.sleep(.1)
    
except KeyboardInterrupt:
  exit(0)

