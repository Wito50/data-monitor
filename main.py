# main.py
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDInputDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDFlatButton
import sqlite3, os, time

KV = '''
MDScreen:
    md_bg_color: app.theme_cls.bg_normal

    MDTopAppBar:
        title: "Monitor de Datos"
        elevation: 4
        left_action_items: [["menu", lambda x: app.toggle_theme()]]

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(10)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDLabel:
            text: f"Saldo Inicial: {app.get_saldo_str()}"
            halign: "center"
            theme_text_color: "Primary"

        MDRaisedButton:
            text: "Ver Uso de Hoy"
            on_release: app.ver_uso_hoy()

        MDRaisedButton:
            text: "Reiniciar Datos de Hoy"
            on_release: app.reset_hoy()

        MDRaisedButton:
            text: "Configurar Saldo Inicial"
            on_release: app.set_saldo()

        MDRaisedButton:
            text: "Tomar Instantánea"
            on_release: app.take_snapshot()

        MDRaisedButton:
            text: "Cambiar Tema"
            on_release: app.toggle_theme()
'''

class MonitorApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.store = JsonStore("config.json")
        self.db_path = os.path.join(self.user_data_dir, "datos.db")
        self.ensure_db()
        return Builder.load_string(KV)

    def ensure_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datos (
                timestamp INTEGER,
                interfaz TEXT,
                rx_bytes INTEGER,
                tx_bytes INTEGER,
                remaining_quota_bytes INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def get_saldo(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = 'initial_quota_gb'")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0

    def get_saldo_str(self):
        gb = self.get_saldo()
        return f"{gb:.2f} GB" if gb else "No configurado"

    def set_saldo(self):
        def on_confirm(instance, value):
            try:
                val = float(value)
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", ("initial_quota_gb", val))
                conn.commit()
                conn.close()
                Snackbar(text="✅ Saldo configurado").open()
            except:
                Snackbar(text="❌ Valor inválido").open()

        self.dialog = MDInputDialog(
            title="Saldo Inicial (GB)",
            hint_text="Ej: 2.5",
            text_button_ok="Guardar",
            callback=on_confirm
        )
        self.dialog.open()

    def ver_uso_hoy(self):
        Snackbar(text="📊 Uso de hoy: No disponible en Android aún.").open()

    def reset_hoy(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = time.strftime("%Y-%m-%d")
        ts_start = int(time.mktime(time.strptime(today, "%Y-%m-%d")))
        ts_end = ts_start + 86400
        cursor.execute("DELETE FROM datos WHERE timestamp >= ? AND timestamp < ?", (ts_start, ts_end))
        conn.commit()
        conn.close()
        Snackbar(text="🔁 Datos de hoy reiniciados").open()

    def take_snapshot(self):
        ts = int(time.time())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO datos (timestamp, interfaz, rx_bytes, tx_bytes, remaining_quota_bytes) VALUES (?, ?, ?, ?, ?)",
                       (ts, "android", 0, 0, self.get_saldo() * 1024 * 1024 * 1024))
        conn.commit()
        conn.close()
        Snackbar(text="✅ Snapshot guardado").open()

    def toggle_theme(self):
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"