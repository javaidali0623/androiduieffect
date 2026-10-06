from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QGroupBox, QHBoxLayout, QFormLayout, QWidget, QPushButton, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
from pyshark.capture.live_capture import LiveCapture

import sys
import time
import zlib
import queue
import logging
import threading
from datetime import datetime

from threads import PySharkListener, PyProxyInspector
from proxy import Socks5Server
from app_styles import AppStyles

# Shared queue for thread communication
packet_queue = queue.Queue()


def check_packet(raw_packets):
    def compare_tcp_data_with_crc32(data1: bytes, data2: bytes) -> bool:
        checksum1 = zlib.crc32(data1)
        checksum2 = zlib.crc32(data2)
        return checksum1 == checksum2

    if len(raw_packets) == 0:
        return False
    time.sleep(0.3)
    captured_packets = []
    if packet_queue is not None:
        while not packet_queue.empty():
            captured_packets.append(packet_queue.get())
        if len(captured_packets) > 0:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print("---------------------------------------------------   Delay 200ms -------------------   Current Time:", formatted_time)
            captured_packets_byte = [bytes.fromhex(str(packet['TCP'].payload).replace(":", '')) for packet in captured_packets] 
            for raw_packet in raw_packets:
                raw_packet_byte = bytes(raw_packet)
                for index, captured_packet_byte in enumerate(captured_packets_byte):
                    if compare_tcp_data_with_crc32(raw_packet_byte, captured_packet_byte):
                        captured_packets_byte.remove(captured_packet_byte)
                        captured_packets.pop(index)
                        print(f"========={captured_packets[index]['type']}=========================   Match Found -------------------   Current Time:", formatted_time)
                        time.sleep(3)
    return False

