import time
import threading
from datetime import datetime, timedelta


class Alarm:
    def __init__(self, time_str, label="", repeat=False, snooze_duration=5, ring_callback=None):
        self.time_str = time_str
        self.label = label
        self.repeat = repeat
        self.snooze_duration = snooze_duration
        self.active = True
        self.thread = None
        self.ring_callback = ring_callback

    def set_alarm(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run_alarm, daemon=True)
        self.thread.start()

    def _run_alarm(self):
        while self.active:
            now = datetime.now().strftime("%H:%M")
            if now == self.time_str:
                self.ring_alarm()
                if not self.repeat:
                    self.active = False
                time.sleep(60)
            time.sleep(1)

    def ring_alarm(self):
        if self.ring_callback:
            self.ring_callback(self.label)

    def stop(self):
        self.active = False


class AlarmClock:
    def __init__(self):
        self.alarms = []

    def add_alarm(self, time_str, label="", repeat=False, snooze_duration=5, ring_callback=None):
        alarm = Alarm(time_str, label, repeat, snooze_duration, ring_callback)
        self.alarms.append(alarm)
        alarm.set_alarm()
        return alarm

    def remove_alarm(self, label):
        alarm_to_remove = None
        for alarm in self.alarms:
            if alarm.label == label:
                alarm.stop()
                alarm_to_remove = alarm
                break
        if alarm_to_remove:
            self.alarms.remove(alarm_to_remove)

    def list_alarms(self):
        if not self.alarms:
            return []
        return [{"time": a.time_str, "label": a.label, "active": a.active} for a in self.alarms]


class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.running = False
        self.elapsed = 0

    def start(self):
        if not self.running:
            self.start_time = time.time() - self.elapsed
            self.running = True

    def stop(self):
        if self.running:
            self.elapsed = time.time() - self.start_time
            self.running = False

    def reset(self):
        self.start_time = None
        self.elapsed = 0
        self.running = False

    def get_elapsed(self):
        if self.running:
            return time.time() - self.start_time
        return self.elapsed


class Timer:
    def __init__(self, duration, time_up_callback=None):
        self.duration = duration
        self.thread = None
        self.active = False
        self.start_time = 0
        self.time_up_callback = time_up_callback

    def start(self):
        if not self.thread or not self.thread.is_alive():
            self.active = True
            self.start_time = time.time()
            self.thread = threading.Thread(target=self._run_timer, daemon=True)
            self.thread.start()

    def _run_timer(self):
        self.active = True
        time.sleep(self.duration)
        if self.active:
            self.time_up()

    def time_up(self):
        if self.time_up_callback:
            self.time_up_callback()

    def cancel(self):
        self.active = False

    def get_remaining(self):
        if not self.active:
            return 0
        elapsed = time.time() - self.start_time
        remaining = self.duration - elapsed
        return max(0, remaining)