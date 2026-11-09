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
    QAbstractItemView,
    QTabWidget,
    QFileDialog,
    QProgressBar,
    QProgressDialog
)
from PySide6.QtCore import Qt, QObject, Signal, Slot, QSettings, QTimer, QMetaObject, QGenericArgument, QByteArray, QThread, QUrl, QRect, QSize
from PySide6.QtGui import QCursor, QIcon, QAction, QCloseEvent, QDesktopServices, QIconEngine, QPainter, QPixmap, QColor, QPalette
from PySide6.QtSvg import QSvgRenderer

# Safe import for googletrans (handling modern httpcore incompatibility)
try:
    import httpcore
    if not hasattr(httpcore, 'SyncHTTPTransport'):
        httpcore.SyncHTTPTransport = object
    from googletrans import Translator, LANGUAGES
except Exception as e:
    logging.warning(f"Could not import googletrans: {e}")
    Translator = None
    LANGUAGES = {
        'en': 'english', 'ru': 'russian', 'de': 'german', 'fr': 'french',
        'es': 'spanish', 'it': 'italian', 'zh-cn': 'chinese (simplified)',
        'ja': 'japanese', 'ko': 'korean', 'uk': 'ukrainian', 'pl': 'polish',
        'tr': 'turkish', 'ar': 'arabic', 'pt': 'portuguese', 'nl': 'dutch'
    }

import pyperclip
import logging
import keyboard
import time
import win32gui
import win32process
import os
import webbrowser
import offline_translator


software_version = "1.2.0"

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    # Получаем абсолютный путь к ресурсам (для PyInstaller, Nuitka и обычного запуска).
    try:
        base_path = sys._MEIPASS
    except Exception:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

path_to_the_images = resource_path('extension.png')

# Векторные иконки в едином простом стиле (чистый минимализм)
ICONS_SVG = {
    "trash": """<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>""",
    "close": """<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>""",
    "check": """<polyline points="20 6 9 17 4 12"/>""",
    "package": """<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>""",
    "download": """<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>""",
    "file-plus": """<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/>""",
    "folder": """<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>""",
    "refresh": """<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>""",
    "globe": """<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>""",
    "warning": """<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>""",
    "info": """<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>""",
    "key": """<path d="M21 2l-2 2m-1.5 1.5L16 7l-1.5-1.5L13 7l-2-2-4 4a5 5 0 1 0 7.07 7.07l7.93-7.93V2h-1z"/><circle cx="7.5" cy="16.5" r="1.5"/>""",
    "keyboard": """<rect x="2" y="4" width="20" height="16" rx="2" ry="2"/><line x1="6" y1="8" x2="6.01" y2="8"/><line x1="10" y1="8" x2="10.01" y2="8"/><line x1="14" y1="8" x2="14.01" y2="8"/><line x1="18" y1="8" x2="18.01" y2="8"/><line x1="6" y1="12" x2="6.01" y2="12"/><line x1="18" y1="12" x2="18.01" y2="12"/><line x1="10" y1="12" x2="14" y2="12"/><line x1="8" y1="16" x2="16" y2="16"/>""",
    "settings": """<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>""",
    "history": """<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>""",
    "show": """<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>""",
    "exit": """<path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/>"""
}

def is_dark_theme() -> bool:
    """Определяет, используется ли тёмная тема в приложении или системе."""
    app = QApplication.instance()
    if app:
        palette = app.palette()
        win_color = palette.color(QPalette.ColorRole.Window)
        if win_color.isValid():
            return win_color.lightness() < 128
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return val == 0
    except Exception:
        pass
    return True

_icon_pixmap_cache = {}

class SvgIconEngine(QIconEngine):
    """Векторный движок иконок: для тёмной темы — чисто белые, для светлой — чисто чёрные."""
    def __init__(self, name: str, color_override: str = None):
        super().__init__()
        self.name = name
        self.color_override = color_override

    def _get_color(self) -> str:
        if self.color_override:
            return self.color_override
        return "#ffffff" if is_dark_theme() else "#000000"

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        w, h = size.width(), size.height()
        side = min(w, h)
        if side <= 0:
            return QPixmap()

        color = self._get_color()
        is_disabled = (mode == QIcon.Mode.Disabled)
        cache_key = (self.name, color, w, h, is_disabled)
        if cache_key in _icon_pixmap_cache:
            return _icon_pixmap_cache[cache_key]

        body = ICONS_SVG.get(self.name, "")
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{side}" height="{side}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>'
        )
        renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))

        pm = QPixmap(size)
        pm.fill(QColor(0, 0, 0, 0))
        p = QPainter(pm)
        if is_disabled:
            p.setOpacity(0.35)

        x = (w - side) // 2
        y = (h - side) // 2
        renderer.render(p, QRect(x, y, side, side))
        p.end()

        _icon_pixmap_cache[cache_key] = pm
        return pm

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
        pm = self.pixmap(rect.size(), mode, state)
        if not pm.isNull():
            painter.drawPixmap(rect.topLeft(), pm)

    def clone(self):
        return SvgIconEngine(self.name, self.color_override)

def get_icon(name: str, color_override: str = None) -> QIcon:
    """Возвращает масштабируемую иконку в едином простом стиле (белая для темной темы, черная для светлой)."""
    return QIcon(SvgIconEngine(name, color_override))

def get_pixmap(name: str, size: int = 24, color_override: str = None) -> QPixmap:
    """Возвращает растровое изображение иконки заданного размера."""
    return get_icon(name, color_override).pixmap(size, size)

