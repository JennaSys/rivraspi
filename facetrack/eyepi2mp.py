import pigpio  # http://abyz.co.uk/rpi/pigpio/python.html
import time

class EyePi():
    
    def __init__(self):
        
        self.pPanL = 18
        self.pTiltL = 26
        self.pPanR = 23
        self.pTiltR = 24
        self.pPanicBtn = 17

        self.pan_minL = 1200
        self.pan_maxL = 2300
        self.tilt_minL = 800
        self.tilt_maxL = 2100
        self.pan_minR = 800
        self.pan_maxR = 1700
        self.tilt_minR = 700
        self.tilt_maxR = 2300

        #pan_center = ((pan_max - pan_min) / 2) + pan_min
        #tilt_center = ((tilt_max - tilt_min) / 2) + tilt_min
        self.pan_centerL = 1800
        self.tilt_centerL = 1550
        self.pan_centerR = 1260
        self.tilt_centerR = 1600
        
        self._inPanic = False
        
        self.pi = None
        self._cb_panic = None
        

    def inPanic(self):
        return self._inPanic

    def cb_panic(self, port, status, tick):
        print "PANIC!!! ({} {} {})".format(port, status, tick)
        self._inPanic = True
        self.cross_eyed()
        time.sleep(4)
        self.look_forward()
        print "Don't Panic"
        self._inPanic = False
        
        
    def start(self):
        if self.pi is None:
            self.pi = pigpio.pi()

        self.pi.set_mode(self.pPanL, pigpio.OUTPUT)
        self.pi.set_mode(self.pTiltL, pigpio.OUTPUT)
        self.pi.set_mode(self.pPanR, pigpio.OUTPUT)
        self.pi.set_mode(self.pTiltR, pigpio.OUTPUT)
        
        #same as look_forward() without clearing first
        self.pi.set_servo_pulsewidth(self.pPanL, self.pan_centerL)
        self.pi.set_servo_pulsewidth(self.pTiltL, self.tilt_centerL)
        self.pi.set_servo_pulsewidth(self.pPanR, self.pan_centerR)
        self.pi.set_servo_pulsewidth(self.pTiltR, self.tilt_centerR)
        
        self.pi.set_mode(self.pPanicBtn, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pPanicBtn, pigpio.PUD_UP)
        self._cb_panic = self.pi.callback(self.pPanicBtn, pigpio.FALLING_EDGE, self.cb_panic)

    def stop(self):
        self._cb_panic.cancel()
        self.pi.set_servo_pulsewidth(self.pPanL, 0)
        self.pi.set_servo_pulsewidth(self.pTiltL, 0)
        self.pi.set_servo_pulsewidth(self.pPanR, 0)
        self.pi.set_servo_pulsewidth(self.pTiltR, 0)
        self.pi.stop()
        
    def __set_position(self, port, pulse_value):
        self.pi.set_servo_pulsewidth(port, pulse_value)

    def set_pan(self, pan_pct):
        if pan_pct < 0:  #Pan Left
            if pan_pct < -100:
                pan_pct = -100
            panL = int(((self.pan_centerL - self.pan_minL) * pan_pct) / 100) + self.pan_centerL
            panR = int(((self.pan_centerR - self.pan_minR) * pan_pct) / 100) + self.pan_centerR
        else:  #Pan Right
            if pan_pct > 100:
                pan_pct = 100
            panL = int(((self.pan_maxL - self.pan_centerL) * pan_pct) / 100) + self.pan_centerL
            panR = int(((self.pan_maxR - self.pan_centerR) * pan_pct) / 100) + self.pan_centerR
        
        print 'PAN=L:{0} ({1}/{2}/{3})  R:{4} ({5}/{6}/{7})'.format(panL, self.pan_minL, self.pan_centerL, self.pan_maxL, panR, self.pan_minR, self.pan_centerR, self.pan_maxR)

        if not self.inPanic:
            self.pi.set_servo_pulsewidth(self.pPanL, panL)
            self.pi.set_servo_pulsewidth(self.pPanR, panR)
        
        

    def set_tilt(self, tilt_pct):
        if tilt_pct < 0:  #Tilt Down
            if tilt_pct < -100:
                tilt_pct = -100
            tiltL = int(((self.tilt_centerL - self.tilt_minL) * tilt_pct) / 100) + self.tilt_centerL
            tiltR = self.tilt_centerR - int(((self.tilt_maxR - self.tilt_centerR) * tilt_pct) / 100)
        else:  #Tilt Up
            if tilt_pct > 100:
                tilt_pct = 100
            tiltL = int(((self.tilt_maxL - self.tilt_centerL) * tilt_pct) / 100) + self.tilt_centerL
            tiltR = self.tilt_centerR - int(((self.tilt_centerR - self.tilt_minR) * tilt_pct) / 100)
            
        
        print 'TILT=L:{0} ({1}/{2}/{3})  R:{4} ({5}/{6}/{7})'.format(tiltL, self.tilt_minL, self.tilt_centerL, self.tilt_maxL, tiltR, self.tilt_minR, self.tilt_centerR, self.tilt_maxR)
        
        if not self.inPanic:
            self.pi.set_servo_pulsewidth(self.pTiltL, tiltL)
            self.pi.set_servo_pulsewidth(self.pTiltR, tiltR)
        


    def look_forward(self):
        self.__set_position(self.pPanL, self.pan_centerL)
        self.__set_position(self.pTiltL, self.tilt_centerL)
        self.__set_position(self.pPanR, self.pan_centerR)
        self.__set_position(self.pTiltR, self.tilt_centerR)

    def cross_eyed(self):
        self.__set_position(self.pPanL, self.pan_minL)
        self.__set_position(self.pPanR, self.pan_maxR)
        self.__set_position(self.pTiltL, self.tilt_centerL)
        self.__set_position(self.pTiltR, self.tilt_centerR)


    def look_left(self):
        self.__set_position(self.pPanL, self.pan_minL)
        self.__set_position(self.pPanR, self.pan_minR)

    def look_right(self):
        self.__set_position(self.pPanL, self.pan_maxL)
        self.__set_position(self.pPanR, self.pan_maxR)

    def look_up(self):
        self.__set_position(self.pTiltL, self.tilt_minL)
        self.__set_position(self.pTiltR, self.tilt_maxR)

    def look_down(self):
        self.__set_position(self.pTiltL, self.tilt_maxL)
        self.__set_position(self.pTiltR, self.tilt_minR)
        
    def __call__(self, fname, *args, **kwds):
        __callable = {"set_pan":self.set_pan, "set_tilt":self.set_tilt, "inPanic":self.inPanic}
        return __callable[fname](*args, **kwds)
        
    
    
if __name__ == '__main__':
    eyes = EyePi()
    eyes.start()
    eyes.cross_eyed()
    time.sleep(3)
    eyes.look_forward()
    time.sleep(2)
    eyes.stop()

