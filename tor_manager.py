"""
Módulo de Gestión de Tor
Manejo de servicios ocultos y enrutamiento anónimo
"""

import socket
import subprocess
import time
import os
import signal
from pathlib import Path
import threading


class TorManager:
    """Gestor de conexión Tor y servicios ocultos"""
    
    def __init__(self):
        self.tor_process = None
        self.tor_port = 9050  # Puerto SOCKS
        self.control_port = 9051
        self.hidden_service_port = 9999
        self.onion_address = None
        
        self.data_dir = Path.home() / '.deepchat' / 'tor_data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_running = False
    
    def start_tor(self):
        """Iniciar proceso Tor"""
        if self.is_running:
            return True
        
        print("Iniciando Tor...")
        
        # Configuración de Tor
        torrc_config = self._generate_torrc()
        torrc_path = self.data_dir / 'torrc'
        
        with open(torrc_path, 'w') as f:
            f.write(torrc_config)
        
        try:
            # Iniciar Tor
            # En Android, se usaría Orbot o tor binary compilado
            self.tor_process = subprocess.Popen(
                ['tor', '-f', str(torrc_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Esperar a que Tor esté listo
            time.sleep(10)
            
            if self._check_tor_connection():
                self.is_running = True
                print("Tor iniciado exitosamente")
                return True
            else:
                print("Error: Tor no se conectó")
                return False
                
        except FileNotFoundError:
            print("Error: Tor no está instalado")
            print("En Android, usar Orbot como backend")
            return False
        except Exception as e:
            print(f"Error iniciando Tor: {e}")
            return False
    
    def _generate_torrc(self):
        """Generar archivo de configuración torrc"""
        hidden_service_dir = self.data_dir / 'hidden_service'
        
        torrc = f"""
# Configuración Tor para DeepChat
DataDirectory {self.data_dir}
SocksPort {self.tor_port}
ControlPort {self.control_port}

# Servicio Oculto
HiddenServiceDir {hidden_service_dir}
HiddenServicePort 80 127.0.0.1:{self.hidden_service_port}

# Optimizaciones
ConnectionPadding 1
CircuitPadding 1
SafeLogging 1
MaxCircuitDirtiness 600

# Seguridad adicional
ExcludeExitNodes {{??}}
StrictNodes 1
"""
        return torrc
    
    def _check_tor_connection(self):
        """Verificar que Tor esté funcionando"""
        try:
            # Intentar conectar al puerto SOCKS
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', self.tor_port))
            sock.close()
            
            return result == 0
            
        except Exception as e:
            print(f"Error verificando Tor: {e}")
            return False
    
    def start_hidden_service(self):
        """Iniciar servicio oculto y obtener dirección .onion"""
        # Primero iniciar Tor
        if not self.is_running:
            if not self.start_tor():
                return None
        
        # Esperar a que se genere la dirección .onion
        hostname_file = self.data_dir / 'hidden_service' / 'hostname'
        
        # Esperar hasta 30 segundos
        for _ in range(30):
            if hostname_file.exists():
                with open(hostname_file, 'r') as f:
                    self.onion_address = f.read().strip()
                print(f"Servicio oculto: {self.onion_address}")
                return self.onion_address
            time.sleep(1)
        
        print("Error: No se generó dirección .onion")
        return None
    
    def create_tor_socket(self):
        """Crear socket que enruta por Tor (SOCKS5)"""
        import socks
        
        sock = socks.socksocket()
        sock.set_proxy(
            socks.SOCKS5,
            "127.0.0.1",
            self.tor_port
        )
        
        return sock
    
    def connect_to_onion(self, onion_address, port=80):
        """Conectar a un servicio .onion"""
        try:
            sock = self.create_tor_socket()
            sock.settimeout(30)
            sock.connect((onion_address, port))
            return sock
            
        except Exception as e:
            print(f"Error conectando a {onion_address}: {e}")
            return None
    
    def get_tor_ip(self):
        """Obtener IP pública a través de Tor (para verificar)"""
        try:
            import requests
            
            proxies = {
                'http': f'socks5://127.0.0.1:{self.tor_port}',
                'https': f'socks5://127.0.0.1:{self.tor_port}'
            }
            
            response = requests.get(
                'https://check.torproject.org/api/ip',
                proxies=proxies,
                timeout=30
            )
            
            data = response.json()
            
            if data.get('IsTor'):
                print(f"Conectado a Tor. IP: {data.get('IP')}")
                return data.get('IP')
            else:
                print("Advertencia: No estás conectado a Tor")
                return None
                
        except Exception as e:
            print(f"Error verificando IP de Tor: {e}")
            return None
    
    def renew_circuit(self):
        """Renovar circuito Tor (nueva ruta)"""
        try:
            from stem import Signal
            from stem.control import Controller
            
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                print("Circuito Tor renovado")
                return True
                
        except Exception as e:
            print(f"Error renovando circuito: {e}")
            return False
    
    def stop(self):
        """Detener Tor"""
        if self.tor_process:
            print("Deteniendo Tor...")
            self.tor_process.terminate()
            
            try:
                self.tor_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.tor_process.kill()
            
            self.is_running = False
            print("Tor detenido")
    
    def get_bandwidth_stats(self):
        """Obtener estadísticas de ancho de banda"""
        # TODO: Implementar lectura de estadísticas de Tor
        return {
            'read': 0,
            'written': 0
        }


class TorListener(threading.Thread):
    """Listener para servicios ocultos entrantes"""
    
    def __init__(self, port, callback):
        super().__init__(daemon=True)
        self.port = port
        self.callback = callback
        self.running = False
        self.server_socket = None
    
    def run(self):
        """Ejecutar listener"""
        self.running = True
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('127.0.0.1', self.port))
            self.server_socket.listen(5)
            
            print(f"Listener iniciado en puerto {self.port}")
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, address = self.server_socket.accept()
                    
                    # Manejar conexión en thread separado
                    threading.Thread(
                        target=self._handle_connection,
                        args=(client_socket,),
                        daemon=True
                    ).start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Error en listener: {e}")
                    
        except Exception as e:
            print(f"Error iniciando listener: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def _handle_connection(self, client_socket):
        """Manejar conexión entrante"""
        try:
            # Recibir datos
            data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                
                # Si recibimos mensaje completo (terminado en \n\n)
                if b"\n\n" in data:
                    break
            
            if data:
                # Llamar callback con los datos
                self.callback(data.decode('utf-8'))
            
        except Exception as e:
            print(f"Error manejando conexión: {e}")
        finally:
            client_socket.close()
    
    def stop(self):
        """Detener listener"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()


# Configuración para Android con Orbot
class OrbotManager:
    """
    Gestor para usar Orbot en Android
    Orbot es la implementación oficial de Tor para Android
    """
    
    def __init__(self):
        self.orbot_port = 9050
        self.is_orbot_running = False
    
    def check_orbot(self):
        """Verificar si Orbot está instalado y ejecutándose"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', self.orbot_port))
            sock.close()
            
            self.is_orbot_running = (result == 0)
            return self.is_orbot_running
            
        except:
            return False
    
    def start_orbot_intent(self):
        """
        Enviar intent para iniciar Orbot (Android)
        Requiere: from jnius import autoclass
        """
        try:
            from jnius import autoclass
            
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            intent = Intent()
            intent.setAction("org.torproject.android.intent.action.START")
            PythonActivity.mActivity.startActivity(intent)
            
            print("Intent enviado para iniciar Orbot")
            return True
            
        except Exception as e:
            print(f"Error iniciando Orbot: {e}")
            return False


if __name__ == '__main__':
    # Test de TorManager
    print("=== Test de TorManager ===\n")
    
    tor = TorManager()
    
    if tor.start_tor():
        # Obtener dirección .onion
        onion_addr = tor.start_hidden_service()
        
        if onion_addr:
            print(f"\nTu dirección .onion: {onion_addr}")
            
            # Verificar IP de Tor
            tor.get_tor_ip()
            
            # Iniciar listener
            def handle_message(data):
                print(f"Mensaje recibido: {data}")
            
            listener = TorListener(tor.hidden_service_port, handle_message)
            listener.start()
            
            print("\nListener activo. Presiona Ctrl+C para detener...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nDeteniendo...")
                listener.stop()
                tor.stop()
