import asyncio
import sys
import socket
import threading
import select

PY3 = sys.version_info[0] == 3
if PY3:
    chr_to_int = lambda x: x
    encode_str = lambda x: x.encode()
else:
    chr_to_int = ord
    encode_str = lambda x: x

SOCK_TIMEOUT = 5  # seconds
RESEND_TIMEOUT = 60  # seconds
MAX_RECEIVE_SIZE = 65536

VER = b'\x05'
METHOD = b'\x00'
SUCCESS = b'\x00'
SOCK_FAIL = b'\x01'
NETWORK_FAIL = b'\x02'
HOST_FAIL = b'\x04'
REFUSED = b'\x05'
TTL_EXPIRED = b'\x06'
UNSUPPORTED_CMD = b'\x07'
ADDR_TYPE_UNSUPPORT = b'\x08'
UNASSIGNED = b'\x09'

ADDR_TYPE_IPV4 = b'\x01'
ADDR_TYPE_DOMAIN = b'\x03'
ADDR_TYPE_IPV6 = b'\x04'

CMD_TYPE_CONNECT = b'\x01'
CMD_TYPE_TCP_BIND = b'\x02'
CMD_TYPE_UDP = b'\x03'

BLOCK_LIST_SUBDOMAIN = 'egcvi.com'  # disable live video stream
FILTER_LIST_SUBDOMAIN = 'evo-games.com' # socket url for betting

