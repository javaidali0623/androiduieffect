import json, os
import pyshark
import threading
import queue

from PyQt5.QtCore import QThread, pyqtSignal
from pyshark.capture.live_capture import LiveCapture

class PySharkListener(QThread):

    capture : LiveCapture
    update_game_status = pyqtSignal(dict)  # Signal to update Game Status
    packet_queue : queue.Queue

    def __init__(self, **kwargs):
        super().__init__()
        if "packet_queue" in kwargs:
            self.packet_queue = kwargs['packet_queue']
        self.capture = pyshark.LiveCapture( 
            interface='Adapter for loopback traffic capture',  # capture traffic between proxy and browser
            bpf_filter='port 1080',

            # interface='ProtonVPN',
            # bpf_filter="src net 23.46.155.0/24 or dst net 23.46.155.0/24 and tcp port https",
            display_filter='data-text-lines', 
            override_prefs={'tls.keylog_file': os.path.abspath('C:\\sslkeys.log')},
            )
        self._stop_event = threading.Event()


    def run(self):
        print('------------------------------ Capturing now')
        for packet in self.capture.sniff_continuously():
            if self._stop_event.is_set():
                print("Stopping capture")
                return
            try:
                socket_layers = packet.get_multiple_layers('WEBSOCKET')
                for websocket_layer in socket_layers:
                    payload = json.loads(str(websocket_layer.payload_text))
                    if 'type' in payload:
                        self.update_game_status.emit(payload)
                        if payload['type'] == 'baccarat.playerBetRequest':
                            if self.packet_queue is not None:
                                print(f"Logger : put to queue from Listener ({payload['type']})")
                                self.packet_queue.put(packet)
                    if 'log' in payload and 'type' in payload['log']:
                        if payload['log']['type'] == 'CLIENT_BET_CHIP' and payload['log']['value']['amount'] > 0:
                            print(f"Logger : put to queue from Listener (Bet_chip {payload['log']['value']['amount']})")
                            self.packet_queue.put(packet)
                        if payload['log']['type'] == 'CLIENT_BET_ACCEPTED':
                            if bool(payload['log']['value']['originalBet']):
                                print(f"Logger : put to queue from Listener (Bet Accept {payload['log']['value']['originalBet']})")
                                self.packet_queue.put(packet)

            except Exception as e:
                pass
    
    def stop(self):
        self._stop_event.set()
        if self._stop_event.is_set():
            print("stopping Live Capture")
        # await self.capture.close_async()
