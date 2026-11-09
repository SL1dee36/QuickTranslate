"""
Offline translation module using Argos Translate.
Allows downloading .argosmodel packages to files, transferring them
to air-gapped computers, and performing 100% offline machine translation.
"""

import os
import re
import sys
import types
import shutil
import logging
from pathlib import Path
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

# Lightweight sentence boundary detection mock for Stanza
class _DummySentence:
    def __init__(self, text):
        self.text = text

class _DummyDoc:
    def __init__(self, text):
        parts = [s.strip() for s in re.split(r'(?<=[.!?…\n])\s+', text) if s.strip()]
        self.sentences = [_DummySentence(s) for s in (parts if parts else [text])]

class _DummyStanzaPipeline:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, text):
        return _DummyDoc(text)

# Mock unused heavy NLP packages BEFORE importing argostranslate
# This prevents importing PyTorch, SpaCy, and Stanza which are not needed for CTranslate2 inference
for mod_name in ('stanza', 'spacy', 'torch'):
    if mod_name not in sys.modules or sys.modules[mod_name] is None:
        dummy = types.ModuleType(mod_name)
        if mod_name == 'stanza':
            dummy.Pipeline = _DummyStanzaPipeline
        sys.modules[mod_name] = dummy

# Check Argos availability
ARGOS_AVAILABLE = False
try:
    import argostranslate.package
    import argostranslate.translate
    import argostranslate.settings
    ARGOS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Argos Translate is not available: {e}")


def is_available() -> bool:
    """Check if Argos Translate engine is installed and ready."""
    return ARGOS_AVAILABLE


def get_packages_dir() -> Path:
    """Get the directory where installed language models are stored."""
    if not ARGOS_AVAILABLE:
        return Path(os.path.expanduser("~/.local/share/argos-translate/packages"))
    return argostranslate.settings.package_data_dir


def get_installed_packages():
    """Return a list of installed package information dictionaries."""
    if not ARGOS_AVAILABLE:
        return []
    try:
        packages = argostranslate.package.get_installed_packages()
        result = []
        for p in packages:
            result.append({
                "from_code": p.from_code,
                "from_name": getattr(p, "from_name", p.from_code),
                "to_code": p.to_code,
                "to_name": getattr(p, "to_name", p.to_code),
                "version": getattr(p, "package_version", "1.0"),
                "pkg": p
            })
        return result
    except Exception as e:
        logger.error(f"Error getting installed packages: {e}")
        return []


def install_from_file(file_path: str) -> bool:
    """Install a .argosmodel package from a local file path."""
    if not ARGOS_AVAILABLE:
        raise RuntimeError("Argos Translate library is not installed.")
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.lower().endswith(".argosmodel") and not file_path.lower().endswith(".zip"):
        raise ValueError("Package file must be a .argosmodel file.")
    
    argostranslate.package.install_from_path(path)
    # Refresh cache
    argostranslate.translate.load_installed_languages()
    return True


def uninstall_package(pkg) -> bool:
    """Uninstall an installed package."""
    if not ARGOS_AVAILABLE:
        raise RuntimeError("Argos Translate library is not installed.")
    
    argostranslate.package.uninstall(pkg)
    argostranslate.translate.load_installed_languages()
    return True


def get_available_packages():
    """
    Fetch the list of packages available for download online.
    Requires an internet connection.
    """
    if not ARGOS_AVAILABLE:
        raise RuntimeError("Argos Translate library is not installed.")
    
    argostranslate.package.update_package_index()
    packages = argostranslate.package.get_available_packages()
    return packages


