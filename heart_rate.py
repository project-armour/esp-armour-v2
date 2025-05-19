import micropython
from machine import Pin, ADC, Timer
from time import ticks_diff, ticks_us, ticks_ms
from asyncio import sleep_ms
from max30102 import *

from utils import CallbackSource


class HeartRate(CallbackSource):
    events = ('heart_rate',)
    def __init__(self, i2c, irq, sample_rate=100, window_size=150, smoothing_window=5, hr_compute_interval = 2):
        super().__init__()
        self.i2c = i2c
        self.irq = Pin(irq, Pin.IN)

        self.sensor = MAX30102(i2c)
        self.sensor.setup_sensor()
        self.sensor.set_sample_rate(sample_rate * 8)
        self.sensor.set_fifo_average(8)
        self.sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

        self.sample_rate = sample_rate
        self.window_size = window_size
        self.smoothing_window = smoothing_window
        self.hr_compute_interval = 2

        self.samples = []
        self.timestamps = []
        self.filtered_samples = []

        self.heart_rate = None
        self.ref_time = ticks_ms()

        if self.sensor.i2c_address not in i2c.scan():
            print("Sensor not found.")
            return

    def add_sample(self, sample):
        """Add a new sample to the monitor."""
        timestamp = ticks_ms()
        self.samples.append(sample)
        self.timestamps.append(timestamp)

        # Apply smoothing
        if len(self.samples) >= self.smoothing_window:
            smoothed_sample = (
                    sum(self.samples[-self.smoothing_window:]) / self.smoothing_window
            )
            self.filtered_samples.append(smoothed_sample)
        else:
            self.filtered_samples.append(sample)

        # Maintain the size of samples and timestamps
        if len(self.samples) > self.window_size:
            self.samples.pop(0)
            self.timestamps.pop(0)
            self.filtered_samples.pop(0)

    def find_peaks(self):
        """Find peaks in the filtered samples."""
        peaks = []

        if len(self.filtered_samples) < 3:  # Need at least three samples to find a peak
            return peaks

        # Calculate dynamic threshold based on the min and max of the recent window of filtered samples
        recent_samples = self.filtered_samples[-self.window_size:]
        min_val = min(recent_samples)
        max_val = max(recent_samples)
        threshold = (
                min_val + (max_val - min_val) * 0.5
        )  # 50% between min and max as a threshold

        for i in range(1, len(self.filtered_samples) - 1):
            if (
                    self.filtered_samples[i] > threshold
                    and self.filtered_samples[i - 1] < self.filtered_samples[i]
                    and self.filtered_samples[i] > self.filtered_samples[i + 1]
            ):
                peak_time = self.timestamps[i]
                peaks.append((peak_time, self.filtered_samples[i]))

        return peaks

    def calculate_heart_rate(self):
        """Calculate the heart rate in beats per minute (BPM)."""
        peaks = self.find_peaks()

        if len(peaks) < 2:
            return None  # Not enough peaks to calculate heart rate

        # Calculate the average interval between peaks in milliseconds
        intervals = []
        for i in range(1, len(peaks)):
            interval = ticks_diff(peaks[i][0], peaks[i - 1][0])
            intervals.append(interval)

        average_interval = sum(intervals) / len(intervals)

        # Convert intervals to heart rate in beats per minute (BPM)
        heart_rate = (
            60000 // average_interval
        )  # 60 seconds per minute * 1000 ms per second

        if heart_rate > 300:
            return None

        return heart_rate

    def get_heart_rate(self):
        return self.heart_rate

    async def mainloop(self):
        while True:
            # The check() method has to be continuously polled, to check if
            # there are new readings into the sensor's FIFO queue. When new
            # readings are available, this function will put them into the storage.
            self.sensor.check()

            # Check if the storage contains available samples
            while self.sensor.available():
                # Access the storage FIFO and gather the readings (integers)
                red_reading = self.sensor.pop_red_from_storage()
                ir_reading = self.sensor.pop_ir_from_storage()

                # Add the IR reading to the heart rate monitor
                # Note: based on the skin color, the red, IR or green LED can be used
                # to calculate the heart rate with more accuracy.
                print("Red:", red_reading)
                self.add_sample(red_reading)

            # Periodically calculate the heart rate every `hr_compute_interval` seconds
            if ticks_diff(ticks_ms(), self.ref_time) / 1000 > self.hr_compute_interval:
                # Calculate the heart rate
                self.heart_rate = self.calculate_heart_rate()
                # Reset the reference time
                self.ref_time = ticks_ms()
                self.trigger('heart_rate', self.heart_rate)
            sleep_ms(20)