import datetime
import time
from colorama import Fore, Back, Style

_show_error = True
_show_warning = True
_show_info = True
_show_debug = True


def fprint(text, EOL=True):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
    endchar = ''
    if EOL:
        endchar = '\n\r'
    print(f'[{timestamp: <23}] {text}\r', end=endchar,flush=True )

def error(text, EOL=True):
    if _show_error:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        title = f"Error"
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <23}] {Back.RED}{Fore.BLACK}{title: ^10}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )

def warning(text, EOL=True):
    if _show_warning:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        title = f"Warning"
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <23}] {Back.YELLOW}{Fore.BLACK}{title: ^10}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )

def info(text, EOL=True):
    if _show_info:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        title = f"Info"
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <23}] {Back.GREEN}{Fore.BLACK}{title: ^10}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )

def debug(text,source="debug", EOL=True):
    if _show_debug:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <23}] {Back.MAGENTA}{Fore.BLACK}{source: ^10}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )


def spinner(text, delay=0.2):
    spinner = ['/','-','\\','|']
    for char in spinner:
        fprint(f'{text} {char}',EOL=False)
        time.sleep(delay) 
