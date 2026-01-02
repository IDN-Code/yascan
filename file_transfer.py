"""
Módulo de Transferencia de Archivos
Envío de archivos encriptados por chunks en paralelo
"""

import os
import hashlib
import base64
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
import time


class FileTransferManager:
    """Gestor de transferencia de archivos encriptados"""
    
    def __init__(self, crypto_manager, p2p_network):
        self.crypto_manager = crypto_manager
        self.p2p_network = p2p_network
        
        self.data_dir = Path.home() / '.deepchat' / 'file_transfers'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Transferencias activas
        self.active_transfers = {}
        self.received_chunks = {}
        
        # Thread pool para procesamiento paralelo
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Configuración
        self.chunk_size = 64 * 1024  # 64 KB por chunk
        self.max_file_size = 100 * 1024 * 1024  # 100 MB máximo
    
    def send_file(self, file_path, recipient_address, progress_callback=None):
        """
        Enviar archivo encriptado en chunks paralelos
        
        Args:
            file_path: Ruta del archivo a enviar
            recipient_address: Dirección .onion del destinatario
            progress_callback: Función para reportar progreso
            
        Returns:
            ID de la transferencia
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        file_size = file_path.stat().st_size
        
        if file_size > self.max_file_size:
            raise ValueError(f"Archivo muy grande. Máximo: {self.max_file_size / 1024 / 1024} MB")
        
        # Generar ID de transferencia
        transfer_id = hashlib.sha256(
            f"{file_path}{recipient_address}{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Calcular checksum del archivo
        file_checksum = self._calculate_file_checksum(file_path)
        
        # Dividir archivo en chunks
        chunks = self._split_file_to_chunks(file_path)
        total_chunks = len(chunks)
        
        print(f"Archivo dividido en {total_chunks} chunks de {self.chunk_size / 1024:.1f} KB")
        
        # Crear metadata
        metadata = {
            'transfer_id': transfer_id,
            'filename': file_path.name,
            'file_size': file_size,
            'total_chunks': total_chunks,
            'checksum': file_checksum,
            'sender': self.crypto_manager.load_identity()['onion_address'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Guardar info de transferencia
        self.active_transfers[transfer_id] = {
            'metadata': metadata,
            'recipient': recipient_address,
            'chunks_sent': 0,
            'status': 'sending'
        }
        
        # Enviar metadata primero
        self._send_file_metadata(recipient_address, metadata)
        
        # Enviar chunks en paralelo
        self._send_chunks_parallel(
            chunks,
            recipient_address,
            transfer_id,
            progress_callback
        )
        
        return transfer_id
    
    def _split_file_to_chunks(self, file_path):
        """
        Dividir archivo en chunks
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Lista de chunks (bytes)
        """
        chunks = []
        
        with open(file_path, 'rb') as f:
            chunk_index = 0
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                
                chunks.append({
                    'index': chunk_index,
                    'data': chunk
                })
                chunk_index += 1
        
        return chunks
    
    def _send_chunks_parallel(self, chunks, recipient, transfer_id, progress_callback):
        """
        Enviar chunks en paralelo usando ThreadPoolExecutor
        
        Args:
            chunks: Lista de chunks a enviar
            recipient: Dirección del destinatario
            transfer_id: ID de la transferencia
            progress_callback: Callback para reportar progreso
        """
        total_chunks = len(chunks)
        
        # Función para enviar un chunk individual
        def send_chunk(chunk):
            chunk_index = chunk['index']
            chunk_data = chunk['data']
            
            # Encriptar chunk
            encrypted_chunk = self._encrypt_chunk(chunk_data)
            
            # Crear paquete de chunk
            packet = {
                'type': 'file_chunk',
                'transfer_id': transfer_id,
                'chunk_index': chunk_index,
                'total_chunks': total_chunks,
                'data': base64.b64encode(encrypted_chunk).decode('utf-8'),
                'timestamp': datetime.now().isoformat()
            }
            
            # Enviar por P2P
            success = self.p2p_network.send_message(
                recipient,
                json.dumps(packet)
            )
            
            return success, chunk_index
        
        # Enviar todos los chunks en paralelo
        futures = []
        for chunk in chunks:
            future = self.executor.submit(send_chunk, chunk)
            futures.append(future)
        
        # Procesar resultados a medida que completan
        chunks_sent = 0
        for future in as_completed(futures):
            try:
                success, chunk_index = future.result()
                
                if success:
                    chunks_sent += 1
                    
                    # Actualizar progreso
                    self.active_transfers[transfer_id]['chunks_sent'] = chunks_sent
                    
                    # Callback de progreso
                    if progress_callback:
                        progress = (chunks_sent / total_chunks) * 100
                        progress_callback(progress)
                    
                    print(f"Chunk {chunk_index + 1}/{total_chunks} enviado ({chunks_sent}/{total_chunks})")
                
            except Exception as e:
                print(f"Error enviando chunk: {e}")
        
        # Marcar como completado
        if chunks_sent == total_chunks:
            self.active_transfers[transfer_id]['status'] = 'completed'
            
            # Enviar señal de finalización
            self._send_transfer_complete(recipient, transfer_id)
            
            print(f"✅ Transferencia {transfer_id} completada: {chunks_sent}/{total_chunks} chunks")
        else:
            self.active_transfers[transfer_id]['status'] = 'failed'
            print(f"❌ Transferencia {transfer_id} falló: {chunks_sent}/{total_chunks} chunks")
    
    def _encrypt_chunk(self, chunk_data):
        """
        Encriptar chunk de datos
        
        Args:
            chunk_data: Datos a encriptar
            
        Returns:
            Datos encriptados
        """
        from cryptography.fernet import Fernet
        
        # Generar clave temporal para el chunk
        key = Fernet.generate_key()
        fernet = Fernet(key)
        
        encrypted = fernet.encrypt(chunk_data)
        
        # Encriptar la clave con RSA
        # TODO: Usar clave pública del destinatario
        
        return encrypted
    
    def _send_file_metadata(self, recipient, metadata):
        """Enviar metadata del archivo"""
        packet = {
            'type': 'file_metadata',
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        self.p2p_network.send_message(
            recipient,
            json.dumps(packet)
        )
    
    def _send_transfer_complete(self, recipient, transfer_id):
        """Enviar señal de transferencia completa"""
        packet = {
            'type': 'transfer_complete',
            'transfer_id': transfer_id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.p2p_network.send_message(
            recipient,
            json.dumps(packet)
        )
    
    def receive_file_metadata(self, metadata):
        """
        Procesar metadata de archivo entrante
        
        Args:
            metadata: Diccionario con metadata del archivo
        """
        transfer_id = metadata['transfer_id']
        
        # Preparar para recibir chunks
        self.received_chunks[transfer_id] = {
            'metadata': metadata,
            'chunks': {},
            'received_count': 0,
            'status': 'receiving'
        }
        
        print(f"📥 Recibiendo archivo: {metadata['filename']} ({metadata['file_size'] / 1024:.1f} KB)")
    
    def receive_chunk(self, packet):
        """
        Recibir y procesar chunk de archivo
        
        Args:
            packet: Paquete con chunk de datos
        """
        transfer_id = packet['transfer_id']
        chunk_index = packet['chunk_index']
        total_chunks = packet['total_chunks']
        encrypted_data = base64.b64decode(packet['data'])
        
        if transfer_id not in self.received_chunks:
            print(f"Advertencia: Chunk recibido sin metadata: {transfer_id}")
            return
        
        # Desencriptar chunk
        chunk_data = self._decrypt_chunk(encrypted_data)
        
        # Guardar chunk
        transfer_info = self.received_chunks[transfer_id]
        transfer_info['chunks'][chunk_index] = chunk_data
        transfer_info['received_count'] += 1
        
        received = transfer_info['received_count']
        progress = (received / total_chunks) * 100
        
        print(f"📦 Chunk {chunk_index + 1}/{total_chunks} recibido ({progress:.1f}%)")
        
        # Si recibimos todos los chunks, ensamblar archivo
        if received == total_chunks:
            self._assemble_file(transfer_id)
    
    def _decrypt_chunk(self, encrypted_data):
        """Desencriptar chunk"""
        from cryptography.fernet import Fernet
        
        # TODO: Implementar desencriptación correcta con RSA
        # Por ahora, retornar sin desencriptar
        return encrypted_data
    
    def _assemble_file(self, transfer_id):
        """
        Ensamblar archivo desde chunks recibidos
        
        Args:
            transfer_id: ID de la transferencia
        """
        transfer_info = self.received_chunks[transfer_id]
        metadata = transfer_info['metadata']
        chunks = transfer_info['chunks']
        
        # Ordenar chunks por índice
        sorted_chunks = [chunks[i] for i in sorted(chunks.keys())]
        
        # Ensamblar archivo
        file_data = b''.join(sorted_chunks)
        
        # Verificar checksum
        received_checksum = hashlib.sha256(file_data).hexdigest()
        
        if received_checksum != metadata['checksum']:
            print(f"❌ Error: Checksum no coincide para {metadata['filename']}")
            transfer_info['status'] = 'failed'
            return
        
        # Guardar archivo
        output_path = self.data_dir / metadata['filename']
        
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        transfer_info['status'] = 'completed'
        transfer_info['output_path'] = str(output_path)
        
        print(f"✅ Archivo recibido: {output_path}")
        print(f"   Tamaño: {len(file_data) / 1024:.1f} KB")
        print(f"   Checksum verificado: {received_checksum[:16]}...")
    
    def _calculate_file_checksum(self, file_path):
        """Calcular SHA-256 checksum de un archivo"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)  # 64 KB
                if not data:
                    break
                sha256.update(data)
        
        return sha256.hexdigest()
    
    def get_transfer_status(self, transfer_id):
        """Obtener estado de una transferencia"""
        if transfer_id in self.active_transfers:
            return self.active_transfers[transfer_id]
        elif transfer_id in self.received_chunks:
            return self.received_chunks[transfer_id]
        else:
            return None
    
    def cancel_transfer(self, transfer_id):
        """Cancelar transferencia"""
        if transfer_id in self.active_transfers:
            self.active_transfers[transfer_id]['status'] = 'cancelled'
            return True
        return False
    
    def get_active_transfers(self):
        """Obtener lista de transferencias activas"""
        transfers = []
        
        # Transferencias salientes
        for tid, info in self.active_transfers.items():
            transfers.append({
                'id': tid,
                'type': 'outgoing',
                **info
            })
        
        # Transferencias entrantes
        for tid, info in self.received_chunks.items():
            transfers.append({
                'id': tid,
                'type': 'incoming',
                **info
            })
        
        return transfers


