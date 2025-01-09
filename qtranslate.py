import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QScrollBar,
    QMessageBox,
    QMenu,
    QSystemTrayIcon,
    QDialog,
    QLabel,
    QComboBox,
    QSpinBox,
    QDialogButtonBox,
    QFormLayout
)
from PySide6.QtCore import Qt, QObject, Signal, Slot, QSettings
from PySide6.QtGui import QCursor, QIcon, QAction
from googletrans import Translator, LANGUAGES
import pyperclip
import logging
import keyboard
import time
import win32gui
import win32process

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SettingsDialog(QDialog):
    """Диалог настроек."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.settings = QSettings("QuickTranslate", "Translator")  # Инициализируем QSettings

        # Создаем выпадающие списки для выбора языка
        self.source_lang_combo = QComboBox()
        self.dest_lang_combo = QComboBox()
        for lang_code, lang_name in LANGUAGES.items():
            self.source_lang_combo.addItem(f"{lang_name} ({lang_code})", lang_code)
            self.dest_lang_combo.addItem(f"{lang_name} ({lang_code})", lang_code)

        # Создаем спинбоксы для настройки размера окна
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(100, 1000)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(50, 1000)
        
         # Создаем спинбоксы для настройки горячих клавиш
        self.hotkey_input = QTextEdit()
        self.hotkey_input.setFixedHeight(25)
        self.hotkey_input.setReadOnly(True)
        
        # Инициализируем значения на основе сохраненных настроек
        self.load_settings()

        # Создаем форму для настроек
        form_layout = QFormLayout()
        form_layout.addRow("Исходный язык:", self.source_lang_combo)
        form_layout.addRow("Язык перевода:", self.dest_lang_combo)
        form_layout.addRow("Ширина окна:", self.width_spinbox)
        form_layout.addRow("Высота окна:", self.height_spinbox)
        form_layout.addRow("Сочетание клавиш:", self.hotkey_input)

        # Кнопки OK и Отмена
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Общий макет
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
        
        # подключаем обработчик нажатия на текстовое поле
        self.hotkey_input.mousePressEvent = self.set_hotkey_input

    def load_settings(self):
        """Загружает настройки из QSettings."""
        # Загружаем сохраненные настройки или значения по умолчанию
        source_lang = self.settings.value("source_lang", "en")
        dest_lang = self.settings.value("dest_lang", "ru")
        window_width = self.settings.value("window_width", 300, type=int)
        window_height = self.settings.value("window_height", 120, type=int)
        hotkey = self.settings.value("hotkey", "ctrl+b")

        # Устанавливаем выбранные языки в выпадающих списках
        index = self.source_lang_combo.findData(source_lang)
        if index >= 0:
            self.source_lang_combo.setCurrentIndex(index)
        index = self.dest_lang_combo.findData(dest_lang)
        if index >= 0:
            self.dest_lang_combo.setCurrentIndex(index)

        # Устанавливаем сохраненные размеры окна
        self.width_spinbox.setValue(window_width)
        self.height_spinbox.setValue(window_height)
        
        #Устанавливаем сохраненную горячую клавишу
        self.hotkey_input.setText(hotkey)
        

    def save_settings(self):
        """Сохраняет настройки в QSettings."""
        # Сохраняем текущие настройки
        self.settings.setValue("source_lang", self.source_lang_combo.currentData())
        self.settings.setValue("dest_lang", self.dest_lang_combo.currentData())
        self.settings.setValue("window_width", self.width_spinbox.value())
        self.settings.setValue("window_height", self.height_spinbox.value())
        self.settings.setValue("hotkey", self.hotkey_input.toPlainText())

    def accept(self):
        """Обработка нажатия на кнопку 'OK'."""
        self.save_settings()
        super().accept()  # Закрываем диалог

    def get_settings(self):
        """Возвращает текущие настройки."""
        return {
            "source_lang": self.source_lang_combo.currentData(),
            "dest_lang": self.dest_lang_combo.currentData(),
            "window_width": self.width_spinbox.value(),
            "window_height": self.height_spinbox.value(),
            "hotkey": self.hotkey_input.toPlainText()
        }
    
    def set_hotkey_input(self, event):
        """Ожидает нажатия горячих клавиш для добавления в текстовое поле."""
        self.hotkey_input.clear()
        self.hotkey_input.setText("Нажмите сочетание клавиш...")
        def on_press(e):
            if e.event_type == keyboard.KEY_DOWN:
                hotkey_text = keyboard.get_hotkey_name(e)
                self.hotkey_input.setText(hotkey_text)
                keyboard.unhook(on_press)
        keyboard.hook(on_press)


class TranslatorApp(QWidget):
    translation_requested = Signal()
    close_requested = Signal()

    def __init__(self, source_lang='en', dest_lang='ru', window_width=300, window_height=120, hotkey="ctrl+b"):
        super().__init__()

        self.source_lang = source_lang
        self.dest_lang = dest_lang
        self.window_width = window_width
        self.window_height = window_height
        self.hotkey = hotkey
        self.translator = Translator()
        self.last_selected_text = ""
        self.user_buffer = ""
        self.is_window_active = False
        self.setWindowIcon(QIcon("extension.png"))
        self.setWindowTitle("QuickTranslate")
        self.setGeometry(100, 100, self.window_width, self.window_height)
        self.setWindowFlag(Qt.WindowStaysOnTopHint) # Окно всегда сверху

        self.initUI()
        self.initTrayIcon()
        logging.info("TranslatorApp initialized.")
        
        self.initHotkey(self.hotkey)

    def initUI(self):
        """Инициализация пользовательского интерфейса."""
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True) # текст только для чтения
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) # добавить скролбар
        self.text_edit.setMouseTracking(True)  # отслеживать положение мыши

        self.text_edit.mousePressEvent = self.text_clicked
        self.setLayout(layout)
        layout.addWidget(self.text_edit)
        logging.info("UI initialized.")

    def initTrayIcon(self):
        """Инициализация иконки в трее."""
        self.tray_icon = QSystemTrayIcon(QIcon("extension.png"), self)  # Укажите путь к вашей иконке
        self.tray_menu = QMenu()

        # Действие для открытия окна настроек
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.open_settings)
        self.tray_menu.addAction(settings_action)

         # Действие для показа окна
        show_action = QAction("Показать", self)
        show_action.triggered.connect(self.show)
        self.tray_menu.addAction(show_action)


        # Действие для выхода
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close_app)
        self.tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        logging.info("Tray icon initialized.")

    def translate_text(self, text):
        logging.info(f"Translating text: {text}")
        if text and isinstance(text, str):
            try:
                translation = self.translator.translate(text, src=self.source_lang, dest=self.dest_lang)
                logging.info(f"Translation successful: {translation.text}")
                return translation.text
            except Exception as e:
                logging.error(f"Error during translation: {e}")
                return f"Ошибка перевода: {e}"
        else:
            logging.warning("No text provided for translation or text is not string.")
            return None

    @Slot()
    def show_translation(self, selected_text):
        logging.info(f"Attempting to show translation for: {selected_text}")
        if selected_text and selected_text != self.last_selected_text:
            if self.is_foreign_text(selected_text):
                self.last_selected_text = selected_text
                translated_text = self.translate_text(selected_text)
                if translated_text:
                    self.text_edit.setText(translated_text)
                    self.show()  # Показать окно
                    self.adjust_window_position()  # Регулировать положение окна
            else:
                logging.info("Selected text is not in the source language.")
        else:
            logging.info("Selected text is same as last selected or is empty.")

    def adjust_window_position(self):
        """Регулировка положения окна под курсором мыши."""
        cursor_pos = QCursor.pos()  # Текущая позиция курсора
        self.move(cursor_pos.x() + 20, cursor_pos.y() - self.height() - 5)
        logging.info(f"Window position adjusted to: {cursor_pos.x() + 20}, {cursor_pos.y() - self.height() - 5}")

    def text_clicked(self, event):
        """Обработка клика мыши по тексту для копирования перевода."""
        translated_text = self.text_edit.toPlainText()
        if translated_text:
            self.copy_translation(translated_text)
        logging.info("Translation copied to clipboard.")
        time.sleep(1)
        self.hide()

    def copy_translation(self, translated_text):
        """Копирование перевода в буфер обмена."""
        logging.info(f"Copying translation to clipboard: {translated_text}")
        pyperclip.copy(translated_text)
        self.user_buffer = ""  # Очищаем, когда пользователь скопировал перевод

    def is_foreign_text(self, text):
        """Проверка, является ли текст иностранным."""
        logging.info(f"Checking if text is in source language: {text}")
        if text and isinstance(text, str):
            try:
                detected = self.translator.detect(text)
                if detected.lang == self.source_lang:
                    logging.info(f"Text is in source language: {self.source_lang}")
                    return True
                else:
                    logging.info(f"Text is not in source language, it's: {detected.lang}")
                    return False
            except Exception as e:
                logging.error(f"Error during language detection: {e}")
                return False
        else:
            logging.warning("No text provided for language detection or text is not a string.")
            return False

    @Slot()
    def translate_selected_text(self):
        """Получение выделенного текста и его перевод."""
        logging.info("Attempting to translate selected text.")
        try:
            self.user_buffer = pyperclip.paste()  # Сохраняем текущий буфер
            pyperclip.copy("")  # очищаем буфер обмена
            time.sleep(0.05)
            # Получаем текущее окно
            hwnd = win32gui.GetForegroundWindow()
            thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
            # Эмулируем Ctrl + C с помощью keyboard
            keyboard.press_and_release('ctrl+c')
            time.sleep(0.05)
            selected_text = pyperclip.paste()  # копируем выделенный текст
            # Возвращаем фокус в исходное окно
            if hwnd:
                win32gui.SetForegroundWindow(hwnd)
            if selected_text:
                self.show_translation(selected_text)
            else:
                logging.info("No text was selected.")
        except Exception as e:
            logging.error(f"Error during text selection or translation: {e}")
            if self.user_buffer:
                pyperclip.copy(self.user_buffer)
                self.user_buffer = ""
                logging.info("User's clipboard restored after an error.")

    def open_settings(self):
        """Открывает диалог настроек и применяет их."""
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec() == QDialog.Accepted:
            settings = settings_dialog.get_settings()
            logging.info(f"Settings dialog accepted, new settings: {settings}")

            # Изменяем параметры на новые
            self.source_lang = settings["source_lang"]
            self.dest_lang = settings["dest_lang"]
            self.window_width = settings["window_width"]
            self.window_height = settings["window_height"]
            self.hotkey = settings["hotkey"]

            # Обновляем размеры окна
            self.resize(self.window_width, self.window_height)
            #Переназначаем горячую клавишу
            self.initHotkey(self.hotkey)
            logging.info("Settings applied successfully.")

    def close_app(self):
        """Закрывает приложение."""
        logging.info("Application close requested.")
        self.tray_icon.hide()  # Скрываем иконку перед закрытием
        self.close()
    
    def initHotkey(self, hotkey):
        """Инициализирует горячую клавишу."""
        # Отключаем старую горячую клавишу
        keyboard.unhook_all()

        # Глобальный хук для обработки Ctrl+B и ESC (работает во всех приложениях)
        def on_hotkey():
            self.translation_requested.emit()

        def on_esc():
            self.close_requested.emit()

        keyboard.add_hotkey(hotkey, on_hotkey)
        keyboard.add_hotkey('esc', on_esc)
        self.translation_requested.connect(self.translate_selected_text)
        self.close_requested.connect(self.hide)
        logging.info(f"New hotkey set: {hotkey}")
        

    def __del__(self):
        """Деструктор класса для отключения хуков."""
        keyboard.unhook_all()
        logging.info("Keyboard hooks unhooked.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Загружаем настройки из QSettings
    settings = QSettings("MyApp", "Translator")
    source_lang = settings.value("source_lang", "en")
    dest_lang = settings.value("dest_lang", "ru")
    window_width = settings.value("window_width", 300, type=int)
    window_height = settings.value("window_height", 120, type=int)
    hotkey = settings.value("hotkey", "ctrl+b")

    translator_app = TranslatorApp(source_lang, dest_lang, window_width, window_height, hotkey)


    logging.info("Starting PySide6 application.")
    sys.exit(app.exec())