# Translation dictionary for UI language (humanized, warm, and zero emojis)
translation_dict = {
    "English": {
        "settings": "Settings",
        "source_lang": "Translate from",
        "dest_lang": "Translate to",
        "window_width": "Window width",
        "window_height": "Window height",
        "hotkey": "Shortcut key",
        "ui_lang": "Interface language",
        "translator": "Translation engine",
        "deepl_api_key": "DeepL API key",
        "get_api_key": "Get DeepL API key...",
        "buftranslate": "Translate on clipboard copy (Ctrl+C)",
        "autorun": "Launch on Windows startup",
        "show": "Show translation window",
        "exit": "Exit",
        "additional_translate": "Quick translation to:",
        "history": "Translation history",
        "history_size": "History entries to keep",
        "history_empty": "Translation history is empty.",
        "clear_history": "Clear history",
        "close": "Close",
        "save": "Save",
        "cancel": "Cancel",
        "record_hotkey": "Record",
        "offline_packages": "Offline models",
        "manage_packages": "Manage offline models...",
        "installed_packages_tab": "Installed models",
        "download_packages_tab": "Download for offline use",
        "install_package_file": "Install model from file (.argosmodel)...",
        "delete_package": "Delete model",
        "open_packages_folder": "Open models folder in Explorer",
        "download_package_file": "Save selected model to file...",
        "open_web_catalog": "Browse models on website",
        "refresh_catalog": "Refresh online list",
        "offline_notice": "Offline translation runs locally on your PC without an internet connection.",
        "download_notice": "Download a model file (.argosmodel) on an online PC, transfer it via USB flash drive, and install it on the 'Installed models' tab.",
        "unidirectional_notice": "Important: translation models are one-way.\nFor example, 'Russian → English' only translates Russian to English. For two-way translation, install both models ('English → Russian' and 'Russian → English').",
        "no_installed_packages": "No offline models installed yet.\nClick below to install a model from a file.",
        "package_installed_success": "Model installed successfully and ready to use!",
        "package_saved_success": "Model file downloaded successfully!",
        "confirm_delete_package": "Are you sure you want to delete this language model?",
        "install_now_prompt": "Would you like to install this model on this computer right now?",
        "started_notification": "QuickTranslate is running in the background.\nSelect text anywhere and press your shortcut to translate.",
        "press_hotkey_hint": "Press keys (Esc to cancel)...",
        "software_version": "Version: 1.2.0",
        "copied_hint": "Translation copied to clipboard!",
        "saved_feedback": "Saved!",
        "dismiss": "Dismiss"
    },
    "Русский": {
        "settings": "Настройки",
        "source_lang": "Переводить с",
        "dest_lang": "Переводить на",
        "window_width": "Ширина окна",
        "window_height": "Высота окна",
        "hotkey": "Горячая клавиша",
        "ui_lang": "Язык интерфейса",
        "translator": "Служба перевода",
        "deepl_api_key": "Ключ DeepL API",
        "get_api_key": "Как получить ключ DeepL...",
        "buftranslate": "Переводить текст при копировании (Ctrl+C)",
        "autorun": "Запускать при старте Windows",
        "show": "Показать окно перевода",
        "exit": "Выход",
        "additional_translate": "Быстрый перевод на:",
        "history": "История переводов",
        "history_size": "Количество записей в истории",
        "history_empty": "История переводов пока пуста.",
        "clear_history": "Очистить историю",
        "close": "Закрыть",
        "save": "Сохранить",
        "cancel": "Отмена",
        "record_hotkey": "Задать",
        "offline_packages": "Офлайн-модели",
        "manage_packages": "Управление офлайн-моделями...",
        "installed_packages_tab": "Установленные модели",
        "download_packages_tab": "Скачать для переноса на ПК",
        "install_package_file": "Установить модель из файла (.argosmodel)...",
        "delete_package": "Удалить модель",
        "open_packages_folder": "Открыть папку с моделями в проводнике",
        "download_package_file": "Скачать выбранную модель в файл...",
        "open_web_catalog": "Открыть каталог на официальном сайте",
        "refresh_catalog": "Обновить список моделей",
        "offline_notice": "Офлайн-перевод работает прямо на компьютере без подключения к сети.",
        "download_notice": "Скачайте файл модели (.argosmodel) на компьютере с интернетом, скиньте на флешку и установите на вкладке «Установленные модели».",
        "unidirectional_notice": "Памятка: языковые модели работают строго в одну сторону.\nНапример, «Russian → English» переводит только с русского на английский. Для двустороннего перевода нужны оба пакета («English → Russian» и «Russian → English»).",
        "no_installed_packages": "Офлайн-модели пока не установлены.\nНажмите кнопку ниже, чтобы установить модель из файла.",
        "package_installed_success": "Модель успешно установлена и готова к работе!",
        "package_saved_success": "Файл модели успешно скачан и сохранён!",
        "confirm_delete_package": "Вы действительно хотите удалить эту языковую модель?",
        "install_now_prompt": "Установить скачанную модель на этот компьютер прямо сейчас?",
        "started_notification": "QuickTranslate работает в фоне.\nВыделите любой текст и нажмите горячую клавишу для перевода.",
        "press_hotkey_hint": "Нажмите сочетание клавиш (Esc для отмены)...",
        "software_version": "Версия программы: 1.2.0",
        "copied_hint": "Перевод скопирован в буфер обмена!",
        "saved_feedback": "Сохранено!",
        "dismiss": "Скрыть"
    }
}

# Строгий маппинг кириллических и локализованных клавиш в латиницу (QWERTY)
CYRILLIC_TO_LATIN = dict(zip(
    'йцукенгшщзхъфывапролджэячсмитьбюё',
    "qwertyuiop[]asdfghjkl;'zxcvbnm,.`"
))
CYRILLIC_TO_LATIN.update({
    'і': 's', 'ї': ']', 'є': "'", 'ґ': 'g', 'ў': 'u'
})

MODIFIER_KEYS = {
    'ctrl': 'ctrl', 'left ctrl': 'ctrl', 'right ctrl': 'ctrl', 'control': 'ctrl',
    'alt': 'alt', 'left alt': 'alt', 'right alt': 'alt', 'alt gr': 'alt',
    'shift': 'shift', 'left shift': 'shift', 'right shift': 'shift',
    'windows': 'windows', 'left windows': 'windows', 'right windows': 'windows', 'win': 'windows'
}

def normalize_key_to_latin(name: str) -> str:
    """Преобразует символ клавиши к строчной латинице (например, 'и' -> 'b')."""
    if not name:
        return ""
    name_lower = name.lower().strip()
    return CYRILLIC_TO_LATIN.get(name_lower, name_lower)

def normalize_hotkey_to_latin(hotkey_str: str) -> str:
    """Приводит всю комбинацию горячих клавиш строго к латинице."""
    if not hotkey_str:
        return "ctrl + b"
    raw_parts = [p.strip().lower() for p in hotkey_str.split('+') if p.strip()]
    modifiers = []
    normal_keys = []
    for p in raw_parts:
        if p in MODIFIER_KEYS:
            mod = MODIFIER_KEYS[p]
            if mod not in modifiers:
                modifiers.append(mod)
        else:
            lat = normalize_key_to_latin(p)
            if lat not in normal_keys and lat not in modifiers:
                normal_keys.append(lat)
    order = ['ctrl', 'alt', 'shift', 'windows']
    sorted_mods = [m for m in order if m in modifiers]
    all_parts = sorted_mods + normal_keys
    return " + ".join(all_parts) if all_parts else "ctrl + b"


