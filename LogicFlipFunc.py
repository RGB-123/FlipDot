import serial
import fcntl
import struct
import time
import numpy as np
import sys
import random
 
ser = serial.Serial(
    port='/dev/ttyO4', 
    baudrate=38400, 
    timeout=1,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)
 
# Standard Linux RS485 ioctl:
TIOCSRS485 = 0x542F
 
# define serial_rs485 struct per Michael Musset's patch that adds gpio RE/DE 
# control:
# (https:#github.com/RobertCNelson/bb-kernel/blob/am33x-v3.8/patches/fixes/0007-omap-RS485-support-by-Michael-Musset.patch#L30)
SER_RS485_ENABLED         = (1 << 0)
SER_RS485_RTS_ON_SEND     = (1 << 1)
SER_RS485_RTS_AFTER_SEND  = (1 << 2)
SER_RS485_RTS_BEFORE_SEND = (1 << 3)
SER_RS485_USE_GPIO        = (1 << 5)
 
# Enable RS485 mode using a GPIO pin to control RE/DE: 
RS485_FLAGS = SER_RS485_ENABLED | SER_RS485_USE_GPIO 
# With this configuration the GPIO pin will be high when transmitting and low
# when not
 
# If SER_RS485_RTS_ON_SEND and SER_RS485_RTS_AFTER_SEND flags are included the
# RE/DE signal will be inverted, i.e. low while transmitting
 
# The GPIO pin to use, using the Kernel numbering: 
RS485_RTS_GPIO_PIN = 48 # GPIO1_16 -> GPIO(1)_(16) = (1)*32+(16) = 48
 
# Pack the config into 8 consecutive unsigned 32-bit values:
# (per  struct serial_rs485 in patched serial.h)
serial_rs485 = struct.pack('IIIIIIII', 
                           RS485_FLAGS,        # config flags
                           0,                  # delay in us before send
                           0,                  # delay in us after send
                           RS485_RTS_GPIO_PIN, # the pin number used for DE/RE
                           0, 0, 0, 0          # padding - space for more values 
                           )
 
# Apply the ioctl to the open ttyO4 file descriptor:
fd=ser.fileno()
fcntl.ioctl(fd, TIOCSRS485, serial_rs485)

#*******************************************************************************
def sendPack (cmd, addr, data):
    # Packet Information 
    # 0x80 beginning 
    #-----
    # 0x81 - 112 bytes / no refresh / C+3E
    # 0x82 - refresh
    # 0x83 - 28 bytes of data / refresh / 2C
    # 0x84 - 28 bytes of data / no refresh / 2C
    # 0x85 - 56 bytes of data / refresh / C+E
    # 0x86 - 56 bytes of data / no refresh / C+E
    ByteHeader  = 0x80     
    ByteEnd     = 0x8F    

    ser.write(chr(ByteHeader))
    ser.write(chr(cmd))
    ser.write(chr(addr))
    for n in range (0,panelCols):
        ser.write(chr(data[n]))
    
    ser.write(chr(ByteEnd))

#*******************************************************************************
# Main 
#*******************************************************************************


panelCols   = 28
panelRows   = 7
ByteCommand = 0x83
ByteAddress = 0x00
ByteDataWht    = [255  ] * panelCols
ByteDataBlk    = [0] * panelCols

#for idx in range (0,10):

while 1:
    sendPack(ByteCommand,ByteAddress,ByteDataWht)
    time.sleep(random.random())
    sendPack(ByteCommand,ByteAddress,ByteDataBlk)
    time.sleep(random.random())

ser.close()
