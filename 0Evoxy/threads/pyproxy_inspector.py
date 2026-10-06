import time, logging, sys
import threading
import queue
import zlib
from datetime import datetime

from proxy import Socks5Server

class PyProxyInspector(threading.Thread):

    proxy : Socks5Server
    logger : logging.Logger
    packet_queue : queue.Queue

    def __init__(self, **kwargs):
        super().__init__()
        self.logger = self.make_logger()
        self._stop_event = threading.Event() 
        self.proxy = Socks5Server('', 1080, self.check_packet, self.logger, stopper = self._stop_event)
        if "packet_queue" in kwargs:
            self.packet_queue = kwargs['packet_queue']
        else:
            self.packet_queue = None

    def run(self):
        self.proxy.serve_forever()
    
    def stop(self):
        self._stop_event.set()
        
        # await self.capture.close_async()

    def make_logger(log_path=None, log_level_str='INFO'):
        formatter = logging.Formatter('%(asctime)s: %(name)s (%(levelname)s): %(message)s')
        if log_path == None:
            log_handler = logging.FileHandler(log_path)
        else:
            log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setFormatter(formatter)
        logger = logging.getLogger('socks5_server')
        logger.addHandler(log_handler)
        log_level = logging.getLevelName(log_level_str.upper())
        logger.setLevel(log_level)
        return logger

    def check_packet(self, raw_packets):
        def compare_tcp_data_with_crc32(data1: bytes, data2: bytes) -> bool:
            checksum1 = zlib.crc32(data1)
            checksum2 = zlib.crc32(data2)
            return checksum1 == checksum2

        if len(raw_packets) == 0:
            return False

        time.sleep(0.3)
        captured_packets = []
        if self.packet_queue is not None:
            while not self.packet_queue.empty():
                captured_packets.append(self.packet_queue.get())
            if len(captured_packets) > 0:
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                print(f"------- {len(captured_packets)} -------------------------   Delay 200ms -------------------   Current Time:", formatted_time)
                captured_packets_byte = [bytes.fromhex(str(packet['TCP'].payload).replace(":", '')) for packet in captured_packets] 
                for raw_packet in raw_packets:
                    raw_packet_byte = bytes(raw_packet)
                    for index, captured_packet_byte in enumerate(captured_packets_byte):
                        if compare_tcp_data_with_crc32(raw_packet_byte, captured_packet_byte):
                            print(f"======= {index} {captured_packets[0]['websocket'].payload_text[15:30]}  ======   Match Found -------------------   Current Time:", formatted_time)
                            captured_packets_byte.remove(captured_packet_byte)
                            captured_packets.pop(index)
                            time.sleep(3)

        return False
        if self.packet_queue is not None:
            while not self.packet_queue.empty():
                parsed_packet = self.packet_queue.get()
                if bytes.fromhex(str(parsed_packet['TCP'].payload).replace(":", '')) == bytes(raw_packet):
                    self.logger.log("Packet Matched")
                    return True
            return False
        return False
        for packet in live_capture.captured_packets:
            if bytes.fromhex(str(packet['TCP'].payload).replace(":", '')) == bytes(raw_packet):
                return True
        return False