class HistoryDialog(QDialog):
    def __init__(self, parent=None, history=None):
        super().__init__(parent)
        self.parent_app = parent
        ui_lang = getattr(parent, 'ui_lang', 'English')
        t = translation_dict.get(ui_lang, translation_dict["English"])
        self.setWindowTitle(t.get("history", "Translation history"))
        if parent:
            self.setWindowIcon(parent.windowIcon())
        self.setMinimumSize(460, 320)
        layout = QVBoxLayout(self)

        self.history_list = QListWidget()
        self.history_list.setWordWrap(True)
        self.history_list.setSelectionMode(QAbstractItemView.NoSelection)

        if history:
            for item in history:
                src_lang = item.get('src_lang', "AUTO")
                dest_lang = item.get('dest_lang', "AUTO")
                orig_text = item.get('original', '')
                trans_text = item.get('translated', '')

                header = QListWidgetItem(f"[{src_lang} → {dest_lang}]")
                header_font = header.font()
                header_font.setBold(True)
                header.setFont(header_font)
                header.setForeground(Qt.gray)
                self.history_list.addItem(header)

                self.history_list.addItem(QListWidgetItem(orig_text))

                trans_item = QListWidgetItem(f"→ {trans_text}")
                trans_item.setForeground(Qt.cyan)
                self.history_list.addItem(trans_item)

                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setFrameShadow(QFrame.Shadow.Sunken)
                separator_item = QListWidgetItem()
                self.history_list.addItem(separator_item)
                self.history_list.setItemWidget(separator_item, separator)
        else:
            empty_item = QListWidgetItem(t.get("history_empty", "Translation history is empty."))
            empty_item.setFlags(Qt.NoItemFlags)
            self.history_list.addItem(empty_item)

        layout.addWidget(self.history_list)

        btn_layout = QHBoxLayout()

        if history and parent and hasattr(parent, 'history'):
            clear_btn = QPushButton(t.get("clear_history", "Clear history"))
            clear_btn.setIcon(get_icon("trash"))
            def clear_act():
                parent.history.clear()
                self.history_list.clear()
                empty = QListWidgetItem(t.get("history_empty", "Translation history is empty."))
                empty.setFlags(Qt.NoItemFlags)
                self.history_list.addItem(empty)
                clear_btn.setEnabled(False)
            clear_btn.clicked.connect(clear_act)
            btn_layout.addWidget(clear_btn)

        btn_layout.addStretch()
        close_btn = QPushButton(t.get("close", "Close"))
        close_btn.setIcon(get_icon("close"))
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)


