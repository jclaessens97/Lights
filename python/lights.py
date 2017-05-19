import webiopi
import datetime
from datetime import timedelta
from time import sleep
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

GPIO = webiopi.GPIO
LIGHTS = [19, 13, 6, 5, 22, 27, 17, 4,
          18, 23, 24, 25, 12, 16, 20, 21]

HOUR_ON = datetime.datetime(2017, 1, 1, 0, 0, 0)
HOUR_OFF = datetime.datetime(2017, 1, 1, 0, 0, 0)
SEQUENCE = ''

ACTIVE = False
RUNNING = False
TOGGLED = False

def readConfig():
    try: 
        root_dir = os.path.join(os.path.dirname(__file__), '')
        conf = open(root_dir + '/config', 'r')
        lines = conf.read().splitlines()
        conf.close()

        return lines
    except IOError:
        print("ERROR: configfile niet gevonden!")
        exit(-1)

def parseConfig():
    lines = readConfig()
    config = {}

    hour_on = lines[1]    
    hour_off = lines[3]    
    def_seq = lines[5]

    setTime(hour_on, hour_off)
    setCurrentSequence(def_seq)

def readSequence():
    try: 
        root_dir = os.path.join(os.path.dirname(__file__), '..')
        seq = open(root_dir + '/sequenties/' + SEQUENCE, 'r')
        lines = seq.read().splitlines()
        seq.close()

        return lines
    except IOError:
        print("ERROR: sequentiefile niet gevonden!")
        return []

def parseSequence():
    lines = readSequence()

    if (len(lines) == 0):
        return

    commands = {}

    try:

        for i in range(0, len(lines)):
            commands[i] = lines[i].split(',')

            commands[i][0] = int(commands[i][0])

            if (checkIfInt(commands[i][1])):
                commands[i][1] = int(commands[i][1])
            else:
                if (commands[i][1].strip() == "False"):
                    commands[i][1] = False
                else:
                    commands[i][1] = True

            commands[i][2] = int(commands[i][2]) / 1000

        return commands
    
    except ValueError:
        print('ERROR: fout in sequentiefile!')
        return {}

def timeCheck():
    now = datetime.datetime.now()

    if ((now >= HOUR_ON) and (now <= HOUR_OFF)):
        return True
    else:
        return False

def infiniteTimeCheck():
    if (HOUR_ON.hour == 0 and HOUR_ON.minute == 0):

        if (HOUR_ON == HOUR_OFF):
            return True
        else:
            return False
    else:
        return False  

def setup():
    parseConfig()
    global HOUR_OFF

    if (HOUR_OFF < HOUR_ON):
        HOUR_OFF = HOUR_OFF + timedelta(days=1)

    global ACTIVE
    ACTIVE = True

    global TOGGLED
    TOGGLED = False
    
    for light in LIGHTS:
        GPIO.setFunction(light, GPIO.OUT)
        GPIO.digitalWrite(light, GPIO.LOW)

def loop():
    global RUNNING

    commands = parseSequence()

    if (commands == None or len(commands) == 0):
        return
    
    index = 0
    
    if ((ACTIVE == True) and (timeCheck() == True)):
        RUNNING = True
    else:
        RUNNING = False

    while (RUNNING):
        if (index == len(commands)):
            index = 0
    
        lightIndex = commands[index][0]
        lightVal = None
        repeat = 0

        if (isinstance(commands[index][1], bool)):
            lightVal = commands[index][1]
        else:
            repeat = commands[index][1]
            
        delay = commands[index][2]
        flashing = False

        if (lightIndex > 10):

            lightNr = LIGHTS[lightIndex - 3]
        elif (lightIndex >= 1):

            lightNr = LIGHTS[lightIndex - 1]
        elif (lightIndex == 0):
            flashing = True           

        if (lightVal == True and not flashing):
            GPIO.digitalWrite(lightNr, GPIO.HIGH)
        elif (lightVal == False and not flashing):
            GPIO.digitalWrite(lightNr, GPIO.LOW)
        else:
            flashAllLights(repeat, delay)
      
        index += 1

        if (flashing):
            continue
        else:
            webiopi.sleep(delay)

        if (not infiniteTimeCheck()):
            if (timeCheck() == False):
                destroy()
        
        if (ACTIVE == False):
            destroy()        
    
    webiopi.sleep(1)


def destroy():
    global ACTIVE
    ACTIVE = False
    global RUNNING 
    RUNNING = False
    global TOGGLED
    TOGGLED = False

    for light in LIGHTS:
        if (GPIO.digitalRead(light) == GPIO.HIGH):
            GPIO.digitalWrite(light, GPIO.LOW)

def flashAllLights(repeat, delay):
    for i in range(0, repeat):
        for light in LIGHTS:
                GPIO.digitalWrite(light, GPIO.HIGH)

        webiopi.sleep(delay)

        for light in LIGHTS:
            GPIO.digitalWrite(light, GPIO.LOW)

        webiopi.sleep(1)

def checkIfInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

@webiopi.macro
def getTime():
    return "%s;%s" % (HOUR_ON.strftime("%H:%M"), HOUR_OFF.strftime("%H:%M"))

@webiopi.macro
def setTime(on, off):
    global HOUR_ON, HOUR_OFF

    time_on = on.split(':')
    time_off = off.split(':')

    now = datetime.datetime.now()

    HOUR_ON = datetime.datetime(now.year, now.month, now.day, int(time_on[0]), int(time_on[1]), 0)
    HOUR_OFF = datetime.datetime(now.year, now.month, now.day, int(time_off[0]), int(time_off[1]), 0)

    return getTime()

@webiopi.macro
def getCurrentSequence():
    global SEQUENCE
    return SEQUENCE

@webiopi.macro
def setCurrentSequence(seq):
    global SEQUENCE
    SEQUENCE = seq
    return getCurrentSequence()

@webiopi.macro
def readAllSequences():
    root_dir = os.path.join(os.path.dirname(__file__), '..')
    seqdir = root_dir + '/sequenties'

    sequences = ''

    for file in os.listdir(seqdir):
        if file.endswith('.txt'):
            sequences += file[:-4] + ';'
    
    return sequences

@webiopi.macro
def writeToConfig():
    try:
        lines = readConfig()

        hour_on_str = HOUR_ON.strftime('%H:%M:%S')
        hour_off_str = HOUR_OFF.strftime('%H:%M:%S')

        configString = ''
        configString += lines[0] + '\n'
        configString += str(hour_on_str) + '\n'
        configString += lines[2] + '\n'
        configString += str(hour_off_str) + '\n'
        configString += lines[4] + '\n'
        configString += str(SEQUENCE) + '\n'

        root_dir = os.path.join(os.path.dirname(__file__), '')        
        conf = open(root_dir + '/config', 'w')
        conf.write(configString)
        conf.close()
    except IOError:
        print("ERROR: kon niet naar configfile wegschrijven!")

@webiopi.macro
def toggleAllLights():
    global TOGGLED

    if (RUNNING == False):
        TOGGLED = not TOGGLED
        for light in LIGHTS:
            if (TOGGLED == True):
                GPIO.digitalWrite(light, GPIO.HIGH)
            else:
                GPIO.digitalWrite(light, GPIO.LOW)
    
@webiopi.macro
def stop():
    destroy()

@webiopi.macro
def restart():
    setup()    

@webiopi.macro
def getState():
    if (RUNNING and ACTIVE):
        return 'runningActive'
    elif (ACTIVE):
        return 'active'
    else:
        return 'stopped' 