# QuickTranslate: A Desktop Translation Tool

QuickTranslate is a versatile desktop application designed to streamline your translation needs. It allows you to quickly translate selected text using either Google Translate or DeepL, and offers a range of customizable features. The application operates from your system tray and is activated with a customizable hotkey. The translated text is displayed in a small window that appears near your cursor.

![Static Badge](https://img.shields.io/badge/Download_Latest_QuickTranslate-blue?logo=Hack%20The%20Box&link=https://github.com/SL1dee36/QuickTranslate/releases/latest)

## Features

*   **Instant Translation:** Translates selected text from any application.
*   **Multiple Translators:** Choose between Google Translate and DeepL for translations.
*   **Customizable Hotkey:** Trigger the translation with a configurable keyboard shortcut.
*   **Language Selection:** Set your source and destination languages, including the option for auto-detect.
*   **UI Language Support:** Choose the language for the application's user interface.
*   **System Tray Integration:** Runs in the background and minimizes to the system tray.
*   **Always on Top:** The translation window stays on top of other windows.
*   **Clipboard Copy:** Clicking the translated text will copy it to your clipboard.
*   **Configurable Window Size:** Set the width and height of the translation window.
*   **Automatic Language Detection:** Detects if the selected text is in the source language before attempting translation.
*   **Error Handling:** Provides error messages for translation failures.
*   **Settings Persistence:** Saves your settings between sessions.
*   **Auto-Translate Clipboard:** Optionally translates text copied to the clipboard automatically.
*   **Run on Startup:** Set the application to run automatically when your system starts.

## Getting Started

### Prerequisites

*   Python 3.6 or higher
*   `PySide6` library
*   `googletrans` library
*   `pyperclip` library
*   `keyboard` library
*   `pypiwin32` library
*   `deepl` library (if using DeepL translator)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Sl1dee36/QuickTranslate.git
    cd QuickTranslate
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install PySide6 googletrans pyperclip keyboard pypiwin32 deepl
    ```

3.  **Run the application:**
    ```bash
    python qtranslate.py
    ```

## Usage

1.  The application will start in your system tray.
2.  **Configure settings:** Right-click the tray icon and select "Settings".
    *   Set the source and destination languages. You can select "Auto" for automatic source language detection.
    *   Set the desired window width and height.
    *    Set the desired UI language.
    *   Set the hotkey for translation. Click on the `Hotkey` field and press your desired keyboard shortcut.
    *    Choose the desired translator from `googletrans` and `deepl`.
    *    If you are using DeepL, paste your DeepL API Key in `DeepL API Key` field.
    *    You can enable the automatic translation of the text copied in clipboard by checking the `Auto-Translate Clipboard` checkbox.
    *    If you want the application to start automatically when you login into the system, check the `Run on startup` checkbox.
3.  **Translate text:**
    *   Select the text in any application.
    *   Press the assigned hotkey (default: `ctrl+b`).
    *   The translation will appear in a small window near your mouse cursor.
4.  **Copy the translation:** Click on the translated text to copy it to your clipboard and close the translation window.
5.  **Hide window:** Press ESC to close the translation window.
6.  **Exit the app:** Right-click the tray icon and select "Exit".

## Configuration

All settings are saved in a configuration file using `QSettings`, ensuring your preferences are remembered between sessions. The settings include:

*   `source_lang`: Language code for the source language (e.g., 'en', 'ru', 'auto').
*   `dest_lang`: Language code for the destination language (e.g., 'ru', 'en').
*   `window_width`: Width of the translation window.
*   `window_height`: Height of the translation window.
*   `hotkey`: Keyboard shortcut for triggering translation.
*   `ui_lang`: The language of the application interface (e.g., "English", "Русский").
*    `translator`: The translator to use ("googletrans", "deepl").
*    `deepl_api_key`: The API key for the DeepL translator.
*   `buftranslate`: Boolean value indicating if auto-translate clipboard is enabled
*   `autorun`: Boolean value indicating if application will start on login

## Contributing

Contributions are welcome! If you have suggestions or find bugs, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

*   [Sl1dee36](https://github.com/Sl1dee36)

## Screenshots

![{9E21A9C1-FDD2-4017-86A3-B81846CDE2E0}](https://github.com/user-attachments/assets/35491cae-cf68-4fc5-a498-0ce62c9a5485)

<details>
    
<summary>Previous versions</summary>
    
![{1EE4999E-08EC-43EA-BF86-042484B9B678}](https://github.com/user-attachments/assets/c5b547c1-2003-4209-83ec-d5e61dcae9a3)

![{466299DB-E60E-44B9-B5B9-2876895E49C8}](https://github.com/user-attachments/assets/ee48eb9f-a9d4-429b-953e-c70b6c513bcf)    ![{583313B7-AD1F-4A20-A739-CDEC972847C0}](https://github.com/user-attachments/assets/2c481d11-edae-4dfb-a022-7565fda160b4)

</details>
