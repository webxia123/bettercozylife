"""CozyLife device control class."""
import socket
import json
import time
import logging

_LOGGER = logging.getLogger(__name__)

class CozyLifeDevice:
    """Class to communicate with CozyLife devices."""

    def __init__(self, ip, port=5555):
        """Initialize the device."""
        self.ip = ip
        self.port = port
        self._socket = None

    def _ensure_connection(self):
        """Ensure connection is established."""
        if self._socket is None:
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(3)
                self._socket.connect((self.ip, self.port))
                return True
            except Exception as e:
                _LOGGER.error(f"Connection failed to {self.ip}: {e}")
                self._socket = None
                return False
        return True

    def _get_sn(self):
        """Generate sequence number."""
        return str(int(round(time.time() * 1000)))

    def _send_message(self, command):
        """Send message to device."""
        if not self._ensure_connection():
            return None

        try:
            payload = json.dumps(command) + "\r\n"
            self._socket.send(payload.encode('utf-8'))
            response = self._socket.recv(1024)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            _LOGGER.error(f"Failed to communicate with {self.ip}: {e}")
            self._socket = None
            return None

    def send_command(self, state):
        """Send command to device."""
        command = {
            'cmd': CMD_SET,
            'pv': 0,
            'sn': self._get_sn(),
            'msg': {
                'attr': [1],
                'data': {
                    '1': 255 if state else 0
                }
            }
        }
        response = self._send_message(command)
        return response is not None and response.get('res') == 0

    def query_state(self):
        """Query device state."""
        command = {
            'cmd': CMD_QUERY,
            'pv': 0,
            'sn': self._get_sn(),
            'msg': {
                'attr': [0]
            }
        }
        response = self._send_message(command)
        if response and response.get('msg'):
            return response['msg'].get('data', {})
        return None