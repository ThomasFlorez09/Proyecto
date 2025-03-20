from machine import Pin, time_pulse_us
import time

class HCSR04:
    def _init_(self, trigger_pin, echo_pin, timeout_us=30000):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.timeout_us = timeout_us

    def distance_cm(self):
        self.trigger.off()
        time.sleep_us(2)
        self.trigger.on()
        time.sleep_us(10)
        self.trigger.off()

        tiempo_inicio = time.ticks_us()
        
        while self.echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), tiempo_inicio) > self.timeout_us:
                return -1.0
        
        tiempo_pulse_start = time.ticks_us()

        while self.echo.value() == 1:
            if time.ticks_diff(time.ticks_us(), tiempo_pulse_start) > self.timeout_us:
                return -1.0
        
        tiempo_pulse_end = time.ticks_us()
        duracion = time.ticks_diff(tiempo_pulse_end, tiempo_pulse_start)

        distancia = (duracion * 0.0343) / 2  

        if distancia <= 0 or distancia > 400:
            return -1.0

        return distancia