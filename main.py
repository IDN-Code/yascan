"""
Yascan - Aplicación de Chat Seguro
Versión Básica con Encriptación AES-256
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

import sys
import os

# Importar gestores
sys.path.insert(0, os.path.dirname(__file__))

from crypto_manager import CryptoManager, generate_identity_id
from tor_manager import TorManager
from p2p_network import P2PNetwork

class YascanApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crypto = CryptoManager()
        self.tor = None
        self.network = None
        self.identity_id = None
        
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Título
        title = Label(
            text='[b]YASCAN[/b]\nChat Seguro con Encriptación AES-256',
            markup=True,
            size_hint=(1, 0.15),
            font_size='20sp'
        )
        layout.add_widget(title)
        
        # Estado
        self.status_label = Label(
            text='Estado: Inicializando...',
            size_hint=(1, 0.1),
            font_size='14sp'
        )
        layout.add_widget(self.status_label)
        
        # Identidad
        identity_box = BoxLayout(size_hint=(1, 0.15), spacing=5)
        identity_box.add_widget(Label(text='Tu ID:', size_hint=(0.3, 1)))
        
        self.identity_input = TextInput(
            text='',
            readonly=True,
            size_hint=(0.7, 1)
        )
        identity_box.add_widget(self.identity_input)
        layout.add_widget(identity_box)
        
        # Botón generar identidad
        btn_generate = Button(
            text='Generar Nueva Identidad',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 0.2, 1)
        )
        btn_generate.bind(on_press=self.generate_identity)
        layout.add_widget(btn_generate)
        
        # Área de chat
        scroll = ScrollView(size_hint=(1, 0.4))
        self.chat_label = Label(
            text='Bienvenido a Yascan\n\nChat seguro con:\n✓ Encriptación AES-256\n✓ Conexión Tor\n✓ Sin servidores centrales\n\nGenera tu identidad para comenzar.',
            size_hint_y=None,
            markup=True
        )
        self.chat_label.bind(texture_size=self.chat_label.setter('size'))
        scroll.add_widget(self.chat_label)
        layout.add_widget(scroll)
        
        # Info
        info = Label(
            text='Yascan v1.0 - Versión Básica\nEncriptación: AES-256 + ECDSA',
            size_hint=(1, 0.1),
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(info)
        
        # Inicializar
        self.update_status('Listo. Genera una identidad para comenzar.')
        
        return layout
    
    def generate_identity(self, instance):
        """Genera nueva identidad criptográfica"""
        try:
            self.update_status('Generando identidad...')
            
            # Generar claves
            self.identity_id = generate_identity_id()
            public_key = self.crypto.generate_keypair()
            
            # Mostrar ID
            self.identity_input.text = self.identity_id
            
            # Actualizar chat
            self.add_message(f'[color=00ff00]✓ Identidad generada[/color]')
            self.add_message(f'Tu ID: {self.identity_id}')
            self.add_message(f'Clave pública: {public_key[:32]}...')
            
            self.update_status('Identidad generada. Lista para usar.')
            
        except Exception as e:
            self.update_status(f'Error: {str(e)}')
            self.add_message(f'[color=ff0000]Error generando identidad: {str(e)}[/color]')
    
    def update_status(self, message):
        """Actualiza mensaje de estado"""
        self.status_label.text = f'Estado: {message}'
    
    def add_message(self, message):
        """Agrega mensaje al chat"""
        current = self.chat_label.text
        self.chat_label.text = f'{current}\n{message}'

if __name__ == '__main__':
    YascanApp().run()