class MainWindow(QWidget):
    listener : PySharkListener
    proxyInspector : threading.Thread

    def __init__(self):
        super().__init__()
        self.init_ui()

        
        self._is_listening = False
        self._is_proxying = False
        
        
    def init_ui(self):
        # Customize Window
        self.setWindowTitle("Evoxy Auto")
        self.setGeometry(100, 100, 400, 600)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f0f0f0"))  # Light gray background
        self.setPalette(palette)

        layout = QVBoxLayout()
        # layout.addWidget(self.label)
        # layout.addWidget(self.button)
        layout.addWidget(self.game_status_group())
        layout.addWidget(self.betting_control_group())
        layout.addWidget(self.service_control_group())
        self.setLayout(layout)
        self.setWindowTitle("Evoxy")

    def game_status_group(self) -> QGroupBox:
        game_status_group = QGroupBox("Game Status"); game_status_group.setFont(QFont("Arial", 8))
        game_status_layout = QFormLayout()
        
        self.game_id = QLineEdit(); self.game_id.setReadOnly(True); self.game_id.setFont(QFont("Arial", 8))
        self.time = QLineEdit(); self.time.setReadOnly(True); self.time.setFont(AppStyles.label_small_font)
        self.player_score = QLineEdit(); self.player_score.setReadOnly(True); self.player_score.setFont(AppStyles.label_small_font)
        self.banker_score = QLineEdit(); self.banker_score.setReadOnly(True); self.banker_score.setFont(AppStyles.label_small_font)
        self.winner = QLineEdit(); self.winner.setReadOnly(True); self.winner.setFont(AppStyles.label_small_font)
        
        label = QLabel("Game ID:"); label.setFont(AppStyles.label_small_font)
        game_status_layout.addRow(label, self.game_id)
        label = QLabel("Time:"); label.setFont(AppStyles.label_small_font)
        game_status_layout.addRow(label, self.time)
        label = QLabel("Player Score:"); label.setFont(AppStyles.label_small_font)
        game_status_layout.addRow(label, self.player_score)
        label = QLabel("Banker Score:"); label.setFont(AppStyles.label_small_font)
        game_status_layout.addRow(label, self.banker_score)
        label = QLabel("Winner:"); label.setFont(AppStyles.label_small_font)
        game_status_layout.addRow(label, self.winner)

        game_status_group.setLayout(game_status_layout)

        return game_status_group
        
    def betting_control_group(self) -> QGroupBox:
        betting_control_group = QGroupBox("Betting Control"); betting_control_group.setFont(QFont("Arial", 8))
        betting_control_layout = QVBoxLayout()
        betting_buttons_layout = QHBoxLayout()
        
        self.player_button = QPushButton("Player"); self.player_button.setFont(AppStyles.label_small_font)
        self.banker_button = QPushButton("Banker"); self.banker_button.setFont(AppStyles.label_small_font)
        self.force_cancel_button = QPushButton("Force Cancel"); self.force_cancel_button.setFont(AppStyles.label_small_font)
        self.label = QLabel("Start Proxy First ...", self)
        self.label.setFont(AppStyles.label_small_font)
        self.label.setStyleSheet(AppStyles.info_css)
        

        betting_buttons_layout.addWidget(self.player_button)
        betting_buttons_layout.addWidget(self.banker_button)
        betting_buttons_layout.addWidget(self.force_cancel_button)
        
        betting_control_layout.addLayout(betting_buttons_layout)
        betting_control_layout.addWidget(self.label)
        
        betting_control_group.setLayout(betting_control_layout)
        
        return betting_control_group

    def service_control_group(self) -> QGroupBox:
        service_control_group = QGroupBox("Service Control"); service_control_group.setFont(QFont("Arial", 8))
        service_control_layout = QVBoxLayout()
        
        self.proxy_button = QPushButton("Start Proxy"); self.proxy_button.setFont(AppStyles.label_small_font)
        self.proxy_button.clicked.connect(self._handle_proxy)
        self.listener_button = QPushButton("Start Listening"); self.listener_button.setFont(AppStyles.label_small_font)
        self.listener_button.clicked.connect(self._handle_listner)
        
        service_control_layout.addWidget(self.proxy_button)
        service_control_layout.addWidget(self.listener_button)

        service_control_group.setLayout(service_control_layout)

        return service_control_group

    def update_label(self, message):
        self.label.setText(message)

    def _handle_proxy(self):
        try:
            if self._is_proxying:
                print("Loger : stopping proxy")
                self.proxyInspector.stop()
                self.proxyInspector.join()
                self.proxyInspector = None
                # self.proxyInspector.terminate()
                self._is_proxying = False
                self.proxy_button.setText("Start Proxy")
                self.label.setText("Proxy service stopped.")
                self.label.setStyleSheet(AppStyles.warn_css)
                self.listener_button.setEnabled(False)
            else:
                print("Loger : starting proxy")
                self.proxyInspector = PyProxyInspector(packet_queue = packet_queue)
                self.proxyInspector.start()
                self._is_proxying = True
                self.proxy_button.setText("Stop Proxy")
                self.label.setText("Proxy service started...")
                self.label.setStyleSheet(AppStyles.info_css)
                self.listener_button.setEnabled(True)
        except Exception as e:
            print(f"Error while starting/stopping proxy server : \n\t\t {str(e)}")


    def _handle_listner(self):
        if (not self._is_listening):
            print("Loger : starting listener")
            self.listener = PySharkListener(packet_queue = packet_queue)
            self.listener.update_game_status.connect(self.update_game_status)
            self.listener.start()
            self._is_listening = True
            self.listener_button.setText("Stop Listening")
            self.label.setText("Listening to Game Status...")
            self.label.setStyleSheet(AppStyles.info_css)
        else:
            print("Loger : stopping listener")
            self.listener.capture.close()
            self.listener.stop()
            self.listener.terminate()
            self.listener_button.setText("Start Listening")
            self.label.setText("Stopped Listening to Game Status")
            self._is_listening = False


    def update_game_status(self, game_status: dict):
        try:
            if ("time" in game_status):
                self.time.setText(str(game_status['time']))
            match game_status['type']:
                case 'baccarat.cardDealt':
                    self.game_id.setText(game_status['args']['gameId'])
                    self.player_score.setText(str(game_status['args']['gameData']['playerHand']['score']) + "(Cards: " + \
                                            str(game_status['args']['gameData']['playerHand']['cards']) + ")")
                    self.banker_score.setText(str(game_status['args']['gameData']['bankerHand']['score']) + "(Cards: " + \
                                            str(game_status['args']['gameData']['bankerHand']['cards']) + ")")
                    if 'result' in game_status['args']['gameData']:
                        self.winner.setText(str(game_status['args']['gameData']['result']['winner']))
                        self.label.setText('Winner : ' + str(game_status['args']['dealing']))
                case 'metrics.pong':
                    pass # 'args' : 't' for timestamp
                case 'metrics.ping':
                    pass # 'args' : 't' for timestamp
                case 'baccarat.gameState' | 'baccarat.newGame' | 'baccarat.newGame':
                    self.game_id.setText(game_status['args']['gameId'])
                    if (game_status['type'] == 'baccarat.gameState'):
                        self.label.setText(str(game_status['args']['betting']) + '  |  ' + str(game_status['args']['dealing']))
                        if (game_status['args']['betting'] == 'BetsOpen'):
                            self.winner.setText("")
                            self.player_score.setText("")
                            self.banker_score.setText("")
                    if (game_status['type'] == 'baccarat.newGame'):
                        self.label.setText(f"New Game - Shoe Cards Out :{game_status['args']['shoeCardsOut']}")
                case _:
                    if (game_status['type'] != "baccarat.bettingStats"):
                        print(game_status['type'])
                    pass
        except Exception as e:
            print('Error while updating game status : ' + str(e))


    def closeEvent(self, event):
        # Cleanup when closing the application
        self.listener.terminate()
        self.proxyInspector.stop()
        event.accept()

if __name__ == '__main__':
    # Run the application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
