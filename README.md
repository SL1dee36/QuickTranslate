# QuickTranslate: A Desktop Translation Tool

QuickTranslate is a simple desktop application that allows you to quickly translate selected text using Google Translate. It sits in your system tray and activates with a customizable hotkey. The translated text is displayed in a small window that appears near your cursor.

[download latest version here.](https://github.com/SL1dee36/QuickTranslate/releases/)

## Features

*   **Instant Translation:** Translates selected text from any application.
*   **Customizable Hotkey:**  Trigger the translation with a configurable keyboard shortcut.
*   **Language Selection:** Choose your source and destination languages.
*   **System Tray Integration:** Runs in the background and minimizes to the system tray.
*   **Always on Top:** The translation window stays on top of other windows.
*   **Clipboard Copy:**  Clicking the translated text will copy it to your clipboard.
*   **Configurable Window Size:** Set the width and height of the translation window.
*   **Automatic Language Detection:** Detects if the selected text is in the source language before attempting translation.
*   **Error Handling:**  Provides error messages for translation failures.
*   **Settings Persistence:** Saves your settings between sessions.

## Getting Started

### Prerequisites

*   Python 3.6 or higher
*   `PySide6` library
*   `googletrans` library
*   `pyperclip` library
*   `keyboard` library
*   `pypiwin32` library

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Sl1dee36/QuickTranslate.git
    cd QuickTranslate
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install PySide6 googletrans pyperclip keyboard pypiwin32
    ```

3.  **Run the application:**
    ```bash
    python qtranslate.py
    ```

## Usage

1.  The application will start in your system tray.
2.  **Configure settings:** Right-click the tray icon and select "Settings".
    *   Set the source and destination languages.
    *   Set the desired window width and height.
    *   Set the hotkey for translation. Click on the `Hotkey` field and press your desired keyboard shortcut.
3.  **Translate text:**
    *   Select the text in any application.
    *   Press the assigned hotkey (default: `ctrl+b`).
    *   The translation will appear in a small window near your mouse cursor.
4.  **Copy the translation:** Click on the translated text to copy it to your clipboard and close the translation window.
5.  **Hide window:** Press ESC to close translation window.
6.  **Exit the app:** Right-click the tray icon and select "Exit".

## Configuration

All settings are saved in a configuration file using `QSettings`, ensuring your preferences are remembered between sessions. The settings include:

*   `source_lang`: Language code for the source language (e.g., 'en', 'ru').
*   `dest_lang`: Language code for the destination language (e.g., 'ru', 'en').
*   `window_width`: Width of the translation window.
*   `window_height`: Height of the translation window.
*   `hotkey`: Keyboard shortcut for triggering translation.

## Contributing

Contributions are welcome! If you have suggestions or find bugs, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

*   [Sl1dee36](https://github.com/Sl1dee36)

## Screenshots

![{1EE4999E-08EC-43EA-BF86-042484B9B678}](https://github.com/user-attachments/assets/c5b547c1-2003-4209-83ec-d5e61dcae9a3)

![{466299DB-E60E-44B9-B5B9-2876895E49C8}](https://github.com/user-attachments/assets/ee48eb9f-a9d4-429b-953e-c70b6c513bcf)    ![{583313B7-AD1F-4A20-A739-CDEC972847C0}](https://github.com/user-attachments/assets/2c481d11-edae-4dfb-a022-7565fda160b4)


