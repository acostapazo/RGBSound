# Created by Ming Lian, David Chen, and Kiera Fair
# SEED Class of 2018
# Last updated: 4/7/18
# The following code is under MIT license.

import smbus
import time
import pygame, pygame.sndarray
import numpy

sample_rate = 44100
bits=16
pygame.mixer.pre_init(sample_rate, -bits, 2)
pygame.mixer.init()
sound=None
def play_for(sample_wave, ms):
    """Play the given NumPy array, as a sound, for ms milliseconds."""
    global sound
    try:
        sound.stop()
    except:
        pass
    sound = pygame.sndarray.make_sound(sample_wave)
    sound.play(-1)
    pygame.time.delay(ms)
    #sound.stop()

def sine_wave(hz, peak, n_samples=sample_rate):
    """Compute N samples of a sine wave with given frequency and peak amplitude.
       Defaults to one second.
    """
    length = sample_rate / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = peak * numpy.sin(xvalues)
    left = numpy.resize(onecycle, (n_samples,)).astype(numpy.int16)
    right = left
    lr=numpy.resize(numpy.concatenate((left, right), axis=0), (n_samples, 2))
    numpy.transpose(lr)
    return lr

bus = smbus.SMBus(1)
# I2C address 0x29
# Register 0x12 has device ver. 
# Register addresses must be OR'ed with 0x80
bus.write_byte(0x29,0x80|0x12)
ver = bus.read_byte(0x29)
# version # should be 0x44

colors = {"F4": [0.567, 0.271,0.245,349.2], "F#": [0.682, 0.208, 0.221, 370],
          "G4": [0.759, 0.171, 0.19, 392], "G#": [0.709, 0.209, 0.184, 415.3],
          "A4": [0.551, 0.296,  0.224, 440], "A#": [0.435,0.394, 0.215,466.2], 
          "B4": [0.365, 0.432, 0.240, 493.9], "C5": [0.369, 0.461, 0.2, 523.2],
          "C#": [0.176, 0.433, 0.440, 554.4], "D5": [0.146, 0.396, 0.513, 587.3],
          "D#": [0.136, 0.380, 0.549, 622.2], "E5": [0.261, 0.353, 0.449, 659.3],
          "F5": [0.353,  0.319, 0.398, 698.5]}

def colorReader():
  data = bus.read_i2c_block_data(0x29, 0)
  clear = clear = data[1] << 8 | data[0]
  red = data[3] << 8 | data[2]
  green = data[5] << 8 | data[4]
  blue = data[7] << 8 | data[6]
  crgb = "C: %s \nR: %s \nG: %s \nB: %s\n" % (clear, red, green, blue)
  return [red/clear, green/clear, blue/clear]

def colorToFrequency(r, g, b):
  distance = (colors["F4"][0]-r)**2 + (colors["F4"][1]-g)**2 + (colors["F4"][2]-b)**2
  frequency = 440
  closestNote= "A4"
  for key in colors:
    temp = (colors[key][0]-r)**2 + (colors[key][1]-g)**2 + (colors[key][2]-b)**2
    if distance > temp:
      distance = temp
      frequency = colors[key][3]
      closestNote=key
  print(frequency)
  print(closestNote)
  return frequency

def notePlayer(color):
  frequency = colorToFrequency(color[0], color[1], color[2])
  print(frequency)
  play_for(sine_wave(frequency, 4096), 100)
  #time.sleep(2)
  
if ver == 0x44:
 print("Device found\n")
 bus.write_byte(0x29, 0x80|0x00) # 0x00 = ENABLE register
 bus.write_byte(0x29, 0x01|0x02) # 0x01 = Power on, 0x02 RGB sensors enabled
 bus.write_byte(0x29, 0x80|0x14) # Reading results start register 14, LSB then MSB

else: 
 print("Device not found\n")

try: 
    while True:
        notePlayer(colorReader())
        print(colorReader())
except KeyboardInterrupt:
    try:
        sound.stop()
    except:
        pass
finally:
    print("Thank you for playing!")
