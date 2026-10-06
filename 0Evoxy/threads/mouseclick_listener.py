import json, os
import pyshark
import threading
import queue

from PyQt5.QtCore import QThread, pyqtSignal
from pyshark.capture.live_capture import LiveCapture

from pynput import mouse
import pygetwindow as gw
import threading

class PyMouseListener(QThread):
    update_click_event_signal = pyqtSignal(str)
    
    def __init__(self, **kwargs):
        super().__init__()

        self._stop_event = threading.Event()


    def run(self):
        def on_click(x, y, button, pressed):
            if pressed:
                # Get active window title on mouse click
                active_window = gw.getActiveWindow()
                window_title = active_window.title if active_window else "No Active Window"
                
                # Prepare the message
                message = f"Mouse clicked in window: '{window_title}' at position ({x}, {y})"
                
                # Emit the signal with the message
                self.mouse_event_signal.emit(message)

        # Start the mouse listener
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    
    def on_click(self, x, y, button, pressed):
        if pressed:
            # Get active window at the time of click
            active_window = gw.getActiveWindow()
            self.emit(f"{active_window.title}")
            if active_window:
                print(f"Mouse clicked in window: {active_window.title} at position ({x}, {y})")
            else:
                print(f"Mouse clicked at position ({x}, {y}) without active window")

    def stop(self):
        self._stop_event.set()