class StreamingFileTransfer:
    """
    Transferencia de archivos con streaming
    Optimizado para archivos grandes con Server-Sent Events
    """
    
    def __init__(self, crypto_manager, p2p_network):
        self.crypto_manager = crypto_manager
        self.p2p_network = p2p_network
        self.chunk_size = 32 * 1024  # 32 KB
    
    def stream_file_send(self, file_path, recipient):
        """
        Enviar archivo usando streaming (generator)
        
        Yields:
            Chunks de progreso
        """
        file_path = Path(file_path)
        file_size = file_path.stat().st_size
        bytes_sent = 0
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                
                # Encriptar y enviar
                # TODO: Implementar encriptación
                
                bytes_sent += len(chunk)
                progress = (bytes_sent / file_size) * 100
                
                yield {
                    'bytes_sent': bytes_sent,
                    'file_size': file_size,
                    'progress': progress
                }
        
        yield {'status': 'completed'}


# Integración con grupos para envío masivo
class GroupFileTransfer:
    """Envío de archivos a grupos"""
    
    def __init__(self, file_manager, group_manager):
        self.file_manager = file_manager
        self.group_manager = group_manager
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def send_file_to_group(self, group_id, file_path, progress_callback=None):
        """
        Enviar archivo a todos los miembros del grupo en paralelo
        
        Args:
            group_id: ID del grupo
            file_path: Ruta del archivo
            progress_callback: Callback para progreso global
            
        Returns:
            Diccionario con resultados por miembro
        """
        group = self.group_manager.get_group(group_id)
        
        if not group:
            return None
        
        my_address = self.file_manager.crypto_manager.load_identity()['onion_address']
        members = [m for m in group['members'] if m != my_address]
        
        print(f"Enviando archivo a {len(members)} miembros del grupo...")
        
        # Función para enviar a un miembro
        def send_to_member(member_address):
            try:
                transfer_id = self.file_manager.send_file(
                    file_path,
                    member_address
                )
                return member_address, True, transfer_id
            except Exception as e:
                print(f"Error enviando a {member_address[:20]}...: {e}")
                return member_address, False, None
        
        # Enviar a todos en paralelo
        futures = []
        for member in members:
            future = self.executor.submit(send_to_member, member)
            futures.append(future)
        
        # Recolectar resultados
        results = {}
        successful = 0
        
        for future in as_completed(futures):
            member, success, transfer_id = future.result()
            results[member] = {
                'success': success,
                'transfer_id': transfer_id
            }
            
            if success:
                successful += 1
            
            if progress_callback:
                progress = (successful / len(members)) * 100
                progress_callback(progress)
        
        print(f"✅ Archivo enviado a {successful}/{len(members)} miembros")
        
        return results


if __name__ == '__main__':
    # Test de transferencia de archivos
    print("=== Test de FileTransferManager ===\n")
    
    from crypto_manager import CryptoManager
    from tor_manager import TorManager
    from p2p_network import P2PNetwork
    
    # Setup
    crypto = CryptoManager()
    crypto.generate_keypair()
    
    tor = TorManager()
    p2p = P2PNetwork(tor, crypto)
    
    # Crear manager
    file_mgr = FileTransferManager(crypto, p2p)
    
    # Crear archivo de prueba
    test_file = Path('/tmp/test_file.txt')
    test_file.write_text("Este es un archivo de prueba para transferencia encriptada")
    
    print(f"Archivo de prueba creado: {test_file}")
    print(f"Tamaño: {test_file.stat().st_size} bytes\n")
    
    # Simular envío
    def progress(percent):
        print(f"Progreso: {percent:.1f}%")
    
    transfer_id = file_mgr.send_file(
        test_file,
        "test.onion",
        progress_callback=progress
    )
    
    print(f"\nTransfer ID: {transfer_id}")
