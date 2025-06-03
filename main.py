from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import sqlite3
import time
import threading
import os
import random

# Simulación de datos de red para demostración
class NetworkSimulator:
    def __init__(self):
        self.base_rx = random.randint(100000000, 500000000)  # 100-500 MB
        self.base_tx = random.randint(50000000, 200000000)   # 50-200 MB
        self.last_rx = self.base_rx
        self.last_tx = self.base_tx
        
    def get_usage(self):
        # Simular incremento gradual de datos
        increment_rx = random.randint(1000, 50000)  # 1-50 KB por segundo
        increment_tx = random.randint(500, 25000)   # 0.5-25 KB por segundo
        
        self.last_rx += increment_rx
        self.last_tx += increment_tx
        
        return self.last_rx, self.last_tx

class DataMonitorApp(App):
    def __init__(self):
        super().__init__()
        self.title = "Monitor de Datos Móviles"
        self.dark_mode = False
        self.monitoring = False
        self.initial_quota_bytes = 0
        self.consumed_bytes = 0
        self.download_speed = 0
        self.upload_speed = 0
        self.remaining_quota = 0
        self.network_sim = NetworkSimulator()
        self.init_database()
        
    def init_database(self):
        """Inicializar base de datos SQLite"""
        self.db_path = "monitor_datos.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de configuración
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value REAL
            )
        """)
        
        # Tabla de datos de consumo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datos (
                timestamp INTEGER,
                rx_bytes INTEGER,
                tx_bytes INTEGER,
                consumed_bytes INTEGER,
                remaining_quota_bytes INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def format_bytes(self, bytes_val, unit='MB'):
        """Formatear bytes a MB o GB"""
        if bytes_val is None or bytes_val < 0:
            return "0.00"
        
        if unit == 'MB':
            return f"{bytes_val / (1024 * 1024):.2f}"
        elif unit == 'GB':
            return f"{bytes_val / (1024 * 1024 * 1024):.2f}"
        return str(bytes_val)
    
    def set_theme(self, dark_mode):
        """Cambiar entre tema claro y oscuro"""
        self.dark_mode = dark_mode
        
        if dark_mode:
            # Tema oscuro con colores vivos
            Window.clearcolor = get_color_from_hex('#121212')
            self.bg_color = '#1e1e1e'
            self.text_color = '#ffffff'
            self.accent_color = '#00ff88'  # Verde brillante
            self.secondary_color = '#ff6b35'  # Naranja brillante
            self.button_color = '#2d2d2d'
        else:
            # Tema claro con colores vivos
            Window.clearcolor = get_color_from_hex('#f8f9fa')
            self.bg_color = '#ffffff'
            self.text_color = '#2c3e50'
            self.accent_color = '#e74c3c'  # Rojo brillante
            self.secondary_color = '#3498db'  # Azul brillante
            self.button_color = '#ecf0f1'
    
    def build(self):
        """Construir la interfaz de usuario"""
        self.set_theme(False)  # Iniciar con tema claro
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=12)
        
        # Header con título y switch de tema
        header = BoxLayout(orientation='horizontal', size_hint_y=0.08)
        
        title = Label(
            text='📱 Monitor de Datos',
            font_size='22sp',
            bold=True,
            color=get_color_from_hex(self.accent_color),
            size_hint_x=0.7
        )
        
        # Control de tema
        theme_layout = BoxLayout(orientation='horizontal', size_hint_x=0.3)
        theme_icon = Label(text='🌙', font_size='18sp', size_hint_x=0.4)
        self.theme_switch = Switch(size_hint_x=0.6)
        self.theme_switch.bind(active=self.on_theme_switch)
        
        theme_layout.add_widget(theme_icon)
        theme_layout.add_widget(self.theme_switch)
        
        header.add_widget(title)
        header.add_widget(theme_layout)
        main_layout.add_widget(header)
        
        # Configuración de cuota inicial
        quota_section = BoxLayout(orientation='vertical', size_hint_y=0.12, spacing=5)
        quota_title = Label(text='💾 Configurar Cuota Inicial', font_size='16sp', bold=True)
        
        quota_input_layout = BoxLayout(orientation='horizontal', spacing=8)
        self.quota_input = TextInput(
            hint_text='Ej: 2.5',
            input_filter='float',
            multiline=False,
            font_size='16sp',
            size_hint_x=0.4
        )
        
        unit_layout = BoxLayout(orientation='horizontal', size_hint_x=0.3, spacing=5)
        self.gb_btn = Button(text='GB', font_size='14sp', background_color=get_color_from_hex(self.accent_color))
        self.mb_btn = Button(text='MB', font_size='14sp', background_color=get_color_from_hex(self.button_color))
        self.selected_unit = 'GB'
        
        self.gb_btn.bind(on_press=lambda x: self.select_unit('GB'))
        self.mb_btn.bind(on_press=lambda x: self.select_unit('MB'))
        
        unit_layout.add_widget(self.gb_btn)
        unit_layout.add_widget(self.mb_btn)
        
        set_btn = Button(
            text='Establecer',
            font_size='14sp',
            background_color=get_color_from_hex(self.secondary_color),
            size_hint_x=0.3
        )
        set_btn.bind(on_press=self.set_quota)
        
        quota_input_layout.add_widget(self.quota_input)
        quota_input_layout.add_widget(unit_layout)
        quota_input_layout.add_widget(set_btn)
        
        quota_section.add_widget(quota_title)
        quota_section.add_widget(quota_input_layout)
        main_layout.add_widget(quota_section)
        
        # Display principal - Saldo restante
        remaining_section = BoxLayout(orientation='vertical', size_hint_y=0.18)
        remaining_title = Label(text='📊 Saldo Restante', font_size='16sp', bold=True)
        self.remaining_label = Label(
            text='0.00 GB',
            font_size='36sp',
            bold=True,
            color=get_color_from_hex(self.accent_color)
        )
        
        remaining_section.add_widget(remaining_title)
        remaining_section.add_widget(self.remaining_label)
        main_layout.add_widget(remaining_section)
        
        # Estadísticas en tiempo real
        stats_layout = GridLayout(cols=2, size_hint_y=0.25, spacing=10)
        
        # Consumido total
        consumed_section = BoxLayout(orientation='vertical')
        consumed_title = Label(text='📈 Consumido Total', font_size='14sp', bold=True)
        self.consumed_label = Label(text='0.00 MB', font_size='20sp', bold=True)
        consumed_section.add_widget(consumed_title)
        consumed_section.add_widget(self.consumed_label)
        
        # Cuota inicial
        quota_section = BoxLayout(orientation='vertical')
        quota_title = Label(text='💽 Cuota Inicial', font_size='14sp', bold=True)
        self.quota_display = Label(text='No configurada', font_size='16sp')
        quota_section.add_widget(quota_title)
        quota_section.add_widget(self.quota_display)
        
        stats_layout.add_widget(consumed_section)
        stats_layout.add_widget(quota_section)
        main_layout.add_widget(stats_layout)
        
        # Velocidades en tiempo real
        speed_layout = GridLayout(cols=2, size_hint_y=0.22, spacing=10)
        
        # Velocidad de descarga
        download_section = BoxLayout(orientation='vertical')
        download_title = Label(text='⬇️ Descarga', font_size='14sp', bold=True)
        self.download_label = Label(
            text='0.00 MB/s',
            font_size='18sp',
            bold=True,
            color=get_color_from_hex('#00ff88')
        )
        download_section.add_widget(download_title)
        download_section.add_widget(self.download_label)
        
        # Velocidad de subida
        upload_section = BoxLayout(orientation='vertical')
        upload_title = Label(text='⬆️ Subida', font_size='14sp', bold=True)
        self.upload_label = Label(
            text='0.00 MB/s',
            font_size='18sp',
            bold=True,
            color=get_color_from_hex('#ff6b35')
        )
        upload_section.add_widget(upload_title)
        upload_section.add_widget(self.upload_label)
        
        speed_layout.add_widget(download_section)
        speed_layout.add_widget(upload_section)
        main_layout.add_widget(speed_layout)
        
        # Botones de control
        control_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
        
        self.monitor_btn = Button(
            text='▶️ Iniciar Monitoreo',
            font_size='16sp',
            bold=True,
            background_color=get_color_from_hex('#00ff88')
        )
        self.monitor_btn.bind(on_press=self.toggle_monitoring)
        
        reset_btn = Button(
            text='🔄 Reiniciar',
            font_size='16sp',
            background_color=get_color_from_hex('#ff6b35')
        )
        reset_btn.bind(on_press=self.reset_data)
        
        control_layout.add_widget(self.monitor_btn)
        control_layout.add_widget(reset_btn)
        main_layout.add_widget(control_layout)
        
        # Cargar configuración guardada
        self.load_saved_config()
        
        return main_layout
    
    def select_unit(self, unit):
        """Seleccionar unidad GB o MB"""
        self.selected_unit = unit
        if unit == 'GB':
            self.gb_btn.background_color = get_color_from_hex(self.accent_color)
            self.mb_btn.background_color = get_color_from_hex(self.button_color)
        else:
            self.mb_btn.background_color = get_color_from_hex(self.accent_color)
            self.gb_btn.background_color = get_color_from_hex(self.button_color)
    
    def on_theme_switch(self, instance, value):
        """Manejar cambio de tema"""
        self.set_theme(value)
        # Actualizar colores de botones activos
        self.select_unit(self.selected_unit)
        self.update_remaining_color()
    
    def set_quota(self, instance):
        """Establecer cuota inicial"""
        try:
            quota_value = float(self.quota_input.text)
            if quota_value <= 0:
                return
            
            # Convertir a bytes según la unidad seleccionada
            if self.selected_unit == 'GB':
                self.initial_quota_bytes = quota_value * 1024 * 1024 * 1024
                display_text = f"{quota_value} GB"
            else:  # MB
                self.initial_quota_bytes = quota_value * 1024 * 1024
                display_text = f"{quota_value} MB"
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                         ("initial_quota_bytes", self.initial_quota_bytes))
            cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                         ("quota_display", display_text))
            conn.commit()
            conn.close()
            
            # Actualizar display
            self.remaining_quota = self.initial_quota_bytes
            self.quota_display.text = display_text
            self.update_display()
            
        except ValueError:
            pass
    
    def load_saved_config(self):
        """Cargar configuración guardada"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Cargar cuota inicial
            cursor.execute("SELECT value FROM config WHERE key = 'initial_quota_bytes'")
            result = cursor.fetchone()
            if result:
                self.initial_quota_bytes = result[0]
                self.remaining_quota = self.initial_quota_bytes
            
            # Cargar texto de display
            cursor.execute("SELECT value FROM config WHERE key = 'quota_display'")
            result = cursor.fetchone()
            if result:
                self.quota_display.text = result[0]
            
            conn.close()
            self.update_display()
        except:
            pass
    
    def toggle_monitoring(self, instance):
        """Iniciar/detener monitoreo"""
        if not self.monitoring:
            if self.initial_quota_bytes <= 0:
                return
            
            self.monitoring = True
            self.monitor_btn.text = "⏸️ Detener Monitoreo"
            self.monitor_btn.background_color = get_color_from_hex('#ff6b35')
            
            # Reiniciar simulador de red
            self.network_sim = NetworkSimulator()
            self.rx_start, self.tx_start = self.network_sim.get_usage()
            self.rx_prev, self.tx_prev = self.rx_start, self.tx_start
            self.last_time = time.time()
            
            # Programar actualizaciones
            Clock.schedule_interval(self.update_monitoring, 1)
        else:
            self.monitoring = False
            self.monitor_btn.text = "▶️ Iniciar Monitoreo"
            self.monitor_btn.background_color = get_color_from_hex('#00ff88')
            Clock.unschedule(self.update_monitoring)
    
    def update_monitoring(self, dt):
        """Actualizar datos de monitoreo en tiempo real"""
        if not self.monitoring:
            return False
        
        current_time = time.time()
        rx_current, tx_current = self.network_sim.get_usage()
        
        time_diff = current_time - self.last_time
        if time_diff > 0:
            # Calcular velocidades
            self.download_speed = (rx_current - self.rx_prev) / time_diff
            self.upload_speed = (tx_current - self.tx_prev) / time_diff
            
            # Calcular consumo total
            total_download = rx_current - self.rx_start
            total_upload = tx_current - self.tx_start
            self.consumed_bytes = total_download + total_upload
            
            # Calcular saldo restante con descuento automático
            self.remaining_quota = max(0, self.initial_quota_bytes - self.consumed_bytes)
            
            # Guardar en base de datos
            self.save_data_point(rx_current, tx_current)
            
            # Actualizar display
            self.update_display()
            
            # Alerta de cuota baja
            self.check_low_quota_alert()
            
            self.rx_prev, self.tx_prev = rx_current, tx_current
            self.last_time = current_time
    
    def save_data_point(self, rx_bytes, tx_bytes):
        """Guardar punto de datos en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            timestamp = int(time.time())
            cursor.execute("""
                INSERT INTO datos (timestamp, rx_bytes, tx_bytes, consumed_bytes, remaining_quota_bytes)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, rx_bytes, tx_bytes, self.consumed_bytes, self.remaining_quota))
            conn.commit()
            conn.close()
        except:
            pass
    
    def check_low_quota_alert(self):
        """Verificar y mostrar alerta de cuota baja"""
        if self.remaining_quota < 0.1 * 1024 * 1024 * 1024:  # Menos de 100MB
            # En una aplicación real, aquí se mostraría una notificación push
            print(f"¡ALERTA! Saldo restante: {self.format_bytes(self.remaining_quota, 'GB')} GB")
    
    def update_display(self, dt=None):
        """Actualizar pantalla con datos actuales"""
        # Actualizar saldo restante
        self.remaining_label.text = f"{self.format_bytes(self.remaining_quota, 'GB')} GB"
        
        # Actualizar consumo total
        self.consumed_label.text = f"{self.format_bytes(self.consumed_bytes, 'MB')} MB"
        
        # Actualizar velocidades
        self.download_label.text = f"{self.format_bytes(self.download_speed, 'MB')}/s"
        self.upload_label.text = f"{self.format_bytes(self.upload_speed, 'MB')}/s"
        
        # Actualizar color del saldo según el nivel
        self.update_remaining_color()
    
    def update_remaining_color(self):
        """Actualizar color del saldo restante según el nivel"""
        if self.remaining_quota < 0.1 * 1024 * 1024 * 1024:  # < 100MB
            self.remaining_label.color = get_color_from_hex('#ff4444')
        elif self.remaining_quota < 0.5 * 1024 * 1024 * 1024:  # < 500MB
            self.remaining_label.color = get_color_from_hex('#ffaa00')
        else:
            self.remaining_label.color = get_color_from_hex(self.accent_color)
    
    def reset_data(self, instance):
        """Reiniciar datos de consumo"""
        if self.monitoring:
            return  # No permitir reset durante monitoreo activo
        
        self.consumed_bytes = 0
        self.remaining_quota = self.initial_quota_bytes
        self.download_speed = 0
        self.upload_speed = 0
        self.update_display()

if __name__ == '__main__':
    DataMonitorApp().run()

