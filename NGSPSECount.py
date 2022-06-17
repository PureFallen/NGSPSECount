import configparser
import ctypes.wintypes
from datetime import datetime, timezone
import glob
import os
from threading import Thread

from util.colors import BColors
from util import prints

VERSION = "2.0.0"
PSE = False
ENEMIES = ENEMIES_CLIMAX = 0


def init():
    log_path = player_identifier = burst_message = climax_message = str()

    # Enable ANSI codes
    os.system("")
    prints.print_info(f"Running Version {VERSION}")

    # Locate Documents Folder
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)

    # Get game folder in which log_ngs was updated most recently
    try:
        log_path = max(glob.glob(os.path.join(buf.value, "SEGA/*/log_ngs/")), key=os.path.getmtime)
    except ValueError:
        prints.print_error(f"Found no folder containing 'log_ngs' in {buf.value}. Normally this should only happen "
                           f"when the game is not installed.")
        exit(0)

    prints.print_info(f"log_ngs folder is {log_path}")

    # Read Config Values
    config = configparser.ConfigParser()
    config.read('./config.ini')
    try:
        player_identifier = config['DEFAULT']['PLAYER_ID']
        burst_message = config['DEFAULT']['BURST_MSG']
        climax_message = config['DEFAULT']['CLIMAX_MSG']
    except KeyError:
        prints.print_error("Unable to read config.ini . Does the file exist? Are the keys \"PLAYER_ID\", \"BURST_MSG\" "
                           "and \"CLIMAX_MSG\" named and set correctly?")
        exit(0)

    prints.print_info("config read successfully.")

    return log_path, player_identifier, burst_message, climax_message


def get_file_obj(log_path, log_type):
    error_fnf = False

    # Attempt to open Logfile until success.
    while True:
        date = int(datetime.now(timezone.utc).strftime("%Y%m%d"))
        log_path = f"{log_path}{log_type}{date}_00.txt"
        try:
            f = open(log_path, 'r', encoding="utf-16")
            break
        except FileNotFoundError:
            if not error_fnf:
                error_fnf = True
                prints.print_error(f"{log_type} File not found! This should solve automatically once you started the "
                                   f"game or after sending/receiving a chat message or doing an action after "
                                   f"UTC Midnight (New {log_type} File). If this error persists, contact the developer "
                                   f"of this script for further advice.")
    return f, date


def log_monitor(log_path, log_type, parser_method, parser_params):
    # Get initial values
    f, date = get_file_obj(log_path, log_type)
    # Set File Cursor at the end of the file; f.seek(0, 2) not worked for whatever reason.
    f.readlines()

    while True:
        # Check for UTC Midnight to update values
        if int(datetime.now(timezone.utc).strftime("%Y%m%d")) > date:
            f, date = get_file_obj(log_path, log_type)

        # Check for new lines in the Chatlog File
        lines = f.readlines()
        if lines:
            for line in lines:
                # Split Line into list using Tabulator; strip newline and similar
                line_list = [s.strip() for s in line.split("\t")]
                parser_params = parser_method(line_list, parser_params)


def chat_parser(line_list, parser_params):
    global PSE, ENEMIES, ENEMIES_CLIMAX
    # line_list: ['<DATE>T<TIME>', '<MESSAGE_ID>', <'CHAT_TYPE'>, '<PLAYER_ID>', '<PLAYER_NAME>', '<MESSAGE>']
    # parser_params: ['PLAYER_ID', 'BURST_MSG', 'CLIMAX_MSG']

    # Check if Chat Message is from PlayerID
    if line_list[3] == parser_params[0]:
        # Check if Chat Message is either PSE Burst Auto Chat or PSE Climax Auto Chat
        if line_list[5] == parser_params[1]:
            PSE = True
            prints.print_info("==========================================")
            prints.print_info("PSE Burst detected. Waiting for PSE Climax...")
        elif line_list[5] == parser_params[2]:
            if PSE:
                PSE = False
                ENEMIES_CLIMAX = ENEMIES
                prints.print_info("PSE Climax detected.")
                prints.print_info(f"Enemies killed during PSE: {BColors.YELLOW}{ENEMIES}")
            else:
                ENEMIES -= ENEMIES_CLIMAX
                ENEMIES_CLIMAX = ENEMIES
                prints.print_info("Additional PSE Climax detected. Is that an Encore, or did you change rooms?")
                prints.print_info(f"Enemies killed since last PSE Climax: {BColors.LIGHT_CYAN}{ENEMIES}")

    return parser_params


def action_parser(line_list, parser_params):
    global ENEMIES
    # line_list: ['<DATE>T<TIME>', '<MESSAGE_ID>', <'ACTION_TYPE'>, '<PLAYER_ID>', '<PLAYER_NAME>', '<ITEM>',
    # '<AMOUNT>', '<MISC>']
    # "ITEM" for Meseta is empty; instead it is only referred in AMOUNT as "Meseta(12)".
    #
    # parser_params: ['Previous Meseta in Wallet', 'Meseta Gained by Pickup', 'Meseta Gained Differently']
    if len(line_list) >= 7:
        # Check if Action is a pickup of Meseta (Enemy Kill)
        if line_list[2] == "[Pickup]" and line_list[6].startswith("N-Meseta"):
            # Check if pick of Meseta is caused by a trial clear
            if line_list[6] == "N-Meseta(1000)" or line_list[6] == "N-Meseta(1500)":
                ENEMIES = -1
            ENEMIES += 1

            pickup_amount = int(line_list[6][9:-1])
            new_total = int(line_list[7][16:-1])
            # Add Meseta picked up from enemy
            parser_params[1] += pickup_amount
            # Check if user started program or used/moved meseta
            if parser_params[0] != -1 and parser_params[0] < new_total:
                # subtract old wallet count and picked up meseta from new wallet count; add to differently gained meseta
                parser_params[2] += new_total - parser_params[0] - pickup_amount
            # Update wallet count
            parser_params[0] = new_total
            # Print out Meseta Yield
            print(f"Meseta (Pickup): {parser_params[1]}; Meseta (Other): {parser_params[2]}; "
                  f"Meseta (Session): {parser_params[1] + parser_params[2]}; "
                  f"Wallet Content: {parser_params[0]}", end='\r')

    return parser_params


if __name__ == "__main__":
    try:
        path, player_id, burst_msg, climax_msg = init()

        # Create Action Log Parsing Thread
        action_t = Thread(target=log_monitor,
                          args=(path, "ActionLog", action_parser, [-1, 0, 0]),
                          daemon=True)
        action_t.start()

        # Loop Chat Log Parsing
        log_monitor(path, "ChatLog", chat_parser, (player_id, burst_msg, climax_msg))
    except KeyboardInterrupt:
        prints.print_info(BColors.YELLOW + "Program closed by user (CTRL+C)")
        exit(0)
