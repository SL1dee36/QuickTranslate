#
# Created by @Sl1dee36
# 25.01.2025 | MIT License
#

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
    QFormLayout,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFrame,
    QListWidget,
    QListWidgetItem, 
    QToolTip,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QObject, Signal, Slot, QSettings, QTimer,QMetaObject,QGenericArgument,QByteArray
from PySide6.QtGui import QCursor, QIcon, QAction, QCloseEvent, QDesktopServices
from googletrans import Translator, LANGUAGES
import pyperclip
import logging
import keyboard
import time
import win32gui
import win32process
import os
import webbrowser


software_version = "1.1.7"

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    # Получаем абсолютный путь к ресурсам.
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

path_to_the_images = resource_path('extension.png')

# Translation dictionary for UI language
translation_dict = {
        "English":{
            "settings": "Settings",
            "source_lang": "Source Language",
            "dest_lang": "Destination Language",
            "window_width":"Window Width",
            "window_height":"Window Height",
            "hotkey": "Hotkey",
             "ui_lang": "UI Language",
             "translator": "Translator",
             "deepl_api_key":"DeepL API Key",
             "get_api_key":"How to get?",
             "buftranslate": "Auto-Translate Clipboard",
             "autorun": "Run on startup",
             "show": "Show",
             "exit": "Exit",
             "additional_translate":"Additional Translate to:",
             "history": "History",
             "history_size":"History Size"
        },
        "Русский": {
            "settings": "Настройки",
            "source_lang": "Исходный язык",
            "dest_lang": "Язык перевода",
            "window_width": "Ширина окна",
            "window_height":"Высота окна",
             "hotkey": "Сочетание клавиш",
             "ui_lang": "Язык интерфейса",
             "translator": "Переводчик",
             "deepl_api_key":"Ключ API DeepL",
             "get_api_key":"Как получить?",
             "buftranslate": "Автоматический перевод буфера обмена",
             "autorun": "Запускать при старте системы",
             "show": "Показать",
             "exit": "Выход",
             "additional_translate":"Дополнительный перевод на:",
            "history": "История",
            "history_size":"Размер истории"
        }
}


class HistoryDialog(QDialog):
    def __init__(self, parent=None, history=None):
        super().__init__(parent)
        self.setWindowTitle(translation_dict[parent.ui_lang]["history"])
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_list.setWordWrap(True)
        self.history_list.setSelectionMode(QAbstractItemView.NoSelection)  # disable selection

        if history:
            for item in history:
                src_lang = item.get('src_lang', "AUTO")
                dest_lang = item.get('dest_lang', "AUTO")
                
                original_item = QListWidgetItem(f"*{src_lang}*\n{item['original']}")
                translated_item = QListWidgetItem(f"*{dest_lang}*\n{item['translated']}")
                
                self.history_list.addItem(original_item)
                self.history_list.addItem(translated_item)
                
                # Create a separator
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setFrameShadow(QFrame.Shadow.Sunken)
                
                separator_item = QListWidgetItem()
                self.history_list.addItem(separator_item)
                self.history_list.setItemWidget(separator_item, separator)
                
        layout.addWidget(self.history_list)
        self.setLayout(layout)


