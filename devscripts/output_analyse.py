import socket
import json
import time
import logging
import sys

# IP configuration variable
IP_ADDRESS = "192.168.2.200"

class CozyLifeDebugger:
    def __init__(self, ip=IP_ADDRESS, port=5555):
        self.ip = ip
        self.port = port
        self.socket = None

        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cozylife_debug.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish connection to device"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.ip, self.port))
            self.logger.info(f"Successfully connected to {self.ip}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    def send_command(self, command):
        """Send command and log raw response"""
        try:
            # Add newline to command
            payload = json.dumps(command) + "\r\n"
            self.logger.debug(f"Sending: {payload.strip()}")

            self.socket.send(payload.encode('utf-8'))

            # Read response with raw data logging
            data = ""
            start_time = time.time()

            while time.time() - start_time < 5:  # 5 second timeout
                try:
                    chunk = self.socket.recv(1024)
                    if not chunk:
                        break

                    # Log raw bytes
                    self.logger.debug(f"Raw bytes received: {chunk}")

                    # Try to decode and log
                    try:
                        decoded = chunk.decode('utf-8')
                        data += decoded
                        self.logger.debug(f"Decoded chunk: {decoded}")
                    except UnicodeDecodeError:
                        self.logger.warning(f"Could not decode chunk: {chunk}")

                    # If we see a newline, we might have a complete message
                    if '\n' in data:
                        self.logger.debug(f"Complete message received: {data}")
                        break

                except socket.timeout:
                    break

            return data
        except Exception as e:
            self.logger.error(f"Error in send_command: {e}")
            return None

    def test_commands(self):
        """Test various commands and log responses"""
        test_commands = [
            # Query device info
            {
                'cmd': 0,
                'pv': 0,
                'sn': str(int(time.time() * 1000)),
                'msg': {}
            },
            # Query state
            {
                'cmd': 2,
                'pv': 0,
                'sn': str(int(time.time() * 1000)),
                'msg': {
                    'attr': [0]
                }
            },
            # Query power
            {
                'cmd': 2,
                'pv': 0,
                'sn': str(int(time.time() * 1000)),
                'msg': {
                    'attr': [28]
                }
            }
        ]

        for cmd in test_commands:
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"Testing command: {cmd['cmd']}")
            response = self.send_command(cmd)

            self.logger.info("Raw response:")
            self.logger.info(response)

            self.logger.info("Attempting to parse JSON responses:")
            # Try to parse each line as JSON
            if response:
                for line in response.split('\n'):
                    if line.strip():
                        try:
                            parsed = json.loads(line)
                            self.logger.info(f"Parsed JSON: {json.dumps(parsed, indent=2)}")
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON parse error: {e} for line: {line}")

            time.sleep(1)  # Wait between commands

    def run_debug_session(self):
        """Run a complete debug session"""
        try:
            self.logger.info(f"Starting debug session for {self.ip}:{self.port}")

            if not self.connect():
                return

            self.test_commands()

        except Exception as e:
            self.logger.error(f"Debug session error: {e}")
        finally:
            if self.socket:
                self.socket.close()
                self.logger.info("Connection closed")

if __name__ == "__main__":
    # Create and run debugger
    debugger = CozyLifeDebugger()
    debugger.run_debug_session()
