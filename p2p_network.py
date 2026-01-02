"""
Módulo de Red P2P
Comunicación peer-to-peer a través de Tor
"""

import socket
import json
import threading
import queue
import time
from datetime import datetime


class P2PNetwork:
    """Gestor de red peer-to-peer"""
    
    def __init__(self, tor_manager, crypto_manager):
        self.tor_manager = tor_manager
        self.crypto_manager = crypto_manager
        
        self.incoming_queue = queue.Queue()
        self.outgoing_queue = queue.Queue()
        
        self.listener_thread = None
        self.sender_thread = None
        
        self.is_running = False
        self.connections = {}
    
    def start(self):
        """Iniciar red P2P"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Iniciar listener para mensajes entrantes
        self.listener_thread = threading.Thread(
            target=self._listener_loop,
            daemon=True
        )
        self.listener_thread.start()
        
        # Iniciar sender para mensajes salientes
        self.sender_thread = threading.Thread(
            target=self._sender_loop,
            daemon=True
        )
        self.sender_thread.start()
        
        print("Red P2P iniciada")
    
    def stop(self):
        """Detener red P2P"""
        self.is_running = False
        
        # Cerrar todas las conexiones
        for conn in self.connections.values():
            try:
                conn.close()
            except:
                pass
        
        self.connections.clear()
        print("Red P2P detenida")
    
    def send_message(self, recipient_onion, encrypted_data):
        """
        Enviar mensaje encriptado a un peer
        
        Args:
            recipient_onion: Dirección .onion del destinatario
            encrypted_data: Datos ya encriptados (string JSON)
        """
        message_packet = {
            'type': 'message',
            'from': self.tor_manager.onion_address,
            'to': recipient_onion,
            'timestamp': datetime.now().isoformat(),
            'data': encrypted_data
        }
        
        # Agregar a cola de salida
        self.outgoing_queue.put((recipient_onion, message_packet))
    
    def send_video_frame(self, recipient_onion, frame_data):
        """
        Enviar frame de video
        
        Args:
            recipient_onion: Dirección .onion del destinatario
            frame_data: Frame de video encriptado
        """
        packet = {
            'type': 'video_frame',
            'from': self.tor_manager.onion_address,
            'timestamp': datetime.now().isoformat(),
            'data': frame_data
        }
        
        self.outgoing_queue.put((recipient_onion, packet))
    
    def request_public_key(self, peer_onion):
        """
        Solicitar clave pública de un peer
        
        Args:
            peer_onion: Dirección .onion del peer
        """
        request = {
            'type': 'key_request',
            'from': self.tor_manager.onion_address,
            'timestamp': datetime.now().isoformat()
        }
        
        self.outgoing_queue.put((peer_onion, request))
    
    def send_public_key(self, peer_onion):
        """
        Enviar nuestra clave pública a un peer
        
        Args:
            peer_onion: Dirección .onion del destinatario
        """
        response = {
            'type': 'key_response',
            'from': self.tor_manager.onion_address,
            'timestamp': datetime.now().isoformat(),
            'public_key': self.crypto_manager.export_public_key()
        }
        
        self.outgoing_queue.put((peer_onion, response))
    
    def _listener_loop(self):
        """Loop para recibir mensajes entrantes"""
        # Crear listener en el puerto del servicio oculto
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener_socket.bind(('127.0.0.1', self.tor_manager.hidden_service_port))
        listener_socket.listen(10)
        listener_socket.settimeout(1.0)
        
        print(f"Escuchando en puerto {self.tor_manager.hidden_service_port}")
        
        while self.is_running:
            try:
                client_socket, address = listener_socket.accept()
                
                # Manejar conexión en thread separado
                threading.Thread(
                    target=self._handle_incoming_connection,
                    args=(client_socket,),
                    daemon=True
                ).start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"Error en listener: {e}")
        
        listener_socket.close()
    
    def _handle_incoming_connection(self, client_socket):
        """Manejar conexión entrante"""
        try:
            # Recibir datos
            data = b""
            
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                
                # Buscar delimitador de fin de mensaje
                if b"\n\n" in data:
                    break
            
            if data:
                # Parsear mensaje
                message = json.loads(data.decode('utf-8').strip())
                
                # Procesar según tipo
                self._process_incoming_message(message)
            
        except json.JSONDecodeError as e:
            print(f"Error parseando mensaje: {e}")
        except Exception as e:
            print(f"Error manejando conexión entrante: {e}")
        finally:
            client_socket.close()
    
    def _process_incoming_message(self, message):
        """Procesar mensaje entrante según su tipo"""
        msg_type = message.get('type')
        sender = message.get('from')
        
        print(f"Mensaje recibido de {sender}: tipo={msg_type}")
        
        if msg_type == 'message':
            # Mensaje de chat encriptado
            encrypted_data = message.get('data')
            
            # Intentar desencriptar
            try:
                decrypted = self.crypto_manager.decrypt_message(encrypted_data)
                
                # Agregar a cola de mensajes entrantes
                self.incoming_queue.put({
                    'type': 'chat_message',
                    'from': sender,
                    'timestamp': message.get('timestamp'),
                    'text': decrypted
                })
                
            except Exception as e:
                print(f"Error desencriptando mensaje: {e}")
        
        elif msg_type == 'video_frame':
            # Frame de video
            frame_data = message.get('data')
            
            self.incoming_queue.put({
                'type': 'video_frame',
                'from': sender,
                'frame': frame_data
            })
        
        elif msg_type == 'key_request':
            # Solicitud de clave pública
            # Responder con nuestra clave pública
            self.send_public_key(sender)
        
        elif msg_type == 'key_response':
            # Respuesta con clave pública
            public_key = message.get('public_key')
            
            # Actualizar clave pública del contacto
            # TODO: Guardar en base de datos de contactos
            
            self.incoming_queue.put({
                'type': 'public_key',
                'from': sender,
                'public_key': public_key
            })
        
        elif msg_type == 'call_request':
            # Solicitud de videollamada
            self.incoming_queue.put({
                'type': 'call_request',
                'from': sender,
                'timestamp': message.get('timestamp')
            })
        
        elif msg_type == 'call_accept':
            # Aceptación de videollamada
            self.incoming_queue.put({
                'type': 'call_accept',
                'from': sender
            })
        
        elif msg_type == 'call_reject':
            # Rechazo de videollamada
            self.incoming_queue.put({
                'type': 'call_reject',
                'from': sender
            })
        
        else:
            print(f"Tipo de mensaje desconocido: {msg_type}")
    
    def _sender_loop(self):
        """Loop para enviar mensajes salientes"""
        while self.is_running:
            try:
                # Esperar mensaje en cola
                recipient, packet = self.outgoing_queue.get(timeout=1.0)
                
                # Enviar mensaje
                self._send_packet(recipient, packet)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error en sender loop: {e}")
    
    def _send_packet(self, recipient_onion, packet):
        """
        Enviar paquete a un peer
        
        Args:
            recipient_onion: Dirección .onion del destinatario
            packet: Diccionario con datos a enviar
        """
        try:
            # Conectar al peer vía Tor
            sock = self.tor_manager.connect_to_onion(recipient_onion, 80)
            
            if not sock:
                print(f"No se pudo conectar a {recipient_onion}")
                return False
            
            # Serializar paquete
            data = json.dumps(packet).encode('utf-8')
            
            # Enviar con delimitador
            sock.sendall(data + b"\n\n")
            
            sock.close()
            
            print(f"Paquete enviado a {recipient_onion}")
            return True
            
        except Exception as e:
            print(f"Error enviando paquete: {e}")
            return False
    
    def get_incoming_message(self, timeout=0.1):
        """
        Obtener siguiente mensaje de la cola de entrada
        
        Returns:
            Diccionario con mensaje o None si no hay mensajes
        """
        try:
            return self.incoming_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def initiate_call(self, recipient_onion):
        """
        Iniciar videollamada con un peer
        
        Args:
            recipient_onion: Dirección .onion del destinatario
        """
        request = {
            'type': 'call_request',
            'from': self.tor_manager.onion_address,
            'timestamp': datetime.now().isoformat()
        }
        
        self.outgoing_queue.put((recipient_onion, request))
    
    def accept_call(self, peer_onion):
        """
        Aceptar videollamada
        
        Args:
            peer_onion: Dirección .onion de quien llamó
        """
        response = {
            'type': 'call_accept',
            'from': self.tor_manager.onion_address,
            'timestamp': datetime.now().isoformat()
        }
        
        self.outgoing_queue.put((peer_onion, response))
    
    def reject_call(self, peer_onion):
        """
        Rechazar videollamada
        
        Args:
            peer_onion: Dirección .onion de quien llamó
        """
        response = {
            'type': 'call_reject',
            'from': self.tor_manager.onion_address,
            'timestamp': datetime.now().isoformat()
        }
        
        self.outgoing_queue.put((peer_onion, response))
    
    def get_connection_stats(self):
        """Obtener estadísticas de conexiones"""
        return {
            'active_connections': len(self.connections),
            'messages_queued': self.outgoing_queue.qsize(),
            'messages_pending': self.incoming_queue.qsize()
        }


class MessageProtocol:
    """
    Protocolo de mensajería con features adicionales
    """
    
    @staticmethod
    def create_text_message(text):
        """Crear mensaje de texto"""
        return {
            'type': 'text',
            'content': text
        }
    
    @staticmethod
    def create_file_message(filename, file_data):
        """Crear mensaje con archivo adjunto"""
        return {
            'type': 'file',
            'filename': filename,
            'data': file_data
        }
    
    @staticmethod
    def create_typing_indicator():
        """Crear indicador de "escribiendo..." """
        return {
            'type': 'typing'
        }
    
    @staticmethod
    def create_read_receipt(message_id):
        """Crear recibo de lectura"""
        return {
            'type': 'read_receipt',
            'message_id': message_id
        }


if __name__ == '__main__':
    # Test básico de P2P
    print("=== Test de P2PNetwork ===\n")
    
    from tor_manager import TorManager
    from crypto_manager import CryptoManager
    
    # Crear instancias
    tor = TorManager()
    crypto = CryptoManager()
    crypto.generate_keypair()
    
    # Iniciar Tor y servicio oculto
    if tor.start_tor():
        onion_addr = tor.start_hidden_service()
        
        if onion_addr:
            # Crear red P2P
            p2p = P2PNetwork(tor, crypto)
            p2p.start()
            
            print(f"Dirección .onion: {onion_addr}")
            print("Red P2P activa. Escuchando mensajes...")
            
            # Simular recepción de mensajes
            try:
                while True:
                    msg = p2p.get_incoming_message()
                    if msg:
                        print(f"Mensaje recibido: {msg}")
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\nDeteniendo...")
                p2p.stop()
                tor.stop()
