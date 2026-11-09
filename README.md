# QuickTranslate: A Desktop Translation Tool

QuickTranslate is a lightweight desktop translator. Highlight text anywhere, press a hotkey, and get a translation popup right next to your cursor. Works with Google Translate, DeepL, and offline Argos models.

<a href="https://github.com/SL1dee36/QuickTranslate/releases/latest">
    <img alt="Static Badge" src="https://img.shields.io/badge/Download_Latest_QuickTranslate-blue?logo=Hack%20The%20Box&link=https%3A%2F%2Fgithub.com%2FSL1dee36%2FQuickTranslate%2Freleases%2Flatest">
</a>

## Screenshots

![{9E21A9C1-FDD2-4017-86A3-B81846CDE2E0}](https://github.com/user-attachments/assets/35491cae-cf68-4fc5-a498-0ce62c9a5485)

## Features

* **Instant Translation:** Translates selected text from any application.
* **Multiple Translators:** Choose between Google Translate, DeepL, and **Argos Translate (Offline)**.
* **Offline Mode:** Download language packs (`.argosmodel`) to a file on a PC with internet, copy them to a flash drive, and install on an offline PC without network access!
* **Customizable Hotkey:** Trigger the translation with a configurable keyboard shortcut.
* **Language Selection:** Set your source and destination languages, including the option for auto-detect.
* **UI Language Support:** Choose the language for the application's user interface.
* **System Tray Integration:** Runs in the background and minimizes to the system tray.
* **Always on Top:** The translation window stays on top of other windows.
* **Clipboard Copy:** Clicking the translated text will copy it to your clipboard.
* **Configurable Window Size:** Set the width and height of the translation window.
* **Automatic Language Detection:** Detects if the selected text is in the source language before attempting translation (both online and offline).
* **Error Handling:** Provides error messages for translation failures.
* **Settings Persistence:** Saves your settings between sessions.
* **Auto-Translate Clipboard:** Optionally translates text copied to the clipboard automatically.
* **Run on Startup:** Set the application to run automatically when your system starts.

## Getting Started

### Prerequisites

* Python 3.8 or higher
* `PySide6` library
* `argostranslate` library (for offline translation)
* `googletrans` library
* `pyperclip` library
* `keyboard` library
* `pypiwin32` library
* `deepl` library (if using DeepL translator)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Sl1dee36/QuickTranslate.git
    cd QuickTranslate
    ```

2. **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application:**

    ```bash
    python qtranslate.py
    ```

## Offline Translation

QuickTranslate supports completely offline neural translation using **Argos Translate**:

1. **On a PC with Internet:**
    * Open **Settings**.
    * Select **`argos`** in the **Translator** dropdown.
    * Click **`Manage offline models...`**.
    * Go to the **`Download for offline use`** tab, select the language pair (e.g. `English → Russian`), and click **`Save selected model to file...`**.
    * Save the `.argosmodel` file to your USB drive.
2. **On an Offline PC:**
    * Copy the `.argosmodel` file from your USB drive.
    * Open **Settings** -> **`Manage offline models...`** in QuickTranslate.
    * On the **`Installed models`** tab, click **`Install model from file (.argosmodel)...`** and select the file.
    * Select **`argos`** as the translation engine.
    * Now you can translate texts with `Ctrl+B` completely offline without any internet connection!

> [!TIP]
> Translation models are one-way. For instance, `Russian → English` only translates from Russian into English. For full two-way translation, install both packages (`English → Russian` and `Russian → English`).

## Building and Distribution

Build scripts and packaging configurations are located in the `utils/` folder:

### 1. Standalone Build + Windows Installer (Recommended)

Compiles the application into a standalone folder and packages it into a clean Windows installer (`QuickTranslate_Setup_v1.2.0.exe`) using Inno Setup:

```powershell
.\utils\build_standalone_installer.ps1
```

*(or run `.\utils\build_standalone_installer.bat`)*

Output: `dist\installer\QuickTranslate_Setup_v1.2.0.exe`

### 2. Single Portable Executable (Onefile)

Compiles everything into a single standalone `.exe` that can be transferred and run anywhere without dependencies:

```powershell
.\utils\build_onefile.ps1
```

*(or run `.\utils\build_onefile.bat`)*

Output: `dist\QuickTranslate.exe`

> [!NOTE]
> The `--nofollow-import-to=torch` flag prevents Nuitka from unnecessarily compiling PyTorch, saving ~1.5 GB of size and over an hour of compilation time.

## Usage

1. The application will start in your system tray.
2. **Configure settings:** Right-click the tray icon and select "Settings".
    * Set the source and destination languages. You can select "Auto" for automatic source language detection.
    * Set the desired window width and height.
    * Set the desired UI language.
    * Set the hotkey for translation. Click on the `Hotkey` field and press your desired keyboard shortcut.
    * Choose the desired translator from `googletrans` and `deepl`.
    * If you are using DeepL, paste your DeepL API Key in `DeepL API Key` field.
    * You can enable the automatic translation of the text copied in clipboard by checking the `Auto-Translate Clipboard` checkbox.
    * If you want the application to start automatically when you login into the system, check the `Run on startup` checkbox.
3. **Translate text:**
    * Select the text in any application.
    * Press the assigned hotkey (default: `ctrl+b`).
    * The translation will appear in a small window near your mouse cursor.
4. **Copy the translation:** Click on the translated text to copy it to your clipboard and close the translation window.
5. **Hide window:** Press ESC to close the translation window.
6. **Exit the app:** Right-click the tray icon and select "Exit".

## Configuration

All settings are saved in a configuration file using `QSettings`, ensuring your preferences are remembered between sessions. The settings include:

* `source_lang`: Language code for the source language (e.g., 'en', 'ru', 'auto').
* `dest_lang`: Language code for the destination language (e.g., 'ru', 'en').
* `window_width`: Width of the translation window.
* `window_height`: Height of the translation window.
* `hotkey`: Keyboard shortcut for triggering translation.
* `ui_lang`: The language of the application interface (e.g., "English", "Русский").
* `translator`: The translator to use ("googletrans", "deepl").
* `deepl_api_key`: The API key for the DeepL translator.
* `buftranslate`: Boolean value indicating if auto-translate clipboard is enabled
* `autorun`: Boolean value indicating if application will start on login

## Contributing

Contributions are welcome! If you have suggestions or find bugs, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
