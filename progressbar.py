"""Progress bar module; animates spinning cursor"""
import sys
import time
import threading

class Spinner:
    """Spinner class to animate a spinning cursor in a separate thread"""
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        """Define spinning cursor as generator"""
        while 1:
            for cursor in '|/-\\':
                yield cursor

    def __init__(self, delay=None):
        """Initialize spinner object"""
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        """Run thread indefinitely until stop function is called"""
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        """Start spinner object; starts task in new thread"""
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        """Stops spinner object; halts thread"""
        self.busy = False
        time.sleep(self.delay)
