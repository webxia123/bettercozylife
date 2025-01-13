import json
import socket
import time
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

class CozyLifeEnergyMonitor:
    def __init__(self, ip: str, port: int = 5555):
        self.ip = ip
        self.port = port
        self.socket = None
        self._connect()
        
    def _connect(self) -> None:
        """Establish connection to device"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3)
            self.socket.connect((self.ip, self.port))
        except Exception as e:
            _LOGGER.error(f"Connection failed: {e}")
            raise

    def _get_package(self, cmd: int, payload: dict) -> bytes:
        """Generate command package"""
        sn = str(int(round(time.time() * 1000)))
        message = {
            'pv': 0,
            'cmd': cmd,
            'sn': sn,
            'msg': payload
        }
        
        if cmd == 2:  # QUERY command
            message['msg'] = {'attr': [0]}
            
        return bytes(json.dumps(message) + "\r\n", encoding='utf8')

    def _send_command(self, cmd: int, payload: dict) -> Optional[dict]:
        """Send command and get response"""
        try:
            package = self._get_package(cmd, payload)
            self.socket.send(package)
            response = self.socket.recv(1024)
            return json.loads(response.strip())
        except Exception as e:
            _LOGGER.error(f"Command failed: {e}")
            self._connect()  # Try to reconnect
            return None

    def get_energy_data(self) -> Dict:
        """Query all potentially energy-related attributes"""
        # Query specific attributes we found in analysis
        payload = {'attr': [1, 2, 26, 28]}  # Key attributes found in analysis
        response = self._send_command(2, payload)
        
        if not response or 'msg' not in response or 'data' not in response['msg']:
            return {}

        data = response['msg']['data']
        
        # Map the data to more meaningful names based on analysis
        energy_data = {
            'power_state': data.get('1', 0),  # On/Off state
            'mode': data.get('2', 0),         # Operating mode
            'power': data.get('26', 0),       # Possibly current power draw
            'energy': data.get('28', 0)       # Possibly accumulated energy
        }
        
        return energy_data

    def monitor_energy(self, interval: int = 5):
        """Continuously monitor energy usage"""
        try:
            while True:
                energy_data = self.get_energy_data()
                if energy_data:
                    _LOGGER.info(f"""
Energy Stats:
- Power State: {'On' if energy_data['power_state'] else 'Off'}
- Mode: {energy_data['mode']}
- Current Power: {energy_data['power']} 
- Accumulated Energy: {energy_data['energy']}
""")
                time.sleep(interval)
        except KeyboardInterrupt:
            _LOGGER.info("Monitoring stopped by user")
        finally:
            if self.socket:
                self.socket.close()

def main():
    ip = "192.168.2.200"
    try:
        monitor = CozyLifeEnergyMonitor(ip)
        _LOGGER.info(f"Starting energy monitoring for device at {ip}")
        monitor.monitor_energy()
    except Exception as e:
        _LOGGER.error(f"Monitoring failed: {e}")

if __name__ == "__main__":
    main()