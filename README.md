# OCR-Translator

## Overview
This app does 2 things
- OCR: Scan the selected area to extract the text 
- Translator: Get the text and feed it to Google Translate API 

## Install
- Download Python 3.13 (Must be 3.13): https://www.python.org/downloads/release/python-31313/ 
    - Scroll down and find `Windows installer (64-bit)`, download it and install 
    - What is Python? It is the language and environment to run this app

- Then open any terminal (Terminal is the box that allow you to type command in) and run these commands one by one   
    - Command Prompt (The built-in terminal of Windows, please use this if you don't have or don't want to install Git Bash)
    ```
    python -m venv venv3
    venv\Scripts\activate.bat
    python -m pip install -r requirements.txt
    ```

    - Git Bash
    ```
    python -m venv venv3
    source venv/Scripts/activate
    python -m pip install -r requirements.txt
    ```


## You want to change ocr source language and translator source language?
- Find the line "# CONFIG HERE" in `main.py`
- Then change `ocr_src_lang` and ` translator_src_lang` (remember to put the value inside `''`)

## Run 

```
python main.py
```

## How to use 
We have 3 buttons
- Select Area: Click the button first, then select the area on screen that you want to capture text
- Clear: Clear all text inside the text box (Just to make it nicer, no special function) 
- Translate Selection: Sometimes you want to copy and paste text instead of "select area" and rely on OCR. Paste the text to the text box, then use mouse to select it, then click this button for translation.

## Tips
- You should select the entire speech bubble, not each line (or column) separately. The idea is that if those lines (or columns) are meant to be read together, you should select them together.
- If the translation sounds weird, it’s likely that the selected area is off, or that you included too many or too few lines. Please try selecting again.

