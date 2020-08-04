# gqrx-hamlib - a gqrx to Hamlib interface to keep frequency
# between gqrx and a radio in sync when using gqrx as a panadaptor
# using Hamlib to control the radio
#
# The Hamlib daemon (rigctld) must be running, gqrx started with
# the 'Remote Control via TCP' button clicked and
# comms to the radio working otherwise an error will occur when
# starting this program. Ports used are the defaults for gqrx and Hamlib.
#
# Return codes from gqrx and Hamlib are printed to stderr
#
# This program is written in Python 3.8
# Python libraries required are:
#   - telnetlib
#   - sys
#   - getopt
#   - time
#   - xmlrpc.client
#
# To run it type the following on the command line in the directory where
# you have placed this file:
#   python3 ./gqrx-hamlib-fldigi2.py [-f]
#
# The -f option will cause the program to tune fldigi to the gqrx frequency.
#
# Copyright 2020 Philippe ARLOTTO arlotto at univ-tln.fr 
# Derived form original code by Simon Kennedy, G0FCU, g0fcu at g0fcu.com
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import telnetlib
import sys, getopt
import time
fldigi_option_set = 0

if len(sys.argv) > 0:
    try:
        opts, args = getopt.getopt(sys.argv, 'f',)
    except getopt.GetoptError:
        print('gqrx-hamlib.py [-f]')
        sys.exit(2)
    for index in range(len(args)):
        if args[index] == '-f':
           fldigi_option_set = 1

if fldigi_option_set == 1:
   import xmlrpc.client

HOST = "localhost"
RIG_PORT = 4532
GQRX_PORT = 7356
FLDIGI_PORT = 7362

MESSAGE = ""

timeout=4

# mode conversion between GQRX and my TS590 :

modeRigtoGQRX = {'AM':'AM', 'CW':'CWU', 'CWR':'CWL',\
                   'USB':'USB','PKTUSB':'USB','LSB':'LSB','PKTLSB':'LSB',\
                   'FM':'FM','PKTFM':'FM', 'RTTY':'USB','RTTYR':'LSB'}

modeGQRXtoRig = {'AM':'AM', 'CWU':'CW', 'CWL':'CWR',\
                   'USB':'USB','LSB':'LSB','FM':'FM'}

rig_freq = 0
gqrx_freq = 0
old_rig_freq = 0
old_gqrx_freq = 0
old_rig_mode = None
old_gqrx_mode = None

tnRig = telnetlib.Telnet(HOST,RIG_PORT)
tnGqrx = telnetlib.Telnet(HOST,GQRX_PORT)

def getFreq(tn) :
     tn.write(b'f\n')
     data=tn.read_until( b'\n',timeout)
     return data
 
def setFreq(tn, freq) :
    build_msg = 'F ' + str(freq) + '\n'
    MESSAGE = bytes(build_msg, 'utf-8')
    tn.write(MESSAGE)
    data=tn.read_until( b'\n', timeout )
    return data

def getMode(tn):
    tn.write(b'm\n')
    mode=tn.read_until( b'\n', timeout )
    width = tn.read_until( b'\n', timeout )
    return mode,width

def setMode(tn, mode) :
    build_msg = 'M ' + str(mode) + ' 0\n'
    MESSAGE = bytes(build_msg, 'utf-8')
    tn.write(MESSAGE)
    data=tn.read_until( b'\n', timeout)
    return data

if fldigi_option_set == 1:
  server = xmlrpc.client.ServerProxy('http://{}:{}/'.format(HOST, FLDIGI_PORT))

n=1
while 1 :
    time.sleep(0.2)
    # sync frequencies
    rig_freq = getFreq(tnRig)
    print('rig_freq =',rig_freq, end=' ')
    if rig_freq != old_rig_freq:
        # set gqrx to Hamlib frequency
        try :
             rc = setFreq(tnGqrx, float(rig_freq))
             print('Return Code from GQRX: {0}'.format(rc))
             old_rig_freq = rig_freq
             old_gqrx_freq = rig_freq
        except ValueError:
             print('ValueError :',rig_freq)
        
    gqrx_freq = getFreq(tnGqrx)
    print('gqrx_freq =',gqrx_freq)
    if gqrx_freq != old_gqrx_freq:
        # set Hamlib to gqrx frequency
        try :
                rc = setFreq(tnRig, float(gqrx_freq))
                print('Return Code from Hamlib: {0}'.format(rc))
                # Set fldigi to gqrx frequency
                if fldigi_option_set == 1:
                    server.main.set_frequency(float(gqrx_freq))
                old_gqrx_freq = gqrx_freq
                old_rig_freq = gqrx_freq
        except ValueError:
             print('ValueError :',gqrx_freq)
    # sync modes 
    n+=1
    if n>5 :
        n=0
        gqrx_mode,gqrx_width = getMode(tnGqrx)
        rig_mode,rig_width = getMode(tnRig)
        rig_mode = rig_mode.decode('ASCII').strip()
        gqrx_mode= gqrx_mode.decode('ASCII').strip()
        print('RIG mode :',rig_mode,'GQRX mode :', gqrx_mode)
        # mode rig -> gqrx
        if rig_mode != old_rig_mode :
            try :
                if modeRigtoGQRX[rig_mode] != gqrx_mode :
                    setMode(tnGqrx,modeRigtoGQRX[rig_mode])
                    print("RIG Mode --> GQRX mode")
                    gqrx_mode=old_gqrx_mode = modeRigtoGQRX[rig_mode]
            except KeyError:
                print('KeyError :',rig_mode)
            old_rig_mode = rig_mode


#        # mode gqrx -> rig
        if gqrx_mode != old_gqrx_mode :
            if gqrx_mode in modeGQRXtoRig :
                 setMode(tnRig,modeGQRXtoRig[gqrx_mode])
                 print("GQRX Mode --> RIG mode")
                 old_gqrx_mode = gqrx_mode
            old_rig_mode = rig_mode