class FetchPackagesThread(QThread):
    packages_loaded = Signal(list)
    error_occurred = Signal(str)

    def run(self):
        try:
            pkgs = offline_translator.get_available_packages()
            self.packages_loaded.emit(pkgs)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DownloadPackageThread(QThread):
    progress_signal = Signal(int, int)
    finished_signal = Signal(bool, str)

    def __init__(self, pkg, destination_path):
        super().__init__()
        self.pkg = pkg
        self.destination_path = destination_path
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            offline_translator.download_package_to_file(
                self.pkg,
                self.destination_path,
                progress_callback=lambda cur, tot: self.progress_signal.emit(cur, tot),
                cancel_check=lambda: self._cancelled
            )
            self.finished_signal.emit(True, self.destination_path)
        except InterruptedError:
            self.finished_signal.emit(False, "cancelled")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class OfflinePackagesDialog(QDialog):
    """Диалог управления офлайн-моделями (Argos Translate)."""
    def __init__(self, parent=None, ui_lang="English"):
        super().__init__(parent)
        self.ui_lang = ui_lang
        t = translation_dict[self.ui_lang]
        self.setWindowTitle(t.get("offline_packages", "Offline models"))
        if parent:
            self.setWindowIcon(parent.windowIcon())
        self.setMinimumSize(580, 440)
        self.available_packages = []
        self.download_thread = None
        self.fetch_thread = None

        main_layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        
        # Вкладка 1: Установленные модели
        self.installed_tab = QWidget()
        self.init_installed_tab()
        self.tab_widget.addTab(
            self.installed_tab,
            get_icon("package"),
            t.get("installed_packages_tab", "Installed models")
        )

        # Вкладка 2: Скачать в файл
        self.download_tab = QWidget()
        self.init_download_tab()
        self.tab_widget.addTab(
            self.download_tab,
            get_icon("download"),
            t.get("download_packages_tab", "Download for offline use")
        )

        main_layout.addWidget(self.tab_widget)

        # Кнопка закрыть
        btn_box = QDialogButtonBox()
        close_btn = btn_box.addButton(t.get("close", "Close"), QDialogButtonBox.RejectRole)
        close_btn.setIcon(get_icon("close"))
        btn_box.rejected.connect(self.close)
        main_layout.addWidget(btn_box)

        self.refresh_installed_list()

    def create_notice_card(self, notice_id, text, icon_name, border_color):
        """Создает аккуратный блок уведомления со светлым текстом и крестиком закрытия."""
        settings = QSettings("QuickTranslate", "Translator")
        if settings.value(f"notice_{notice_id}_closed", False, type=bool):
            return None

        card = QFrame()
        card.notice_id = notice_id
        is_dark = is_dark_theme()
        bg_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.04)"
        card.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border: none; border-left: 3px solid {border_color}; border-radius: 4px; }}")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 8, 8)
        card_layout.setSpacing(10)

        icon_label = QLabel()
        icon_label.setStyleSheet("background: transparent; border: none;")
        icon_label.setPixmap(get_pixmap(icon_name, 18))
        card_layout.addWidget(icon_label, alignment=Qt.AlignTop)

        text_color = "#f0f0f0" if is_dark else "#1a1a1a"
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"color: {text_color}; font-size: 11px; line-height: 1.35; background: transparent; border: none;")
        card_layout.addWidget(text_label, stretch=1)

        # Крестик для закрытия уведомления
        close_card_btn = QPushButton()
        close_card_btn.setIcon(get_icon("close"))
        close_card_btn.setIconSize(QSize(12, 12))
        close_card_btn.setFixedSize(22, 22)
        close_card_btn.setCursor(Qt.PointingHandCursor)
        t = translation_dict.get(self.ui_lang, translation_dict["English"])
        close_card_btn.setToolTip(t.get("dismiss", "Dismiss"))
        hover_bg = "rgba(255, 255, 255, 0.16)" if is_dark else "rgba(0, 0, 0, 0.08)"
        close_card_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 3px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
        """)

        def dismiss():
            s = QSettings("QuickTranslate", "Translator")
            s.setValue(f"notice_{notice_id}_closed", True)
            # Скрываем все карточки с этим же notice_id в диалоге
            for widget in self.findChildren(QFrame):
                if getattr(widget, 'notice_id', None) == notice_id:
                    widget.hide()
                    widget.deleteLater()

        close_card_btn.clicked.connect(dismiss)
        card_layout.addWidget(close_card_btn, alignment=Qt.AlignTop)

        return card

    def init_installed_tab(self):
        t = translation_dict[self.ui_lang]
        layout = QVBoxLayout(self.installed_tab)

        memo_card = self.create_notice_card(
            "unidirectional",
            t.get("unidirectional_notice"),
            "warning",
            "#f39c12"
        )
        if memo_card:
            layout.addWidget(memo_card)

        notice_card = self.create_notice_card(
            "offline",
            t.get("offline_notice"),
            "info",
            "#3498db"
        )
        if notice_card:
            layout.addWidget(notice_card)

        self.installed_list = QListWidget()
        layout.addWidget(self.installed_list)

        btn_layout = QHBoxLayout()
        self.install_file_btn = QPushButton(t.get("install_package_file", "Install model from file (.argosmodel)..."))
        self.install_file_btn.setIcon(get_icon("file-plus"))
        self.install_file_btn.clicked.connect(self.install_from_file_dialog)
        btn_layout.addWidget(self.install_file_btn)

        self.delete_btn = QPushButton(t.get("delete_package", "Delete model"))
        self.delete_btn.setIcon(get_icon("trash"))
        self.delete_btn.clicked.connect(self.delete_selected_package)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        self.open_folder_btn = QPushButton(t.get("open_packages_folder", "Open models folder in Explorer"))
        self.open_folder_btn.setIcon(get_icon("folder"))
        self.open_folder_btn.clicked.connect(self.open_packages_folder)
        layout.addWidget(self.open_folder_btn)

    def init_download_tab(self):
        t = translation_dict[self.ui_lang]
        layout = QVBoxLayout(self.download_tab)

        memo_card = self.create_notice_card(
            "unidirectional",
            t.get("unidirectional_notice"),
            "warning",
            "#f39c12"
        )
        if memo_card:
            layout.addWidget(memo_card)

        notice_card = self.create_notice_card(
            "download",
            t.get("download_notice"),
            "info",
            "#3498db"
        )
        if notice_card:
            layout.addWidget(notice_card)

        h_fetch = QHBoxLayout()
        self.available_combo = QComboBox()
        self.available_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        h_fetch.addWidget(self.available_combo, stretch=1)

        self.refresh_cat_btn = QPushButton(t.get("refresh_catalog", "Refresh online list"))
        self.refresh_cat_btn.setIcon(get_icon("refresh"))
        self.refresh_cat_btn.clicked.connect(self.fetch_available_packages)
        h_fetch.addWidget(self.refresh_cat_btn)
        layout.addLayout(h_fetch)

        self.download_btn = QPushButton(t.get("download_package_file", "Save selected model to file..."))
        self.download_btn.setIcon(get_icon("download"))
        self.download_btn.clicked.connect(self.start_download_package)
        layout.addWidget(self.download_btn)

        layout.addStretch()

        self.web_cat_btn = QPushButton(t.get("open_web_catalog", "Browse models on website"))
        self.web_cat_btn.setIcon(get_icon("globe"))
        self.web_cat_btn.clicked.connect(lambda: webbrowser.open("https://www.argosopentech.com/argospm/index/"))
        layout.addWidget(self.web_cat_btn)

    def refresh_installed_list(self):
        t = translation_dict[self.ui_lang]
        self.installed_list.clear()
        packages = offline_translator.get_installed_packages()
        if not packages:
            item = QListWidgetItem(t.get("no_installed_packages", "No offline packages installed."))
            item.setFlags(Qt.NoItemFlags)
            self.installed_list.addItem(item)
            self.delete_btn.setEnabled(False)
        else:
            for p in packages:
                text = f"{p['from_name']} ({p['from_code'].upper()})  →  {p['to_name']} ({p['to_code'].upper()})  [v{p['version']}]"
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, p['pkg'])
                self.installed_list.addItem(item)
            self.delete_btn.setEnabled(True)

    def install_from_file_dialog(self):
        t = translation_dict[self.ui_lang]
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t.get("install_package_file", "Install from file (.argosmodel)..."),
            "",
            "Argos Model (*.argosmodel *.zip);;All Files (*.*)"
        )
        if not file_path:
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            offline_translator.install_from_file(file_path)
            QApplication.restoreOverrideCursor()
            self.refresh_installed_list()
            QMessageBox.information(
                self,
                "QuickTranslate",
                f"{t.get('package_installed_success', 'Package successfully installed!')}\n\n{os.path.basename(file_path)}"
            )
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", f"Failed to install package:\n{e}")

    def delete_selected_package(self):
        t = translation_dict[self.ui_lang]
        current_item = self.installed_list.currentItem()
        if not current_item:
            return
        pkg = current_item.data(Qt.UserRole)
        if not pkg:
            return

        reply = QMessageBox.question(
            self,
            "QuickTranslate",
            f"{t.get('confirm_delete_package', 'Are you sure you want to delete this package?')}\n\n{current_item.text()}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                offline_translator.uninstall_package(pkg)
                self.refresh_installed_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete package:\n{e}")

    def open_packages_folder(self):
        pkg_dir = offline_translator.get_packages_dir()
        if not os.path.exists(pkg_dir):
            os.makedirs(pkg_dir, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(pkg_dir)))

    def fetch_available_packages(self):
        self.refresh_cat_btn.setEnabled(False)
        self.refresh_cat_btn.setText("Загрузка..." if self.ui_lang == "Русский" else "Loading...")
        self.fetch_thread = FetchPackagesThread()
        self.fetch_thread.packages_loaded.connect(self.on_packages_loaded)
        self.fetch_thread.error_occurred.connect(self.on_fetch_error)
        self.fetch_thread.start()

    def on_packages_loaded(self, packages):
        self.available_packages = packages
        t = translation_dict[self.ui_lang]
        self.refresh_cat_btn.setEnabled(True)
        self.refresh_cat_btn.setText(t.get("refresh_catalog", "Refresh online catalog"))
        self.available_combo.clear()
        
        sorted_pkgs = sorted(packages, key=lambda p: (
            0 if p.to_code == 'ru' or p.from_code == 'ru' else 1,
            getattr(p, 'from_name', ''),
            getattr(p, 'to_name', '')
        ))
        
        for pkg in sorted_pkgs:
            text = f"{pkg.from_name} ({pkg.from_code.upper()})  →  {pkg.to_name} ({pkg.to_code.upper()})  [v{pkg.package_version}]"
            self.available_combo.addItem(text, pkg)

    def on_fetch_error(self, err_msg):
        t = translation_dict[self.ui_lang]
        self.refresh_cat_btn.setEnabled(True)
        self.refresh_cat_btn.setText(t.get("refresh_catalog", "Refresh online catalog"))
        QMessageBox.warning(
            self,
            "Connection Error",
            f"Не удалось получить список пакетов онлайн:\n{err_msg}\n\nВы можете скачать пакеты вручную через веб-каталог."
            if self.ui_lang == "Русский"
            else f"Failed to fetch package list online:\n{err_msg}\n\nYou can download packages manually from the web catalog."
        )

    def start_download_package(self):
        if self.available_combo.count() == 0:
            self.fetch_available_packages()
            return

        pkg = self.available_combo.currentData()
        if not pkg:
            return

        default_filename = f"translate-{pkg.from_code}_{pkg.to_code}-{pkg.package_version}.argosmodel"
        t = translation_dict[self.ui_lang]
        
        dest_path, _ = QFileDialog.getSaveFileName(
            self,
            t.get("download_package_file", "Save package to file (.argosmodel)..."),
            default_filename,
            "Argos Model (*.argosmodel)"
        )
        if not dest_path:
            return

        self.progress_dialog = QProgressDialog(
            f"Скачивание {pkg.from_code.upper()} → {pkg.to_code.upper()}..."
            if self.ui_lang == "Русский"
            else f"Downloading {pkg.from_code.upper()} → {pkg.to_code.upper()}...",
            "Отмена" if self.ui_lang == "Русский" else "Cancel",
            0,
            100,
            self
        )
        self.progress_dialog.setWindowTitle("QuickTranslate")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(200)

        self.download_thread = DownloadPackageThread(pkg, dest_path)
        self.download_thread.progress_signal.connect(self.on_download_progress)
        self.download_thread.finished_signal.connect(lambda ok, msg: self.on_download_finished(ok, msg, dest_path))
        self.progress_dialog.canceled.connect(self.download_thread.cancel)

        self.download_thread.start()

    def on_download_progress(self, current, total):
        if total > 0:
            percent = int((current / total) * 100)
            cur_mb = current / (1024 * 1024)
            tot_mb = total / (1024 * 1024)
            self.progress_dialog.setValue(percent)
            self.progress_dialog.setLabelText(f"{cur_mb:.1f} MB / {tot_mb:.1f} MB ({percent}%)")

    def on_download_finished(self, success, result, dest_path):
        self.progress_dialog.close()
        t = translation_dict[self.ui_lang]
        if success:
            reply = QMessageBox.question(
                self,
                "QuickTranslate",
                f"{t.get('package_saved_success', 'Package successfully saved to file!')}\n\n"
                f"{dest_path}\n\n"
                f"{t.get('install_now_prompt', 'Do you also want to install this package on this PC right now?')}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                try:
                    offline_translator.install_from_file(dest_path)
                    self.refresh_installed_list()
                    self.tab_widget.setCurrentIndex(0)
                    QMessageBox.information(self, "QuickTranslate", t.get('package_installed_success', 'Package successfully installed!'))
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to install package:\n{e}")
        else:
            if result != "cancelled":
                QMessageBox.critical(self, "Download Error", f"Ошибка скачивания пакета:\n{result}")


class SettingsDialog(QDialog):
    class HotkeyHandler(QObject):
        textChanged = Signal(str)

    """Диалог настроек."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("QuickTranslate", "Translator")
        ui_lang = self.settings.value("ui_lang", "English")
        t = translation_dict.get(ui_lang, translation_dict["English"])
        self.setWindowTitle(t["settings"])
        if parent:
            self.setWindowIcon(parent.windowIcon())
        self.setMinimumWidth(420)

        # Создаем выпадающие списки для выбора языка
        self.source_lang_combo = QComboBox()
        self.dest_lang_combo = QComboBox()
        self.source_lang_combo.addItem("Auto", "auto")
        for lang_code, lang_name in LANGUAGES.items():
            self.source_lang_combo.addItem(f"{lang_name} ({lang_code})", lang_code)
            self.dest_lang_combo.addItem(f"{lang_name} ({lang_code})", lang_code)

        # Выбор языка интерфейса
        self.ui_lang_combo = QComboBox()
        self.ui_lang_combo.addItems(["English", "Русский"])
        self.ui_lang_combo.currentIndexChanged.connect(self.on_ui_lang_changed)

        # Выбор службы перевода
        self.translator_combo = QComboBox()
        self.translator_combo.addItems(["googletrans", "deepl", "argos"])
        self.translator_combo.currentIndexChanged.connect(self.toggle_translator_widgets)

        # Ключ DeepL API
        self.deepl_api_key_input = QLineEdit()
        self.deepl_api_key_button = QPushButton(t["get_api_key"])
        self.deepl_api_key_button.setIcon(get_icon("key"))
        self.deepl_api_key_button.clicked.connect(self.open_deepl_website)

        # Кнопка офлайн-моделей Argos
        self.argos_packages_button = QPushButton(t["manage_packages"])
        self.argos_packages_button.setIcon(get_icon("package"))
        self.argos_packages_button.clicked.connect(self.open_offline_packages_dialog)

        # Чекбоксы
        self.buftranslate_checkbox = QCheckBox()
        self.autorun_checkbox = QCheckBox()
        
        # Размеры окна
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(100, 1000)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(50, 1000)
        
        # Настройка горячих клавиш (строго латиница)
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setReadOnly(True)
        self.hotkey_input.setAlignment(Qt.AlignCenter)
        self.hotkey_input.setCursor(QCursor(Qt.PointingHandCursor))
        self.hotkey_input.mousePressEvent = self.start_recording_hotkey

        self.hotkey_handler = SettingsDialog.HotkeyHandler()
        self.hotkey_handler.textChanged.connect(self.hotkey_input.setText)

        self._is_recording_hotkey = False
        self._previous_hotkey = "ctrl + b"
        self._hotkey_hook = None

        self.record_hotkey_btn = QPushButton(t.get("record_hotkey", "Record"))
        self.record_hotkey_btn.setIcon(get_icon("keyboard"))
        self.record_hotkey_btn.clicked.connect(self.start_recording_hotkey)

        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(self.hotkey_input, stretch=1)
        hotkey_layout.addWidget(self.record_hotkey_btn)

        # Размер истории
        self.history_size_spinbox = QSpinBox()
        self.history_size_spinbox.setRange(1, 50)

        # Разделитель и версия программы
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.software_version_label = QLabel(t["software_version"])
        self.software_version_label.setStyleSheet("color: gray; font-size: 11px;")
        
        # Метки формы для чистой локализации
        self.source_lang_label = QLabel()
        self.dest_lang_label = QLabel()
        self.width_label = QLabel()
        self.height_label = QLabel()
        self.hotkey_label = QLabel()
        self.ui_lang_label = QLabel()
        self.translator_label = QLabel()
        self.deepl_row_label = QLabel()
        self.argos_row_label = QLabel()
        self.history_size_label = QLabel()
        self.buftranslate_label = QLabel()
        self.autorun_label = QLabel()

        # Создаем форму для настроек
        form_layout = QFormLayout()
        self.form_layout = form_layout
        form_layout.addRow(self.source_lang_label, self.source_lang_combo)
        form_layout.addRow(self.dest_lang_label, self.dest_lang_combo)
        form_layout.addRow(self.width_label, self.width_spinbox)
        form_layout.addRow(self.height_label, self.height_spinbox)
        form_layout.addRow(self.hotkey_label, hotkey_layout)
        form_layout.addRow(self.ui_lang_label, self.ui_lang_combo)
        form_layout.addRow(self.translator_label, self.translator_combo)
        
        form_layout.addRow(self.deepl_row_label, self.deepl_api_key_input)
        form_layout.addRow("", self.deepl_api_key_button)
        form_layout.addRow(self.argos_row_label, self.argos_packages_button)
        form_layout.addRow(self.history_size_label, self.history_size_spinbox)
        form_layout.addRow(self.buftranslate_label, self.buftranslate_checkbox)
        form_layout.addRow(self.autorun_label, self.autorun_checkbox)
    
        # Кнопки управления настройками
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.ok_btn = QPushButton(t.get("save", "Save"))
        self.ok_btn.setIcon(get_icon("check"))
        self.ok_btn.clicked.connect(self.apply_and_save)
        btn_layout.addWidget(self.ok_btn)

        self.close_btn = QPushButton(t.get("close", "Close"))
        self.close_btn.setIcon(get_icon("close"))
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)
        self.cancel_btn = self.close_btn  # Совместимость

        # Общий макет
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.separator)
        main_layout.addWidget(self.software_version_label)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        
        self.load_settings()
        self.toggle_translator_widgets()
        self.retranslate_ui()

        # Запоминаем исходные настройки и блокируем кнопку сохранения
        self._initial_settings = self.get_settings()
        self.ok_btn.setEnabled(False)

        # Отслеживаем изменения для активации кнопки Сохранить
        self.source_lang_combo.currentIndexChanged.connect(self._check_for_changes)
        self.dest_lang_combo.currentIndexChanged.connect(self._check_for_changes)
        self.ui_lang_combo.currentIndexChanged.connect(self._check_for_changes)
        self.translator_combo.currentIndexChanged.connect(self._check_for_changes)
        self.width_spinbox.valueChanged.connect(self._check_for_changes)
        self.height_spinbox.valueChanged.connect(self._check_for_changes)
        self.hotkey_handler.textChanged.connect(self._check_for_changes)
        self.deepl_api_key_input.textChanged.connect(self._check_for_changes)
        self.buftranslate_checkbox.toggled.connect(self._check_for_changes)
        self.autorun_checkbox.toggled.connect(self._check_for_changes)
        self.history_size_spinbox.valueChanged.connect(self._check_for_changes)

    def on_ui_lang_changed(self):
        self.retranslate_ui()
        self._check_for_changes()

    def start_recording_hotkey(self, event=None):
        """Запуск перехвата клавиш строго в латинице."""
        if self._is_recording_hotkey:
            return
        self._is_recording_hotkey = True
        self._previous_hotkey = normalize_hotkey_to_latin(self.hotkey_input.text())
        hint = translation_dict[self.settings.value("ui_lang", "English")]["press_hotkey_hint"]
        self.hotkey_input.setText(hint)
        self.hotkey_input.setStyleSheet("border: 1px solid #3498db; color: #3498db; font-weight: bold;")

        pressed_modifiers = set()

        def on_event(e):
            if not self._is_recording_hotkey:
                return

            key_name = (e.name or "").lower().strip()
            if not key_name:
                return

            # Отмена записи по клавише Esc
            if key_name in ('esc', 'escape'):
                self._stop_recording_hotkey(self._previous_hotkey)
                return

            # Клавиша-модификатор
            if key_name in MODIFIER_KEYS:
                mod = MODIFIER_KEYS[key_name]
                if e.event_type == keyboard.KEY_DOWN:
                    pressed_modifiers.add(mod)
                    cur_mods = [m for m in ('ctrl', 'alt', 'shift', 'windows') if m in pressed_modifiers]
                    self.hotkey_handler.textChanged.emit(" + ".join(cur_mods) + " + ...")
                elif e.event_type == keyboard.KEY_UP:
                    pressed_modifiers.discard(mod)
                return

            # Обычная клавиша нажата
            if e.event_type == keyboard.KEY_DOWN:
                latin_key = normalize_key_to_latin(key_name)
                order = ['ctrl', 'alt', 'shift', 'windows']
                mods = [m for m in order if m in pressed_modifiers]
                if latin_key not in mods:
                    parts = mods + [latin_key]
                else:
                    parts = mods
                combo_str = " + ".join(parts)
                self._stop_recording_hotkey(combo_str)

        self._hotkey_hook = on_event
        keyboard.hook(on_event)

    def _stop_recording_hotkey(self, final_value):
        if not self._is_recording_hotkey:
            return
        self._is_recording_hotkey = False
        if self._hotkey_hook:
            try:
                keyboard.unhook(self._hotkey_hook)
            except Exception:
                pass
            self._hotkey_hook = None
        self.hotkey_input.setStyleSheet("")
        normalized = normalize_hotkey_to_latin(final_value)
        self.hotkey_handler.textChanged.emit(normalized)

    def closeEvent(self, event):
        self._stop_recording_hotkey(self._previous_hotkey)
        super().closeEvent(event)

    def reject(self):
        self._stop_recording_hotkey(self._previous_hotkey)
        super().reject()

    def load_settings(self):
        """Загружает настройки из QSettings."""
        source_lang = self.settings.value("source_lang", "en")
        dest_lang = self.settings.value("dest_lang", "ru")
        window_width = self.settings.value("window_width", 300, type=int)
        window_height = self.settings.value("window_height", 120, type=int)
        raw_hotkey = self.settings.value("hotkey", "ctrl + b")
        hotkey = normalize_hotkey_to_latin(raw_hotkey)
        ui_lang = self.settings.value("ui_lang", "English")
        translator = self.settings.value("translator", "googletrans")
        deepl_api_key = self.settings.value("deepl_api_key", "")
        buftranslate = self.settings.value("buftranslate", False, type=bool)
        autorun = self.settings.value("autorun", False, type=bool)
        history_size = self.settings.value("history_size", 5, type=int)
        
        index = self.source_lang_combo.findData(source_lang)
        if index >= 0:
            self.source_lang_combo.setCurrentIndex(index)
        index = self.dest_lang_combo.findData(dest_lang)
        if index >= 0:
            self.dest_lang_combo.setCurrentIndex(index)
        
        index = self.ui_lang_combo.findText(ui_lang)
        if index >= 0:
            self.ui_lang_combo.setCurrentIndex(index)
        
        index = self.translator_combo.findText(translator)
        if index >= 0:
            self.translator_combo.setCurrentIndex(index)

        self.width_spinbox.setValue(window_width)
        self.height_spinbox.setValue(window_height)
        
        self.hotkey_input.setText(hotkey)
        self._previous_hotkey = hotkey
        
        self.deepl_api_key_input.setText(deepl_api_key)
        self.buftranslate_checkbox.setChecked(buftranslate)
        self.autorun_checkbox.setChecked(autorun)
        self.history_size_spinbox.setValue(history_size)

    def save_settings(self):
        """Сохраняет настройки в QSettings."""
        self._stop_recording_hotkey(self.hotkey_input.text())
        
        self.settings.setValue("source_lang", self.source_lang_combo.currentData())
        self.settings.setValue("dest_lang", self.dest_lang_combo.currentData())
        self.settings.setValue("window_width", self.width_spinbox.value())
        self.settings.setValue("window_height", self.height_spinbox.value())
        
        # Горячая клавиша всегда строго нормализована в латиницу
        normalized_hotkey = normalize_hotkey_to_latin(self.hotkey_input.text())
        self.settings.setValue("hotkey", normalized_hotkey)
        
        self.settings.setValue("ui_lang", self.ui_lang_combo.currentText())
        self.settings.setValue("translator", self.translator_combo.currentText())
        self.settings.setValue("deepl_api_key", self.deepl_api_key_input.text())
        self.settings.setValue("buftranslate", self.buftranslate_checkbox.isChecked())
        self.settings.setValue("autorun", self.autorun_checkbox.isChecked())
        self.settings.setValue("history_size", self.history_size_spinbox.value())

    def apply_and_save(self):
        """Сохраняет настройки и применяет их без закрытия окна."""
        self.save_settings()
        new_settings = self.get_settings()
        self._initial_settings = dict(new_settings)

        # Применяем в работающем приложении
        parent = self.parent()
        if parent and hasattr(parent, 'apply_settings'):
            parent.apply_settings(new_settings)

        # Обновляем локализацию диалога
        self.retranslate_ui()

        # Визуальный эффект успешного сохранения
        current_ui_lang = self.ui_lang_combo.currentText()
        t = translation_dict.get(current_ui_lang, translation_dict["English"])
        self.ok_btn.setText(t.get("saved_feedback", "Saved!"))
        self.ok_btn.setEnabled(False)

        # Возвращаем стандартный текст кнопки через 1.5 сек
        QTimer.singleShot(1500, self._restore_save_button_text)

    def _restore_save_button_text(self):
        current_ui_lang = self.ui_lang_combo.currentText()
        t = translation_dict.get(current_ui_lang, translation_dict["English"])
        if not self.ok_btn.isEnabled():
            self.ok_btn.setText(t.get("save", "Save"))

    def _check_for_changes(self, *args):
        """Проверяет наличие изменений и активирует/блокирует кнопку сохранения."""
        if not hasattr(self, '_initial_settings'):
            return
        current = self.get_settings()
        has_changes = (current != self._initial_settings)
        self.ok_btn.setEnabled(has_changes)
        if has_changes:
            current_ui_lang = self.ui_lang_combo.currentText()
            t = translation_dict.get(current_ui_lang, translation_dict["English"])
            self.ok_btn.setText(t.get("save", "Save"))

    def accept(self):
        """Сохраняет настройки без закрытия окна."""
        self.apply_and_save()

    def get_settings(self):
        """Возвращает текущие настройки."""
        return {
            "source_lang": self.source_lang_combo.currentData(),
            "dest_lang": self.dest_lang_combo.currentData(),
            "window_width": self.width_spinbox.value(),
            "window_height": self.height_spinbox.value(),
            "hotkey": normalize_hotkey_to_latin(self.hotkey_input.text()),
            "ui_lang": self.ui_lang_combo.currentText(),
            "translator": self.translator_combo.currentText(),
            "deepl_api_key": self.deepl_api_key_input.text(),
            "buftranslate": self.buftranslate_checkbox.isChecked(),
            "autorun": self.autorun_checkbox.isChecked(),
            "history_size": self.history_size_spinbox.value()
        }
    
    def retranslate_ui(self):
        current_ui_lang = self.ui_lang_combo.currentText()
        t = translation_dict.get(current_ui_lang, translation_dict["English"])
        self.setWindowTitle(t["settings"])
        
        self.source_lang_label.setText(f"{t['source_lang']}:")
        self.dest_lang_label.setText(f"{t['dest_lang']}:")
        self.width_label.setText(f"{t['window_width']}:")
        self.height_label.setText(f"{t['window_height']}:")
        self.hotkey_label.setText(f"{t['hotkey']}:")
        self.ui_lang_label.setText(f"{t['ui_lang']}:")
        self.translator_label.setText(f"{t['translator']}:")
        self.deepl_row_label.setText(f"{t['deepl_api_key']}:")
        self.argos_row_label.setText(f"{t['offline_packages']}:")
        self.history_size_label.setText(f"{t['history_size']}:")
        self.buftranslate_label.setText(f"{t['buftranslate']}:")
        self.autorun_label.setText(f"{t['autorun']}:")

        self.deepl_api_key_button.setText(t["get_api_key"])
        self.argos_packages_button.setText(t["manage_packages"])
        self.record_hotkey_btn.setText(t.get("record_hotkey", "Record"))
        self.software_version_label.setText(t["software_version"])
        if not self.ok_btn.isEnabled() and self.ok_btn.text() != t.get("saved_feedback", "Saved!"):
            self.ok_btn.setText(t.get("save", "Save"))
        elif self.ok_btn.isEnabled():
            self.ok_btn.setText(t.get("save", "Save"))
        self.close_btn.setText(t.get("close", "Close"))
    
    def toggle_translator_widgets(self):
        selected = self.translator_combo.currentText()
        is_deepl = (selected == "deepl")
        is_argos = (selected == "argos")
        self.deepl_api_key_input.setVisible(is_deepl)
        self.deepl_api_key_button.setVisible(is_deepl)
        self.deepl_row_label.setVisible(is_deepl)
        self.argos_packages_button.setVisible(is_argos)
        self.argos_row_label.setVisible(is_argos)

    def open_offline_packages_dialog(self):
        dialog = OfflinePackagesDialog(self, ui_lang=self.ui_lang_combo.currentText())
        dialog.exec()
        
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
        try:
            self.translator = Translator()
        except Exception as e:
            logging.warning(f"Could not initialize googletrans Translator: {e}")
            self.translator = None
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

        self.hotkey = normalize_hotkey_to_latin(self.hotkey)
        self.translation_requested.connect(self.translate_selected_text)
        self.close_requested.connect(self.hide_window)

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
        
        self.additional_lang_label = QLabel(translation_dict[self.ui_lang]["additional_translate"])
        self.additional_lang_combo_layout = QHBoxLayout()
        self.additional_lang_combo_layout.addWidget(self.additional_lang_label)
        self.additional_lang_combo_layout.addWidget(self.additional_lang_combo)
        
        layout.addWidget(self.text_edit)
        layout.addLayout(self.additional_lang_combo_layout)
        self.setLayout(layout)
        
        logging.info("UI initialized.")
    
    def retranslate_ui(self):
        # Retranslate all the labels in the application
        if self.ui_lang in self.translation_dict:
            t = self.translation_dict[self.ui_lang]
            self.setWindowTitle("QuickTranslate")
            
            if hasattr(self, 'tray_menu'):
                actions = self.tray_menu.actions()
                if len(actions) >= 4:
                    actions[0].setText(t["settings"])
                    actions[1].setText(t["history"])
                    actions[2].setText(t["show"])
                    actions[-1].setText(t["exit"])
            if hasattr(self, 'additional_lang_label'):
                self.additional_lang_label.setText(t["additional_translate"])

    def initTrayIcon(self):
        """Инициализация иконки в трее с векторными иконками меню."""
        icon_path = resource_path('extension.png')
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(41, 128, 185))
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 16, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "Q")
            painter.end()
            icon = QIcon(pixmap)

        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_menu = QMenu()

        # Действие для открытия окна настроек
        settings_action = QAction(translation_dict[self.ui_lang]["settings"], self)
        settings_action.setIcon(get_icon("settings"))
        settings_action.triggered.connect(self.open_settings)
        self.tray_menu.addAction(settings_action)

        # Действие для открытия окна истории
        history_action = QAction(translation_dict[self.ui_lang]["history"], self)
        history_action.setIcon(get_icon("history"))
        history_action.triggered.connect(self.open_history)
        self.tray_menu.addAction(history_action)

        # Действие для показа окна
        show_action = QAction(translation_dict[self.ui_lang]["show"], self)
        show_action.setIcon(get_icon("show"))
        show_action.triggered.connect(self.show_window)
        self.tray_menu.addAction(show_action)

        self.tray_menu.addSeparator()

        # Действие для выхода
        exit_action = QAction(translation_dict[self.ui_lang]["exit"], self)
        exit_action.setIcon(get_icon("exit"))
        exit_action.triggered.connect(self.close_app)
        self.tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        logging.info("Tray icon initialized.")

        # Уведомление пользователю при запуске
        msg = translation_dict[self.ui_lang].get(
            "started_notification",
            "QuickTranslate работает в фоне.\nВыделите текст и нажмите горячую клавишу для перевода."
        )
        self.tray_icon.showMessage("QuickTranslate", msg, QSystemTrayIcon.Information, 3500)
    
    def translate_google(self, text, src, dest):
        try:
             if not self.translator:
                 return "Ошибка: googletrans не инициализирован."
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

    def translate_offline(self, text, src, dest):
        try:
            return offline_translator.translate_offline(text, src, dest)
        except Exception as e:
            return f"Ошибка офлайн-перевода: {e}"

    def translate_text(self, text, dest_lang = None):
        logging.info(f"Translating text: {text}")
        if not text or not isinstance(text, str):
            logging.warning("No text provided for translation or text is not string.")
            return None

        if self.translator_type == "argos":
            if self.source_lang == "auto":
                source_lang = offline_translator.detect_offline(text)
            else:
                source_lang = self.source_lang
        else:
            if self.source_lang == "auto":
                try:
                    if self.translator:
                        detected = self.translator.detect(text)
                        source_lang = detected.lang
                    else:
                        source_lang = "en"
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
            elif self.translator_type == "argos":
                  translation = self.translate_offline(text, source_lang, dest_lang)
            else:
                 return "Выберите переводчика"
            logging.info(f"Translation successful: {translation}")
            
            # Detect languages after translation for history
            if self.translator_type == "argos":
                src_lang = source_lang.upper()
                dest_lang_upper = dest_lang.upper()
            else:
                if self.source_lang == "auto" and self.translator:
                    try:
                        detected_src = self.translator.detect(text)
                        src_lang = detected_src.lang.upper()
                    except Exception:
                        src_lang = source_lang.upper()
                else:
                    src_lang = self.source_lang.upper()
                
                if dest_lang == self.dest_lang and self.translator:
                    try:
                        detected_dest = self.translator.detect(translation)
                        dest_lang_upper = detected_dest.lang.upper()
                    except Exception:
                        dest_lang_upper = dest_lang.upper()
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
            if self.translator_type == "argos":
                if self.source_lang == "auto":
                    return True
                detected_lang = offline_translator.detect_offline(text)
                return detected_lang == self.source_lang
            try:
                if not self.translator:
                    return True
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

    def apply_settings(self, settings):
        """Применяет новые настройки к работающему приложению."""
        logging.info(f"Applying settings: {settings}")

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
            elif hasattr(self, 'clipboard_timer'):
                self.clipboard_timer.stop()
        # Autorun
        if settings["autorun"] != self.get_autorun():
            self.set_autorun(settings["autorun"])
        
        # History size
        self.history_size = settings["history_size"]

        # Обновляем размеры окна
        self.resize(self.window_width, self.window_height)
        # Переназначаем горячую клавишу
        self.initHotkey(self.hotkey)
        self.retranslate_ui()
        self._settings = settings
        logging.info("Settings applied successfully.")

    def open_settings(self):
        """Открывает диалог настроек."""
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()
    
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
        """Инициализирует горячую клавишу (строго латиница)."""
        keyboard.unhook_all()

        hotkey = normalize_hotkey_to_latin(hotkey)
        self.hotkey = hotkey

        def on_hotkey():
            self.translation_requested.emit()

        def on_esc():
            self.close_requested.emit()
        
        try:
            keyboard.add_hotkey(hotkey, on_hotkey)
            keyboard.add_hotkey('esc', on_esc)
            logging.info(f"New hotkey set: {hotkey}")
        except Exception as e:
            logging.error(f"Failed to register hotkey {hotkey}: {e}")
            try:
                keyboard.add_hotkey("ctrl + b", on_hotkey)
                keyboard.add_hotkey('esc', on_esc)
            except Exception:
                pass

    
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
    hotkey = normalize_hotkey_to_latin(settings.value("hotkey", "ctrl+b"))
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