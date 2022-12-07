# @07122022^MB Added:
#                    + option to change the style
#                    + notice output
#                    + info_spinnner


import datetime
from glob import glob
import time
from colorama import Fore, Back, Style

_show_error = True
_show_warning = True
_show_info = True
_show_debug = True
_show_notice = True

_timestamp_width = 23
_title_width = 10

bool_as_int = lambda x : 1 if ( x ) else 0

def fprint(text, EOL=True):
    global _title_width, _timestamp_width
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
    endchar = ''
    if EOL:
        endchar = '\n\r'
    print(f'[{timestamp: <{_title_width}}] {text}\r', end=endchar,flush=True )

# configure output style eg widths 
def console_style_config(timestamp_w, title_w):
    global _title_width, _timestamp_width
    _timestamp_width = timestamp_w
    _title_width = title_w

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

def hide_notice(state = False):
    global _show_notice
    _show_notice = state

# output functions
def error(text, title = f"Error",EOL=True):
    global _show_error, _title_width, _timestamp_width
    if _show_error:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <{_timestamp_width}}] {Back.RED}{Fore.BLACK}{title: ^{_title_width}}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )

def warning(text, title="Warning", EOL=True):
    global _show_warning, _title_width, _timestamp_width
    if _show_warning:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <{_timestamp_width}}] {Back.YELLOW}{Fore.BLACK}{title: ^{_title_width}}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )

def info(text, title = "Info", EOL=True):
    global _show_info, _title_width, _timestamp_width
    if _show_info:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <{_timestamp_width}}] {Back.GREEN}{Fore.BLACK}{title: ^{_title_width}}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )

def notice(text,title = f"Info", EOL=True):
    global _show_notice, _title_width, _timestamp_width
    if _show_notice:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <{_timestamp_width}}] {Back.GREEN}{Fore.BLACK}{title: ^{_title_width}}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )


def debug(text,source="debug", EOL=True):
    global _show_debug, _title_width, _timestamp_width
    if _show_debug:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000')
        endchar = ''
        if EOL:
            endchar = '\n\r'
        print(f'[{timestamp: <{_timestamp_width}}] {Back.MAGENTA}{Fore.BLACK}{source: ^{_title_width}}{Style.RESET_ALL} {text}\r', end=endchar,flush=True )


def spinner(text, delay=0.2):
    spinner = ['/','-','\\','|']
    for char in spinner:
        fprint(f'{text} {char}',EOL=False)
        time.sleep(delay) 

def info_spinner(text,title='info', delay=0.2, EOL=False):
    global _show_info
    if _show_info:
        spinner = ['/','-','\\','|']
        for char in spinner:
            fprint(f'{Back.GREEN}{Fore.BLACK}{title: ^{_title_width}}{Style.RESET_ALL} {char} {text}                 ',EOL=False)
            time.sleep(delay) 
        fprint(f'{Back.GREEN}{Fore.BLACK}{title: ^{_title_width}}{Style.RESET_ALL} {text}                ',EOL=False)
        if EOL:
            print('')