class Socks5Server:
    def __init__(self, host, port, check_packet, logger, backlog=128, **kwargs):
        self.host = host
        self.port = port
        self.check_packet = check_packet
        self.logger = logger
        self.backlog = backlog
        self.client_dest_map_lock = threading.Lock()
        # This holds client_sock -> dest_sock and dest_sock -> client_sock mappings
        self.client_dest_map = {}
        # Maps from sock -> buffer to send to sock
        self.sock_send_buffers = {}
        self.sock_buffer_stack = {} # for parsing tls data
        self.filter_sock_list = []
        # Set the stopper event
        self._stop_event : threading.Event
        if 'stopper' in kwargs:
            self._stop_event = kwargs['stopper']
        else:
            self._stop_event = threading.Event()
    
    def filter_buffer(self, sock, buffer):
        if sock not in self.filter_sock_list:
            return buffer

        if sock not in self.sock_buffer_stack:
            self.sock_buffer_stack[sock] = buffer
        else:
            self.sock_buffer_stack[sock] += buffer

        temp_buffer_stack = self.sock_buffer_stack[sock]

        packets = []
        while True:
            if len(temp_buffer_stack) < 5:
                break
            content_type = temp_buffer_stack[0]
            version = temp_buffer_stack[1:3]
            length = int.from_bytes(temp_buffer_stack[3:5], 'big')
            if content_type != 23:
                self.sock_buffer_stack[sock] = []
                return buffer
            if len(temp_buffer_stack) < length + 5:
                break
            else:
                packet = temp_buffer_stack[:length + 5]
                packets.append(packet)
                temp_buffer_stack = temp_buffer_stack[length + 5:]
                self.sock_buffer_stack[sock] = temp_buffer_stack[:]
        if len(packets) == 0:
            return buffer
        # if content_type not in [20, 21, 22, 23, 24]:
        #     raise('Invalid content type!')
            # if content_type == 20:
            #     print('TLS ChangeCipherSpec')
            # elif content_type == 21:
            #     print('TLS Alert')
            # elif content_type == 22:
            #     print('TLS Handshake')
            #     client_random = buffer_stack[11:43]
            #     # print(client_random)
            # elif content_type == 23:
            #     print('TLS Application')
            # elif content_type == 24:
            #     print('TLS Heartbeat')
        if callable(self.check_packet):
            try:
                result = self.check_packet(packets)
                if result:
                    print(f'----------Checked Packets----  {len(packets)}  -------------------------   Packet Matched')
                    return b''  ## to do
                else:
                    return buffer
            except Exception as e:
                self.logger.error(f"An unexpected error occurred: {e}")
            
    def remove_from_filter(self, sock):
        if sock in self.filter_sock_list:
            self.filter_sock_list.remove(sock)
        if sock in self.sock_buffer_stack:
            self.sock_buffer_stack.pop(sock)

    def buffer_receive(self, sock):
        """ Reads into the buffer for the corresponding relay socket. """
        if sock not in self.client_dest_map:
            # self.logger.warning(f'Tried to read from a closed socket: {sock}')
            return  # Early exit if the socket is not in the map

        target_sock = self.client_dest_map[sock]
        buf = sock.recv(MAX_RECEIVE_SIZE)
        if len(buf) == 0:
            self.flush_and_close_sock_pair(sock)
        else:
            buf = self.filter_buffer(sock, buf)
            if target_sock not in self.sock_send_buffers:
                self.sock_send_buffers[target_sock] = buf
            else:
                self.sock_send_buffers[target_sock] += buf

    def buffer_send(self, sock):
        if sock in self.sock_send_buffers:
            try:
                bytes_sent = sock.send(self.sock_send_buffers[sock])
                self.sock_send_buffers[sock] = self.sock_send_buffers[sock][bytes_sent:]
            except ConnectionResetError as e:
                # self.logger.error(f'Connection reset by peer: {e}')
                self.flush_and_close_sock_pair(sock, str(e))

    def flush_and_close_sock_pair(self, sock, error_msg=None):
        """ Flush any remaining send buffers to the correct socket, close the sockets, and remove
        the pair of sockets from both the client_dest_map and the sock_send_buffers dicts. """
        if error_msg:
            # self.logger.error('Flushing and closing pair due to error: %s' % error_msg)
            pass
        else:
            # self.logger.info('Flushing and closing finished connection pair')
            pass
        
        with self.client_dest_map_lock:
            # Check if the sock is in the map
            if sock in self.client_dest_map:
                partner_sock = self.client_dest_map.pop(sock)
                self.client_dest_map.pop(partner_sock, None)  # Use pop with a default to avoid KeyError
            else:
                # self.logger.warning(f'Tried to close a socket not in the map: {sock}')
                return  # If the socket is already removed, exit early

        self.remove_from_filter(sock)
        self.remove_from_filter(partner_sock)

        try:
            partner_sock.send(self.sock_send_buffers.pop(partner_sock, b''))
            partner_sock.close()
            sock.send(self.sock_send_buffers.pop(sock, b''))
            sock.close()
        except Exception as e:
            # self.logger.error(f'Error while flushing and closing sockets: {e}')
            pass

    def establish_socks5(self, sock):
        """ Speak the SOCKS5 protocol to get and return dest_host, dest_port. """
        dest_host, dest_port = None, None
        try:
            ver, nmethods, methods = sock.recv(1), sock.recv(1), sock.recv(1)
            sock.sendall(VER + METHOD)
            ver, cmd, rsv, address_type = sock.recv(1), sock.recv(1), sock.recv(1), sock.recv(1)
            dst_addr = None
            dst_port = None
            if address_type == ADDR_TYPE_IPV4:
                dst_addr, dst_port = sock.recv(4), sock.recv(2)
                dst_addr = '.'.join([str(chr_to_int(i)) for i in dst_addr])
            elif address_type == ADDR_TYPE_DOMAIN:
                addr_len = ord(sock.recv(1))
                dst_addr, dst_port = sock.recv(addr_len), sock.recv(2)
                dst_addr = ''.join([chr(chr_to_int(i)) for i in dst_addr])
            elif address_type == ADDR_TYPE_IPV6:
                dst_addr, dst_port = sock.recv(16), sock.recv(2)
                tmp_addr = []
                for i in range(len(dst_addr) // 2):
                    tmp_addr.append(chr(dst_addr[2 * i] * 256 + dst_addr[2 * i + 1]))
                dst_addr = ':'.join(tmp_addr)
            dst_port = chr_to_int(dst_port[0]) * 256 + chr_to_int(dst_port[1])
            server_sock = sock
            server_ip = ''.join([chr(int(i)) for i in socket.gethostbyname(self.host).split('.')])
            if cmd == CMD_TYPE_TCP_BIND:
                # self.logger.error('TCP Bind requested, but is not supported by socks5_server')
                sock.close()
            elif cmd == CMD_TYPE_UDP:
                # self.logger.error('UDP requested, but is not supported by socks5_server')
                sock.close()
            elif cmd == CMD_TYPE_CONNECT:
                sock.sendall(VER + SUCCESS + b'\x00' + b'\x01' + encode_str(server_ip +
                                        chr(self.port // 256) + chr(self.port % 256)))
                dest_host, dest_port = dst_addr, dst_port
            else:
                # Unsupport/unknown Command
                # self.logger.error('Unsupported/unknown SOCKS5 command requested')
                sock.sendall(VER + UNSUPPORTED_CMD + encode_str(server_ip + chr(self.port // 256) +
                                        chr(self.port % 256)))
                sock.close()
        except KeyboardInterrupt as e:
            self.logger.error('Error in SOCKS5 establishment: %s' % e)
            pass

        return dest_host, dest_port

    def handle_connect_thread(self, client_sock, addr):
        """ Handles the establishment of the connection from the client, the socks5 protocol,
        and to the destination. Once finished, it puts the client and dest sockets into the
        self.client_dest_map, from where they are serviced by the main loop/thread. """
        # self.logger.info('Connection from: %s:%d' % addr)
        client_sock.settimeout(SOCK_TIMEOUT)

        
        dest_host, dest_port = self.establish_socks5(client_sock)
        if None in (dest_host, dest_port) or dest_host.endswith(BLOCK_LIST_SUBDOMAIN):
            return None

        # self.logger.debug('Trying to connect to destination: %s:%d' % (dest_host, dest_port))
        dest_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dest_sock.settimeout(RESEND_TIMEOUT)
        try:
            dest_sock.connect((dest_host, dest_port))
        except Exception as e:
            # self.logger.error('Failed to connect to requested destination (%s:%d) due to error: %s'
            #                   % (dest_host, dest_port, e))
            client_sock.close()
            return None

        # self.logger.debug('Connection to %s:%d established' % (dest_host, dest_port))

        # From this point on, we'll be doing nonblocking io on the sockets
        client_sock.settimeout(RESEND_TIMEOUT)
        client_sock.setblocking(0)
        dest_sock.setblocking(0)
        with self.client_dest_map_lock:
            self.client_dest_map[client_sock] = dest_sock
            self.client_dest_map[dest_sock] = client_sock
            if dest_host.endswith(FILTER_LIST_SUBDOMAIN):
                self.filter_sock_list.append(client_sock)
                self.filter_sock_list.append(dest_sock)

        # self.logger.info('SOCKS5 proxy from %s:%d to %s:%d established' %
                        #  (addr[0], addr[1], dest_host, dest_port))

    def accept_connection(self):
        (client, addr) = self.server_sock.accept()
        t = threading.Thread(target=self.handle_connect_thread, args=(client, addr))
        t.daemon = True
        t.start()

    def serve_forever(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(self.backlog)
        # self.logger.info('Serving on %s:%d' % (self.host, self.port))

        while True:
            if self._stop_event.is_set():
                self.server_sock.close()
                self.flush_and_close_sock_pair(self.server_sock)
                print("Socks Server Stopped!!!")
                return
            connected_sockets = list(self.client_dest_map.keys())
            in_socks = [self.server_sock] + connected_sockets
            out_socks = connected_sockets
            if len(connected_sockets) > 500:
                self.logger.info(f"Number of connected sockets{len(connected_sockets)}")
            in_ready, out_ready, err_ready = select.select(in_socks, out_socks, [], 0.01)

            for sock in in_ready:
                if sock == self.server_sock:
                    self.accept_connection()
                else:
                    try:
                        self.buffer_receive(sock)
                    except Exception as e:
                        self.flush_and_close_sock_pair(sock, str(e))

            for sock in out_ready:
                try:
                    self.buffer_send(sock)
                except Exception as e:
                    self.flush_and_close_sock_pair(sock, str(e))

            for sock in err_ready:
                if sock == self.server_sock:
                    self.logger.critical('Error in server socket; closing down')
                    for c in connected_sockets:
                        c.close()
                    self.server_sock.close()
                    sys.exit(1)
                else:
                    self.flush_and_close_sock_pair(sock, 'Unknown socket error')