class SettingsDialog(QDialog):
    class HotkeyHandler(QObject):
          textChanged = Signal(str)
    """Диалог настроек."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.settings = QSettings("QuickTranslate", "Translator")  # Инициализируем QSettings

        # Создаем выпадающие списки для выбора языка
        self.source_lang_combo = QComboBox()
        self.dest_lang_combo = QComboBox()
        self.source_lang_combo.addItem("Auto", "auto") # Adding "Auto" option
        for lang_code, lang_name in LANGUAGES.items():
            self.source_lang_combo.addItem(f"{lang_name} ({lang_code})", lang_code)
            self.dest_lang_combo.addItem(f"{lang_name} ({lang_code})", lang_code)

        # Create ComboBox for UI Language
        self.ui_lang_combo = QComboBox()
        self.ui_lang_combo.addItems(["English", "Русский"])  # add more languages as needed

        # Create ComboBox for Translator
        self.translator_combo = QComboBox()
        self.translator_combo.addItems(["googletrans", "deepl"])
        self.translator_combo.currentIndexChanged.connect(self.toggle_deepl_widgets)

        # Create DeepL API key input
        self.deepl_api_key_input = QLineEdit()
        self.deepl_api_key_button = QPushButton(translation_dict[self.settings.value("ui_lang", "English")]["get_api_key"])
        self.deepl_api_key_button.clicked.connect(self.open_deepl_website)

        # Create CheckBox for Auto Translate from clipboard
        self.buftranslate_checkbox = QCheckBox()
        # Create CheckBox for Auto Run
        self.autorun_checkbox = QCheckBox()
        
        # Создаем спинбоксы для настройки размера окна
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(100, 1000)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(50, 1000)
        
        # Создаем спинбоксы для настройки горячих клавиш
        self.hotkey_input = QTextEdit()
        self.hotkey_input.setFixedHeight(25)
        self.hotkey_input.setReadOnly(True)
        #инициализируем класс
        self.hotkey_handler = SettingsDialog.HotkeyHandler()
        # Подключаем signal
        self.hotkey_handler.textChanged.connect(self.hotkey_input.setText)

        # Create spinbox for history size
        self.history_size_spinbox = QSpinBox()
        self.history_size_spinbox.setRange(1, 20)

        # Create a separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.software_version_label = QLabel(f"Software Version is: {software_version}")
        
        # Инициализируем значения на основе сохраненных настроек
        self.load_settings()

        # Создаем форму для настроек
        form_layout = QFormLayout()
        self.form_layout = form_layout
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["source_lang"], self.source_lang_combo)
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["dest_lang"], self.dest_lang_combo)
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["window_width"], self.width_spinbox)
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["window_height"], self.height_spinbox)
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["hotkey"], self.hotkey_input)
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["ui_lang"], self.ui_lang_combo)
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["translator"], self.translator_combo)
        # Add DeepL API key input and button with text based on the selected UI language
        self.deepl_api_row = form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["deepl_api_key"], self.deepl_api_key_input)
        form_layout.addRow("", self.deepl_api_key_button)
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["history_size"], self.history_size_spinbox)
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["buftranslate"], self.buftranslate_checkbox)
        form_layout.addRow(translation_dict[self.settings.value("ui_lang", "English")]["autorun"], self.autorun_checkbox)
    
        # form_layout.addRow(self.software_version_label)
        # Кнопки OK и Отмена
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Общий макет
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.separator) # Add the separator
        main_layout.addWidget(self.software_version_label)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
        
        # подключаем обработчик нажатия на текстовое поле
        self.hotkey_input.mousePressEvent = self.set_hotkey_input

        self.toggle_deepl_widgets()
        
        self.retranslate_ui()

    def load_settings(self):
        """Загружает настройки из QSettings."""
        # Загружаем сохраненные настройки или значения по умолчанию
        source_lang = self.settings.value("source_lang", "en")
        dest_lang = self.settings.value("dest_lang", "ru")
        window_width = self.settings.value("window_width", 300, type=int)
        window_height = self.settings.value("window_height", 120, type=int)
        hotkey = self.settings.value("hotkey", "ctrl+b")
        ui_lang = self.settings.value("ui_lang", "English")
        translator = self.settings.value("translator", "googletrans")
        deepl_api_key = self.settings.value("deepl_api_key", "")
        buftranslate = self.settings.value("buftranslate", False, type=bool)
        autorun = self.settings.value("autorun", False, type=bool)
        history_size = self.settings.value("history_size", 5, type=int)
        
        # Устанавливаем выбранные языки в выпадающих списках
        index = self.source_lang_combo.findData(source_lang)
        if index >= 0:
            self.source_lang_combo.setCurrentIndex(index)
        index = self.dest_lang_combo.findData(dest_lang)
        if index >= 0:
            self.dest_lang_combo.setCurrentIndex(index)
        
        # Set UI Language ComboBox
        index = self.ui_lang_combo.findText(ui_lang)
        if index >= 0:
            self.ui_lang_combo.setCurrentIndex(index)
        
        # Set Translator ComboBox
        index = self.translator_combo.findText(translator)
        if index >= 0:
            self.translator_combo.setCurrentIndex(index)

        # Устанавливаем сохраненные размеры окна
        self.width_spinbox.setValue(window_width)
        self.height_spinbox.setValue(window_height)
        
        #Устанавливаем сохраненную горячую клавишу
        self.hotkey_input.setText(hotkey)
        
        # Set DeepL API Key
        self.deepl_api_key_input.setText(deepl_api_key)
        
        # Set checkbox
        self.buftranslate_checkbox.setChecked(buftranslate)
        self.autorun_checkbox.setChecked(autorun)
        
        #Set history size
        self.history_size_spinbox.setValue(history_size)

    def save_settings(self):
        """Сохраняет настройки в QSettings."""
        # Сохраняем текущие настройки
        self.settings.setValue("source_lang", self.source_lang_combo.currentData())
        self.settings.setValue("dest_lang", self.dest_lang_combo.currentData())
        self.settings.setValue("window_width", self.width_spinbox.value())
        self.settings.setValue("window_height", self.height_spinbox.value())
        
        # Сохраняем значение горячей клавиши только если оно было изменено
        if self.hotkey_input.toPlainText() != "Нажмите сочетание клавиш...":
             self.settings.setValue("hotkey", self.hotkey_input.toPlainText())
        
        self.settings.setValue("ui_lang", self.ui_lang_combo.currentText())
        self.settings.setValue("translator", self.translator_combo.currentText())
        self.settings.setValue("deepl_api_key", self.deepl_api_key_input.text())
        self.settings.setValue("buftranslate", self.buftranslate_checkbox.isChecked())
        self.settings.setValue("autorun", self.autorun_checkbox.isChecked())
        self.settings.setValue("history_size", self.history_size_spinbox.value())

    def accept(self):
        """Обработка нажатия на кнопку 'OK'."""
        self.save_settings()
        if self.parent().ui_lang != self.get_settings()['ui_lang']:
            self.parent().ui_lang = self.get_settings()['ui_lang']
            self.parent().retranslate_ui()
        super().accept()  # Закрываем диалог

    def get_settings(self):
        """Возвращает текущие настройки."""
        return {
            "source_lang": self.source_lang_combo.currentData(),
            "dest_lang": self.dest_lang_combo.currentData(),
            "window_width": self.width_spinbox.value(),
            "window_height": self.height_spinbox.value(),
            "hotkey": self.hotkey_input.toPlainText(),
            "ui_lang": self.ui_lang_combo.currentText(),
             "translator": self.translator_combo.currentText(),
             "deepl_api_key": self.deepl_api_key_input.text(),
            "buftranslate": self.buftranslate_checkbox.isChecked(),
             "autorun": self.autorun_checkbox.isChecked(),
            "history_size": self.history_size_spinbox.value()
        }


    def set_hotkey_input(self, event):
        """Ожидает нажатия горячих клавиш для добавления в текстовое поле."""
        self.hotkey_input.clear()
        self.hotkey_input.setText("Нажмите сочетание клавиш...")
        keys = []  # Список для хранения нажатых клавиш
        def on_press(e):
            if e.event_type == keyboard.KEY_DOWN:
                if e.name not in keys:
                    keys.append(e.name)
                    hotkey_text = " + ".join(keys)  # Формируем строку сочетания клавиш
                    self.hotkey_handler.textChanged.emit(hotkey_text)
            elif e.event_type == keyboard.KEY_UP and e.name == 'enter':
                keyboard.unhook(on_press)
                hotkey_text = keyboard.get_hotkey_name(keys)
                self.hotkey_handler.textChanged.emit(hotkey_text)
        keyboard.hook(on_press)
    
    def retranslate_ui(self):
         if self.parent():
            self.setWindowTitle(translation_dict[self.settings.value("ui_lang", "English")]["settings"])
            for row in range(self.form_layout.rowCount()):
                 item = self.form_layout.itemAt(row, QFormLayout.LabelRole)
                 if item:
                     label_text = translation_dict[self.settings.value("ui_lang", "English")].get(item.widget().text().replace(":","").lower(), item.widget().text())
                     item.widget().setText(f"{label_text}:")
            self.deepl_api_key_button.setText(translation_dict[self.settings.value("ui_lang", "English")]["get_api_key"])
    
    def toggle_deepl_widgets(self):
        is_deepl_selected = self.translator_combo.currentText() == "deepl"
        self.deepl_api_key_input.setVisible(is_deepl_selected)
        self.deepl_api_key_button.setVisible(is_deepl_selected)
        
    def open_deepl_website(self):
        """Opens DeepL website in the default browser."""
        webbrowser.open("https://www.deepl.com/en/checkout")
class TranslatorApp(QWidget):
    translation_requested = Signal()
    close_requested = Signal()

    def __init__(self, source_lang='en', dest_lang='ru', window_width=300, window_height=120, hotkey="ctrl+b", ui_lang = "English", translator_type = "googletrans", deepl_api_key = "", buftranslate = False, autorun = False, history_size = 5):
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
        self.setWindowIcon(QIcon(path_to_the_images))
        self.setWindowTitle("QuickTranslate")
        self.setGeometry(100, 100, self.window_width, self.window_height)
        self.setWindowFlag(Qt.WindowStaysOnTopHint) # Окно всегда сверху 
        
        # UI Language
        self.translation_dict = translation_dict
        self.ui_lang = ui_lang
        
        # Translator
        self.translator_type = translator_type
        self.deepl_api_key = deepl_api_key
        
        # Buftranslate
        self.buftranslate_enabled = buftranslate
        self.clipboard = QApplication.clipboard()
        if self.buftranslate_enabled:
            self.start_clipboard_monitor()

        #Autorun
        self.set_autorun(autorun)

        # History
        self.history = []
        self.history_size = history_size

        self.initUI()
        self.initTrayIcon()
        self.retranslate_ui()
        logging.info("TranslatorApp initialized.")
        
        self.initHotkey(self.hotkey)
        
        # Store the settings
        self._settings = {
            "source_lang": self.source_lang,
            "dest_lang": self.dest_lang,
            "window_width": self.window_width,
            "window_height": self.window_height,
            "hotkey": self.hotkey,
            "ui_lang": self.ui_lang,
            "translator": self.translator_type,
             "deepl_api_key": self.deepl_api_key,
            "buftranslate": self.buftranslate_enabled,
            "autorun": self.get_autorun(),
            "history_size": self.history_size
        }
        
    def get_settings(self):
        return self._settings    

    def initUI(self):
        """Инициализация пользовательского интерфейса."""
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True) # текст только для чтения
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) # добавить скролбар
        self.text_edit.setMouseTracking(True)  # отслеживать положение мыши

        self.text_edit.mousePressEvent = self.text_clicked
        
        # Add a combobox for additional translation
        self.additional_lang_combo = QComboBox()
        for lang_code, lang_name in LANGUAGES.items():
             self.additional_lang_combo.addItem(f"{lang_name} ({lang_code})", lang_code)
        self.additional_lang_combo.currentIndexChanged.connect(self.update_additional_translation)
        
        self.additional_lang_combo_layout = QHBoxLayout()
        self.additional_lang_combo_layout.addWidget(QLabel(translation_dict[self.ui_lang]["additional_translate"]))
        self.additional_lang_combo_layout.addWidget(self.additional_lang_combo)
        
        layout.addWidget(self.text_edit)
        layout.addLayout(self.additional_lang_combo_layout)
        self.setLayout(layout)
        
        logging.info("UI initialized.")
    
    def retranslate_ui(self):
        # Retranslate all the labels in the application
        if self.ui_lang in self.translation_dict:
            self.setWindowTitle("QuickTranslate")
            # Get the parent dialog
            
            if hasattr(self, 'tray_menu'):
                self.tray_menu.actions()[0].setText(self.translation_dict[self.ui_lang]["settings"])
                self.tray_menu.actions()[1].setText(self.translation_dict[self.ui_lang]["history"])
                self.tray_menu.actions()[2].setText(self.translation_dict[self.ui_lang]["show"])
                self.tray_menu.actions()[3].setText(self.translation_dict[self.ui_lang]["exit"])
            if hasattr(self, 'additional_lang_combo_layout'):
                self.additional_lang_combo_layout.itemAt(0).widget().setText(translation_dict[self.ui_lang]["additional_translate"])

    def initTrayIcon(self):
        """Инициализация иконки в трее."""
        self.tray_icon = QSystemTrayIcon(QIcon(path_to_the_images), self)  # Укажите путь к вашей иконке
        self.tray_menu = QMenu()

        # Действие для открытия окна настроек
        settings_action = QAction(translation_dict[self.ui_lang]["settings"], self)
        settings_action.triggered.connect(self.open_settings)
        self.tray_menu.addAction(settings_action)

        # Действие для открытия окна истории
        history_action = QAction(translation_dict[self.ui_lang]["history"], self)
        history_action.triggered.connect(self.open_history)
        self.tray_menu.addAction(history_action)


         # Действие для показа окна
        show_action = QAction(translation_dict[self.ui_lang]["show"], self)
        show_action.triggered.connect(self.show_window)
        self.tray_menu.addAction(show_action)


        # Действие для выхода
        exit_action = QAction(translation_dict[self.ui_lang]["exit"], self)
        exit_action.triggered.connect(self.close_app)
        self.tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        logging.info("Tray icon initialized.")
    
    def translate_google(self, text, src, dest):
        try:
             translation = self.translator.translate(text, src=src, dest=dest)
             return translation.text
        except Exception as e:
             return f"Ошибка перевода: {e}"
    
    def translate_deepl(self, text, src, dest):
        try:
            import deepl
            translator_deepl = deepl.Translator(self.deepl_api_key)
            translation = translator_deepl.translate_text(text, target_lang=dest, source_lang=src)
            return translation.text
        except Exception as e:
            return f"Ошибка перевода: {e}"

    def translate_text(self, text, dest_lang = None):
        logging.info(f"Translating text: {text}")
        if not text or not isinstance(text, str):
            logging.warning("No text provided for translation or text is not string.")
            return None

        if self.source_lang == "auto":
            try:
                detected = self.translator.detect(text)
                source_lang = detected.lang
            except Exception as e:
                logging.error(f"Error during language detection: {e}")
                return f"Ошибка определения языка: {e}"
        else:
            source_lang = self.source_lang
            
        if dest_lang == None:
             dest_lang = self.dest_lang
        
        try:
            if self.translator_type == "googletrans":
                 translation = self.translate_google(text, source_lang, dest_lang)
            elif self.translator_type == "deepl":
                  translation = self.translate_deepl(text, source_lang, dest_lang)
            else:
                 return "Выберите переводчика"
            logging.info(f"Translation successful: {translation}")
            
            # Detect languages after translation
            if self.source_lang == "auto":
                 detected_src = self.translator.detect(text)
                 src_lang = detected_src.lang.upper()
            else:
                 src_lang = self.source_lang.upper()
            
            if dest_lang == self.dest_lang:
                 detected_dest = self.translator.detect(translation)
                 dest_lang_upper = detected_dest.lang.upper()
            else:
                 dest_lang_upper = dest_lang.upper()
            
            self.update_history(text, translation, src_lang, dest_lang_upper)
            
            return translation
        except Exception as e:
                logging.error(f"Error during translation: {e}")
                return f"Ошибка перевода: {e}"
    
    def update_history(self, original_text, translated_text, src_lang, dest_lang):
        self.history.append({"original": original_text, "translated": translated_text, "src_lang": src_lang, "dest_lang": dest_lang})
        if len(self.history) > self.history_size:
            self.history.pop(0)

    @Slot()
    def show_translation(self, selected_text):
        logging.info(f"Attempting to show translation for: {selected_text}")
        if selected_text and selected_text != self.last_selected_text:
            if self.is_foreign_text(selected_text):
                self.last_selected_text = selected_text
                self.show_window()
                self.flash_window()  # Flash the window
                QTimer.singleShot(100, lambda: self._show_translation(selected_text))
            else:
                logging.info("Selected text is not in the source language.")
        else:
            logging.info("Selected text is same as last selected or is empty.")
    
    def _show_translation(self, selected_text):
        translated_text = self.translate_text(selected_text)
        if translated_text:
            self.text_edit.setText(translated_text)
            self.adjust_window_position()  # Регулировать положение окна
    
    @Slot()
    def update_additional_translation(self):
         selected_text = self.last_selected_text
         if selected_text:
            dest_lang = self.additional_lang_combo.currentData()
            translated_text = self.translate_text(selected_text, dest_lang)
            if translated_text:
                 self.text_edit.setText(translated_text)
                 logging.info(f"Additional translation requested for: {selected_text}, to {dest_lang}")
    
    def flash_window(self):
         """Моргает окно."""
         if self.isVisible():
            original_opacity = self.windowOpacity()
            self.setWindowOpacity(0.5)
            QTimer.singleShot(100, lambda: self.setWindowOpacity(original_opacity))
    
    def open_history(self):
          history_dialog = HistoryDialog(self, self.history)
          history_dialog.exec()
    
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
        self.hide_window()

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
                if detected.lang == self.source_lang or self.source_lang == "auto":
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
            self.ui_lang = settings["ui_lang"]
            self.translator_type = settings["translator"]
            self.deepl_api_key = settings["deepl_api_key"]
            
            # Buftranslate
            if settings["buftranslate"] != self.buftranslate_enabled:
                self.buftranslate_enabled = settings["buftranslate"]
                if self.buftranslate_enabled:
                    self.start_clipboard_monitor()
                else:
                    self.clipboard_timer.stop()
            #Autorun
            if settings["autorun"] != self.get_autorun():
                self.set_autorun(settings["autorun"])
            
            #History size
            self.history_size = settings["history_size"]

            # Обновляем размеры окна
            self.resize(self.window_width, self.window_height)
            #Переназначаем горячую клавишу
            self.initHotkey(self.hotkey)
            self.retranslate_ui()
            logging.info("Settings applied successfully.")
            
            # Update settings
            self._settings = settings
    
    def get_autorun(self):
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            value = winreg.QueryValueEx(key, "QuickTranslate")[0]
            winreg.CloseKey(key)
            return bool(value)
        except FileNotFoundError:
            return False
        except Exception:
            return False


    def close_app(self):
        """Закрывает приложение."""
        logging.info("Application close requested.")
        self.tray_icon.hide()  # Скрываем иконку перед закрытием
        QApplication.quit()
        
    def show_window(self):
        self.show()
        self.activateWindow()
    
    def hide_window(self):
         self.hide()
    
    def closeEvent(self, event: QCloseEvent):
        """Переопределяем событие закрытия окна."""
        event.ignore()  # Игнорируем событие закрытия по умолчанию
        self.hide_window()
    
    def initHotkey(self, hotkey):
        """Инициализирует горячую клавишу."""
        # Отключаем старую горячую клавишу
        keyboard.unhook_all()

        # Глобальный хук для обработки Ctrl+B и ESC (работает во всех приложениях)
        def on_hotkey():
            self.translation_requested.emit()

        def on_esc():
            self.close_requested.emit()
        
        try:
            keyboard.add_hotkey(hotkey, on_hotkey)
            keyboard.add_hotkey('esc', on_esc)
            self.translation_requested.connect(self.translate_selected_text)
            self.close_requested.connect(self.hide_window)
            logging.info(f"New hotkey set: {hotkey}")
        except:
            hotkey = settings.value("hotkey", "ctrl+b")

    
    def start_clipboard_monitor(self):
        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.timeout.connect(self.check_clipboard_change)
        self.clipboard_timer.start(500)
    
    def check_clipboard_change(self):
        new_clipboard_text = self.clipboard.text()
        if new_clipboard_text and new_clipboard_text != self.user_buffer and new_clipboard_text != self.last_selected_text:
             if self.is_foreign_text(new_clipboard_text):
                   self.user_buffer = new_clipboard_text
                   translated_text = self.translate_text(new_clipboard_text)
                   if translated_text:
                       self.copy_translation(translated_text)
                       logging.info("Text from clipboard has been translated and replaced")

    def set_autorun(self, enabled):
            import winreg
            path = os.path.realpath(sys.argv[0])
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            try:
                if enabled:
                    winreg.SetValueEx(key, "QuickTranslate", 0, winreg.REG_SZ, path)
                else:
                    winreg.DeleteValue(key, "QuickTranslate")
            except FileNotFoundError:
                 pass
            finally:
                winreg.CloseKey(key)

    def __del__(self):
        """Деструктор класса для отключения хуков."""
        keyboard.unhook_all()
        logging.info("Keyboard hooks unhooked.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Загружаем настройки из QSettings
    settings = QSettings("QuickTranslate", "Translator")
    source_lang = settings.value("source_lang", "en")
    dest_lang = settings.value("dest_lang", "ru")
    window_width = settings.value("window_width", 300, type=int)
    window_height = settings.value("window_height", 120, type=int)
    hotkey = settings.value("hotkey", "ctrl+b")
    ui_lang = settings.value("ui_lang", "English")
    translator_type = settings.value("translator", "googletrans")
    deepl_api_key = settings.value("deepl_api_key", "")
    buftranslate = settings.value("buftranslate", False, type=bool)
    autorun = settings.value("autorun", False, type=bool)
    history_size = settings.value("history_size", 5, type = int)
    

    translator_app = TranslatorApp(source_lang, dest_lang, window_width, window_height, hotkey, ui_lang, translator_type, deepl_api_key, buftranslate, autorun, history_size)

    # Tooltips
    QToolTip.setFont(app.font())
    translator_app.tray_menu.actions()[0].setToolTip("Open the settings window.")
    translator_app.tray_menu.actions()[1].setToolTip("Open the history window.")
    translator_app.tray_menu.actions()[2].setToolTip("Show the main window.")
    translator_app.tray_menu.actions()[3].setToolTip("Exit the application.")
    
    logging.info("Starting PySide6 application.")
    
    app.exec()