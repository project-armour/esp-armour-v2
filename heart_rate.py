import micropython
from machine import Pin, ADC, Timer
from time import ticks_ms, ticks_diff


class HeartRate:
    def __init__(self, pin, threshold=37120):
        self.pin = Pin(pin)
        self.adc = ADC(self.pin, atten=ADC.ATTN_11DB)

        self.default_threshold = threshold
        self.sample_interval_ms = 2
        self.rate = [0] * 10
        self.qs = False
        self.ibi = 750
        self.pulse = False
        self.sample_counter = 0
        self.last_beat_time = 0
        self.p = 65536 // 2
        self.t = 65536 // 2
        self.thresh = self.default_threshold
        self.amp = 65536 // 16
        self.first_beat = True
        self.second_beat = False
        self.running_total = -1
        self._isr_ref = self._isr
        self.reset()

        self.timer = Timer(0)
        self.timer.init(period = self.sample_interval_ms, mode=Timer.PERIODIC, callback=self._isr)

    def reset(self):
        for i in range(len(self.rate)):
            self.rate[i] = 0
        self.qs = False
        self.ibi = 750
        self.pulse = False
        self.sample_counter = 0
        self.last_beat_time = 0
        self.p = 65536 // 2
        self.t = 65536 // 2
        self.thresh = self.default_threshold
        self.amp = 65536 // 16
        self.first_beat = True
        self.second_beat = False
        self.running_total = -1

    def _schedule_isr(self, _):
        micropython.schedule(self._isr_ref, None)

    def _isr(self, _):
        signal = self.adc.read_uv() << 4
        self.sample_counter = ticks_ms()
        N = ticks_diff(self.sample_counter, self.last_beat_time)
        if signal == 49872000:
            return
        print('isr', N, signal)

        if signal < self.thresh and N > (self.ibi // 5) * 3:
            if signal < self.t: self.t = signal
        if signal > self.thresh and signal > self.p:
            self.p = signal

        if N > 250 and signal > self.thresh and not self.pulse and N > (self.ibi // 5) * 3:
            self.pulse = True
            self.ibi = self.sample_counter - self.last_beat_time
            self.last_beat_time = self.sample_counter

            if self.second_beat:
                self.second_beat = False
                for i in range(10):
                    self.rate[i] = self.ibi

            if self.first_beat:
                self.first_beat = False
                self.second_beat = True
                return

            running_total = 0
            for i in range(9):
                self.rate[i] = self.rate[i+1]
                running_total += self.rate[i]
            self.rate[9] = self.ibi
            running_total += self.ibi
            running_total //= 10
            self.running_total = running_total

        if signal > self.thresh and self.pulse:
            self.pulse = False
            self.amp = self.p - self.t
            self.thresh = self.amp//2 + self.t
            self.p = self.thresh
            self.t = self.thresh

        if N > 2500:
            self.reset()
            return

    def get_bpm(self):
        if self.running_total <= 0:
            return None
        return 60000 / self.running_total