"""
Módulo de Grupos - Chat y Llamadas Grupales
Gestión de conversaciones multipunto encriptadas
"""

import json
import threading
import queue
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid


class GroupManager:
    """Gestor de grupos de chat y llamadas"""
    
    def __init__(self, crypto_manager, p2p_network):
        self.crypto_manager = crypto_manager
        self.p2p_network = p2p_network
        
        self.data_dir = Path.home() / '.deepchat' / 'groups'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.groups = {}
        self.active_group_calls = {}
        
        # Thread pool para procesamiento paralelo
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        self._load_groups()
    
    def create_group(self, group_name, members_onion_addresses):
        """
        Crear nuevo grupo
        
        Args:
            group_name: Nombre del grupo
            members_onion_addresses: Lista de direcciones .onion de miembros
            
        Returns:
            ID del grupo creado
        """
        group_id = str(uuid.uuid4())
        
        # Obtener mi dirección
        identity = self.crypto_manager.load_identity()
        my_address = identity['onion_address']
        
        # Crear estructura del grupo
        group = {
            'id': group_id,
            'name': group_name,
            'creator': my_address,
            'members': [my_address] + members_onion_addresses,
            'created_at': datetime.now().isoformat(),
            'admin': my_address,
            'encryption_key': self._generate_group_key()
        }
        
        self.groups[group_id] = group
        self._save_group(group_id)
        
        # Enviar invitaciones a todos los miembros (en paralelo)
        self._send_group_invitations(group)
        
        return group_id
    
    def _generate_group_key(self):
        """Generar clave de grupo compartida"""
        from cryptography.fernet import Fernet
        return Fernet.generate_key().decode('utf-8')
    
    def _send_group_invitations(self, group):
        """
        Enviar invitaciones a miembros del grupo en paralelo
        
        Args:
            group: Diccionario con datos del grupo
        """
        # Función para enviar invitación individual
        def send_invitation(member_address):
            if member_address == group['creator']:
                return  # No enviarse a sí mismo
            
            invitation = {
                'type': 'group_invitation',
                'group_id': group['id'],
                'group_name': group['name'],
                'creator': group['creator'],
                'encryption_key': group['encryption_key'],
                'members': group['members'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Encriptar invitación
            encrypted = self.crypto_manager.encrypt_message(
                json.dumps(invitation),
                None  # Usar clave pública del contacto
            )
            
            # Enviar por P2P
            self.p2p_network.send_message(member_address, encrypted)
            print(f"Invitación enviada a {member_address[:20]}...")
        
        # Enviar todas las invitaciones en paralelo
        futures = []
        for member in group['members']:
            future = self.executor.submit(send_invitation, member)
            futures.append(future)
        
        # Esperar a que todas terminen
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error enviando invitación: {e}")
    
    def add_member(self, group_id, member_address):
        """
        Agregar miembro a grupo existente
        
        Args:
            group_id: ID del grupo
            member_address: Dirección .onion del nuevo miembro
        """
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        
        # Verificar que quien agrega sea admin
        identity = self.crypto_manager.load_identity()
        if group['admin'] != identity['onion_address']:
            print("Solo el admin puede agregar miembros")
            return False
        
        # Agregar miembro
        if member_address not in group['members']:
            group['members'].append(member_address)
            self._save_group(group_id)
            
            # Enviar invitación al nuevo miembro
            self._send_group_invitations(group)
            
            # Notificar a otros miembros
            self._broadcast_to_group(
                group_id,
                {
                    'type': 'member_added',
                    'member': member_address,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return True
        
        return False
    
    def remove_member(self, group_id, member_address):
        """Remover miembro del grupo"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        
        # Verificar permisos
        identity = self.crypto_manager.load_identity()
        if group['admin'] != identity['onion_address']:
            return False
        
        # Remover
        if member_address in group['members']:
            group['members'].remove(member_address)
            self._save_group(group_id)
            
            # Notificar
            self._broadcast_to_group(
                group_id,
                {
                    'type': 'member_removed',
                    'member': member_address,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return True
        
        return False
    
    def send_group_message(self, group_id, message_text):
        """
        Enviar mensaje a grupo (broadcast paralelo a todos)
        
        Args:
            group_id: ID del grupo
            message_text: Texto del mensaje
        """
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        
        # Crear mensaje
        message = {
            'type': 'group_message',
            'group_id': group_id,
            'group_name': group['name'],
            'sender': self.crypto_manager.load_identity()['onion_address'],
            'text': message_text,
            'timestamp': datetime.now().isoformat(),
            'message_id': str(uuid.uuid4())
        }
        
        # Broadcast a todos los miembros en paralelo
        return self._broadcast_to_group(group_id, message)
    
    def _broadcast_to_group(self, group_id, message_data):
        """
        Broadcast mensaje a todos los miembros del grupo en paralelo
        
        Args:
            group_id: ID del grupo
            message_data: Datos del mensaje
            
        Returns:
            Número de miembros que recibieron el mensaje
        """
        group = self.groups[group_id]
        my_address = self.crypto_manager.load_identity()['onion_address']
        
        # Función para enviar a un miembro
        def send_to_member(member_address):
            if member_address == my_address:
                return True  # No enviarse a sí mismo
            
            try:
                # Encriptar con clave del grupo
                from cryptography.fernet import Fernet
                fernet = Fernet(group['encryption_key'].encode())
                encrypted_text = fernet.encrypt(
                    json.dumps(message_data).encode()
                ).decode()
                
                # Enviar por P2P
                self.p2p_network.send_message(member_address, encrypted_text)
                return True
            except Exception as e:
                print(f"Error enviando a {member_address[:20]}...: {e}")
                return False
        
        # Enviar a todos en paralelo usando ThreadPoolExecutor
        futures = []
        for member in group['members']:
            future = self.executor.submit(send_to_member, member)
            futures.append(future)
        
        # Contar éxitos
        successful = 0
        for future in as_completed(futures):
            try:
                if future.result():
                    successful += 1
            except Exception as e:
                print(f"Error en broadcast: {e}")
        
        # Guardar mensaje localmente
        self._save_group_message(group_id, message_data)
        
        print(f"Mensaje enviado a {successful}/{len(group['members'])} miembros")
        return successful
    
    def start_group_call(self, group_id):
        """
        Iniciar llamada grupal
        
        Args:
            group_id: ID del grupo
            
        Returns:
            ID de la llamada iniciada
        """
        if group_id not in self.groups:
            return None
        
        call_id = str(uuid.uuid4())
        
        call_info = {
            'call_id': call_id,
            'group_id': group_id,
            'initiator': self.crypto_manager.load_identity()['onion_address'],
            'started_at': datetime.now().isoformat(),
            'participants': [],
            'status': 'calling'
        }
        
        self.active_group_calls[call_id] = call_info
        
        # Enviar invitación de llamada a todos
        self._broadcast_to_group(
            group_id,
            {
                'type': 'group_call_invitation',
                'call_id': call_id,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return call_id
    
    def join_group_call(self, call_id):
        """Unirse a llamada grupal"""
        if call_id not in self.active_group_calls:
            return False
        
        call_info = self.active_group_calls[call_id]
        my_address = self.crypto_manager.load_identity()['onion_address']
        
        if my_address not in call_info['participants']:
            call_info['participants'].append(my_address)
            
            # Notificar a otros participantes
            group_id = call_info['group_id']
            self._broadcast_to_group(
                group_id,
                {
                    'type': 'participant_joined',
                    'call_id': call_id,
                    'participant': my_address,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return True
        
        return False
    
    def leave_group_call(self, call_id):
        """Salir de llamada grupal"""
        if call_id not in self.active_group_calls:
            return False
        
        call_info = self.active_group_calls[call_id]
        my_address = self.crypto_manager.load_identity()['onion_address']
        
        if my_address in call_info['participants']:
            call_info['participants'].remove(my_address)
            
            # Notificar
            group_id = call_info['group_id']
            self._broadcast_to_group(
                group_id,
                {
                    'type': 'participant_left',
                    'call_id': call_id,
                    'participant': my_address,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Si no quedan participantes, cerrar llamada
            if len(call_info['participants']) == 0:
                del self.active_group_calls[call_id]
            
            return True
        
        return False
    
    def _save_group(self, group_id):
        """Guardar grupo en disco"""
        group_file = self.data_dir / f'{group_id}.json'
        
        with open(group_file, 'w') as f:
            json.dump(self.groups[group_id], f, indent=2)
    
    def _load_groups(self):
        """Cargar grupos desde disco"""
        for group_file in self.data_dir.glob('*.json'):
            if group_file.name == 'messages.json':
                continue
            
            with open(group_file, 'r') as f:
                group = json.load(f)
                self.groups[group['id']] = group
    
    def _save_group_message(self, group_id, message):
        """Guardar mensaje de grupo localmente"""
        messages_file = self.data_dir / f'{group_id}_messages.json'
        
        # Cargar mensajes existentes
        if messages_file.exists():
            with open(messages_file, 'r') as f:
                messages = json.load(f)
        else:
            messages = []
        
        messages.append(message)
        
        # Guardar
        with open(messages_file, 'w') as f:
            json.dump(messages, f, indent=2)
    
    def get_group_messages(self, group_id):
        """Obtener mensajes de un grupo"""
        messages_file = self.data_dir / f'{group_id}_messages.json'
        
        if not messages_file.exists():
            return []
        
        with open(messages_file, 'r') as f:
            return json.load(f)
    
    def get_groups(self):
        """Obtener lista de grupos"""
        return list(self.groups.values())
    
    def get_group(self, group_id):
        """Obtener información de un grupo"""
        return self.groups.get(group_id)
    
    def delete_group(self, group_id):
        """Eliminar grupo (solo admin)"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        identity = self.crypto_manager.load_identity()
        
        if group['admin'] != identity['onion_address']:
            return False
        
        # Notificar a miembros
        self._broadcast_to_group(
            group_id,
            {
                'type': 'group_deleted',
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Eliminar archivos
        group_file = self.data_dir / f'{group_id}.json'
        messages_file = self.data_dir / f'{group_id}_messages.json'
        
        if group_file.exists():
            group_file.unlink()
        if messages_file.exists():
            messages_file.unlink()
        
        # Eliminar de memoria
        del self.groups[group_id]
        
        return True


class GroupCallManager:
    """
    Gestor de videollamadas grupales
    Maneja múltiples streams simultáneos
    """
    
    def __init__(self, video_stream, p2p_network, group_manager):
        self.video_stream = video_stream
        self.p2p_network = p2p_network
        self.group_manager = group_manager
        
        self.active_call = None
        self.participant_streams = {}
        
        # Thread pool para procesamiento paralelo de video
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def start_group_video_call(self, group_id):
        """Iniciar videollamada grupal"""
        call_id = self.group_manager.start_group_call(group_id)
        
        if not call_id:
            return False
        
        self.active_call = call_id
        
        # Iniciar stream de video
        self.video_stream.start()
        
        # Iniciar broadcast de video
        self._start_video_broadcast(group_id)
        
        return call_id
    
    def _start_video_broadcast(self, group_id):
        """Broadcast de video a todos los participantes"""
        def broadcast_loop():
            group = self.group_manager.get_group(group_id)
            
            while self.active_call:
                # Obtener frame
                frame = self.video_stream.get_encoded_frame()
                
                if frame:
                    # Enviar a todos en paralelo
                    futures = []
                    for member in group['members']:
                        future = self.executor.submit(
                            self.p2p_network.send_video_frame,
                            member,
                            frame
                        )
                        futures.append(future)
                    
                    # No esperar resultados para mantener fluidez
                
                time.sleep(1.0 / self.video_stream.fps)
        
        # Iniciar broadcast en thread separado
        threading.Thread(target=broadcast_loop, daemon=True).start()
    
    def receive_participant_frame(self, participant_address, frame_data):
        """Recibir frame de un participante"""
        # Decodificar frame
        from video_stream import VideoStream
        frame = VideoStream.decode_frame(frame_data)
        
        if frame is not None:
            self.participant_streams[participant_address] = frame
    
    def get_participant_frames(self):
        """Obtener frames de todos los participantes"""
        return self.participant_streams.copy()
    
    def end_group_call(self):
        """Terminar videollamada grupal"""
        if self.active_call:
            self.group_manager.leave_group_call(self.active_call)
            self.active_call = None
            self.video_stream.stop()
            self.participant_streams.clear()


if __name__ == '__main__':
    # Test básico
    print("=== Test de GroupManager ===\n")
    
    from crypto_manager import CryptoManager
    from tor_manager import TorManager
    from p2p_network import P2PNetwork
    
    # Setup
    crypto = CryptoManager()
    crypto.generate_keypair()
    
    tor = TorManager()
    if tor.start_tor():
        onion = tor.start_hidden_service()
        
        p2p = P2PNetwork(tor, crypto)
        p2p.start()
        
        # Crear manager de grupos
        group_mgr = GroupManager(crypto, p2p)
        
        # Crear grupo de prueba
        group_id = group_mgr.create_group(
            "Grupo de Prueba",
            ["test1.onion", "test2.onion", "test3.onion"]
        )
        
        print(f"Grupo creado: {group_id}")
        
        # Enviar mensaje al grupo
        group_mgr.send_group_message(group_id, "Hola a todos!")
        
        # Listar grupos
        print("\nGrupos:")
        for group in group_mgr.get_groups():
            print(f"- {group['name']}: {len(group['members'])} miembros")
