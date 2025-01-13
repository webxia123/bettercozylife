import json
import socket
import time
import logging
from typing import Dict, List, Any, Optional
import itertools

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

class CozyLifeAnalyzer:
    def __init__(self, ip: str, port: int = 5555):
        self.ip = ip
        self.port = port
        self.socket = None
        self.device_info = {}
        self.discovered_commands = {}
        self.known_commands = {0: "INFO", 2: "QUERY", 3: "SET"}
        
    def connect(self) -> bool:
        """Establish connection to device"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3)
            self.socket.connect((self.ip, self.port))
            return True
        except Exception as e:
            _LOGGER.error(f"Connection failed: {e}")
            return False

    def _get_package(self, cmd: int, payload: dict) -> bytes:
        """Generate command package"""
        sn = str(int(round(time.time() * 1000)))
        message = {
            'pv': 0,
            'cmd': cmd,
            'sn': sn,
            'msg': payload
        }
        
        if cmd == 3:  # SET command
            message['msg'] = {
                'attr': [int(k) for k in payload.keys()],
                'data': payload
            }
        elif cmd == 2:  # QUERY command
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
            return None

    def get_device_info(self) -> Dict:
        """Get basic device information"""
        response = self._send_command(0, {})
        if response and 'msg' in response:
            self.device_info = response['msg']
            _LOGGER.info(f"Device Info: {json.dumps(self.device_info, indent=2)}")
            return self.device_info
        return {}

    def analyze_query_attributes(self) -> Dict:
        """Test different attribute combinations for QUERY command"""
        discovered_attrs = {}
        
        # Try individual attributes 0-255
        for attr in range(256):
            payload = {'attr': [attr]}
            response = self._send_command(2, payload)
            if response and 'msg' in response and 'data' in response['msg']:
                discovered_attrs[attr] = response['msg']['data']
                _LOGGER.info(f"Found valid attribute {attr}: {response['msg']['data']}")
                
        return discovered_attrs

    def analyze_set_commands(self, known_attrs: Dict) -> Dict:
        """Test SET commands with discovered attributes"""
        set_results = {}
        test_values = [0, 1, 255, 1000, 65535]  # Common values to test
        
        for attr in known_attrs.keys():
            attr_results = {}
            for value in test_values:
                payload = {str(attr): value}
                response = self._send_command(3, payload)
                if response and response.get('res') == 0:
                    attr_results[value] = True
                    _LOGGER.info(f"SET attr {attr} = {value} succeeded")
                else:
                    attr_results[value] = False
                    
            set_results[attr] = attr_results
            time.sleep(0.5)  # Avoid overwhelming the device
            
        return set_results

    def analyze_command_ranges(self) -> Dict:
        """Test different command numbers to find undocumented commands"""
        command_results = {}
        
        for cmd in range(20):  # Test first 20 command numbers
            if cmd in self.known_commands:
                continue
                
            response = self._send_command(cmd, {})
            if response and response.get('res') == 0:
                command_results[cmd] = response
                _LOGGER.info(f"Found potentially valid command {cmd}: {response}")
                
        return command_results

    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete device analysis"""
        if not self.connect():
            return {"error": "Connection failed"}

        analysis_results = {
            "device_info": self.get_device_info(),
            "query_attributes": {},
            "set_commands": {},
            "unknown_commands": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Run attribute analysis
        _LOGGER.info("Analyzing QUERY attributes...")
        analysis_results["query_attributes"] = self.analyze_query_attributes()

        # Test SET commands
        _LOGGER.info("Analyzing SET commands...")
        analysis_results["set_commands"] = self.analyze_set_commands(analysis_results["query_attributes"])

        # Look for unknown commands
        _LOGGER.info("Searching for unknown commands...")
        analysis_results["unknown_commands"] = self.analyze_command_ranges()

        # Save results to file
        with open(f"cozylife_analysis_{self.ip}_{time.strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(analysis_results, f, indent=2)

        return analysis_results

def main():
    ip = "192.168.2.200"
    analyzer = CozyLifeAnalyzer(ip)
    
    _LOGGER.info(f"Starting analysis of device at {ip}")
    results = analyzer.run_full_analysis()
    
    _LOGGER.info("\n=== Analysis Complete ===")
    _LOGGER.info(f"Results saved to cozylife_analysis_{ip}_{time.strftime('%Y%m%d_%H%M%S')}.json")
    
    if "error" not in results:
        _LOGGER.info(f"\nDevice Info: {json.dumps(results['device_info'], indent=2)}")
        _LOGGER.info(f"\nDiscovered Attributes: {len(results['query_attributes'])}")
        _LOGGER.info(f"SET Command Tests: {len(results['set_commands'])}")
        _LOGGER.info(f"Unknown Commands Found: {len(results['unknown_commands'])}")
    else:
        _LOGGER.error(f"Analysis failed: {results['error']}")

if __name__ == "__main__":
    main()