def download_package_to_file(pkg, destination_path: str, progress_callback=None, cancel_check=None):
    """
    Download an available package to a local .argosmodel file.
    
    Args:
        pkg: AvailablePackage instance or direct download URL string.
        destination_path: Where to save the file.
        progress_callback: Optional callable(downloaded_bytes, total_bytes)
        cancel_check: Optional callable() returning True if download should be cancelled.
    """
    if isinstance(pkg, str):
        url = pkg
    else:
        if not hasattr(pkg, "links") or not pkg.links:
            raise ValueError("No download links found in package.")
        url = pkg.links[0]
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) QuickTranslate/1.2"}
    )
    
    dest_path = Path(destination_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    temp_path = dest_path.with_suffix(".argosmodel.tmp")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response, open(temp_path, "wb") as out_file:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 1024 * 128  # 128 KB
            
            while True:
                if cancel_check and cancel_check():
                    out_file.close()
                    if temp_path.exists():
                        temp_path.unlink()
                    raise InterruptedError("Download cancelled by user.")
                
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                
                if progress_callback:
                    progress_callback(downloaded, total_size)
        
        # Rename temp to destination
        if dest_path.exists():
            dest_path.unlink()
        temp_path.rename(dest_path)
        return True
    except Exception as e:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        raise e


def detect_offline(text: str) -> str:
    """
    Ultra-fast heuristic offline language detection without network calls.
    Detects Cyrillic, Latin, and common European variants.
    """
    if not text:
        return "en"
    
    cyrillic_count = len(re.findall(r"[\u0400-\u04FF]", text))
    latin_count = len(re.findall(r"[a-zA-Z]", text))
    
    # German specific: ä ö ü ß
    german_count = len(re.findall(r"[äöüßÄÖÜ]", text))
    # French specific: é à è ù â ê î ô û ë ï ü ÿ ç
    french_count = len(re.findall(r"[éàèùâêîôûëïüÿçÉÀÈÙÂÊÎÔÛËÏÜŸÇ]", text))
    # Spanish specific: ñ á é í ó ú
    spanish_count = len(re.findall(r"[ñáéíóú¿¡ÑÁÉÍÓÚ]", text))
    # Chinese
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    
    if cjk_count > 0 and cjk_count >= latin_count and cjk_count >= cyrillic_count:
        return "zh"
    
    if cyrillic_count > latin_count:
        return "ru"
    
    if german_count > 1 and german_count > french_count and german_count > spanish_count:
        return "de"
    if french_count > 1 and french_count > german_count and french_count > spanish_count:
        return "fr"
    if spanish_count > 1 and spanish_count > german_count and spanish_count > french_count:
        return "es"
        
    if latin_count > 0:
        return "en"
    
    return "en"


def translate_offline(text: str, from_code: str, to_code: str) -> str:
    """
    Perform offline translation using Argos Translate.
    
    Args:
        text: Input string to translate.
        from_code: Source language code (e.g. 'en', 'ru') or 'auto'.
        to_code: Target language code (e.g. 'ru', 'en').
        
    Returns:
        Translated string or error message.
    """
    if not ARGOS_AVAILABLE:
        return "Ошибка: Библиотека argostranslate не установлена."
    
    if not text or not text.strip():
        return ""
    
    # Handle 'auto'
    if from_code == "auto":
        from_code = detect_offline(text)
    
    from_code = from_code.lower()
    to_code = to_code.lower()
    
    if from_code == to_code:
        return text
    
    try:
        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang = next((l for l in installed_languages if l.code.lower() == from_code), None)
        to_lang = next((l for l in installed_languages if l.code.lower() == to_code), None)
        
        if not from_lang:
            return (
                f"Офлайн-модель для исходного языка «{from_code.upper()}» пока не установлена.\n\n"
                f"Установите файл пакета (.argosmodel) в меню:\n"
                f"Настройки → Офлайн-модели."
            )
        if not to_lang:
            return (
                f"Офлайн-модель для языка перевода «{to_code.upper()}» пока не установлена.\n\n"
                f"Установите файл пакета (.argosmodel) в меню:\n"
                f"Настройки → Офлайн-модели."
            )
            
        translation = from_lang.get_translation(to_lang)
        if not translation:
            # Проверяем, установлен ли обратный пакет, чтобы дать понятную памятку
            reverse_trans = to_lang.get_translation(from_lang) if to_lang else None
            hint = ""
            if reverse_trans:
                hint = (
                    f"\n\nПамятка: у вас установлена модель «{to_code.upper()} → {from_code.upper()}».\n"
                    f"Языковые модели работают строго в одну сторону.\n"
                    f"Для перевода с {from_code.upper()} на {to_code.upper()} нужен отдельный пакет «{from_code.upper()} → {to_code.upper()}»."
                )
            return (
                f"Офлайн-модель {from_code.upper()} → {to_code.upper()} не найдена.{hint}\n\n"
                f"Скачайте и установите пакет через Настройки → Офлайн-модели."
            )
            
        return translation.translate(text)
    except Exception as e:
        logger.error(f"Argos offline translation error: {e}", exc_info=True)
        return f"Ошибка офлайн-перевода: {e}"

