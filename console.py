import datetime
from glob import glob
import time
from colorama import Fore, Back, Style

_show_error = True
_show_warning = True
_show_info = True
_show_debug = True

bool_as_int = lambda x : 1 if ( x ) else 0

def fprint(text, EOL=True):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
    endchar = ''
    if EOL:
        endchar = '\n\r'
    print(f'[{timestamp: <23}] {text}\r', end=endchar,flush=True )

# Functions to manipulate the outputs
def hide_errors(state = False):
    global _show_error
    _show_error = state

def hide_warnings(state = False):
    global _show_warning
    _show_warning = state

def hide_info(state = False):
    global _show_info
    _show_info = state

def hide_debug(state = False):
    global _show_debug
    _show_debug = state


# output functions
def error(text, EOL=True):
    global _show_error
    if _show_error:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        title = f"Error"
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <23}] {Back.RED}{Fore.BLACK}{title: ^10}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )

def warning(text, EOL=True):
    global _show_warning
    if _show_warning:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        title = f"Warning"
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <23}] {Back.YELLOW}{Fore.BLACK}{title: ^10}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )

def info(text, EOL=True):
    global _show_info
    if _show_info:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        title = f"Info"
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <23}] {Back.GREEN}{Fore.BLACK}{title: ^10}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )

def debug(text,source="debug", EOL=True):
    global _show_debug
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
