import ctypes.wintypes
from datetime import datetime, timezone
import glob
import os
from threading import Thread

from util.colors import BColors
from util import prints

PLAYER_ID = "11055664"
BURST_MSG = "/p Triggered PSE Burst."
CLIMAX_MSG = "/p Triggered PSE Climax."

PATH = ""
PSE = False
ENEMIES = -1


def init():
    global PATH

    prints.print_info("Locating log_ngs folder...")

    # Locate Documents Folder
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)

    # Get game folder in which log_ngs was updated most recently
    try:
        PATH = max(glob.glob(os.path.join(buf.value, "SEGA/*/log_ngs/")), key=os.path.getmtime)
    except ValueError:
        prints.print_error(f"Found no folder containing 'log_ngs' in {buf.value}. Normally this should only happen "
                           f"when the game is not installed.")

    prints.print_info(f"log_ngs folder is {PATH}")


def get_file_obj(log_type):
    error_fnf = False
    date = int(datetime.now(timezone.utc).strftime("%Y%m%d"))
    path = f"{PATH}{log_type}{date}_00.txt"

    while True:
        try:
            f = open(path, 'r', encoding="utf-16")
            break
        except FileNotFoundError:
            if not error_fnf:
                error_fnf = True
                prints.print_error(f"{log_type} File not found! This should solve automatically once you started the "
                                   f"game or after sending/receiving a chat message or doing an action after "
                                   f"UTC Midnight (New {log_type} File). If this error persists, contact the developer "
                                   f"of this script for further advice.")
    return f, date


def chat_loop():
    # Get initial values
    f, date = get_file_obj("ChatLog")
    # Set File Cursor at the end of the file; f.seek(0, 2) not worked for whatever reason.
    f.readlines()
    prints.print_info("Initialization complete.")

    while True:
        # Check for UTC Midnight to update values
        if int(datetime.now(timezone.utc).strftime("%Y%m%d")) > date:
            f, date = get_file_obj("ChatLog")

        # Check for new lines in the Chatlog File
        lines = f.readlines()
        if lines:
            chat_parser(lines)


def chat_parser(lines):
    for line in lines:
        # Split line into a list, seperated by Tabulator
        # Legend: ['<DATE>T<TIME>', '<MESSAGE_ID>', <'CHAT_TYPE'>, '<PLAYER_ID>', '<PLAYER_NAME>', '<MESSAGE>']
        line_list = line.split("\t")
        if line_list[3] == PLAYER_ID:
            global ENEMIES
            global PSE

            # Each Message ends with a Newline. No, I do not know why.
            msg = line_list[5].strip()
            if msg == BURST_MSG:
                ENEMIES = -1
                PSE = True
                prints.print_info("PSE Burst detected. Logging Enemy Kills...")
            elif msg == CLIMAX_MSG:
                if PSE:
                    PSE = False
                    prints.print_info("PSE Climax detected.")
                    prints.print_info(f"Enemies killed during PSE: {BColors.LIGHT_PURPLE}{ENEMIES}")
                elif ENEMIES != -1:
                    encore_enemies = latest_trial()
                    prints.print_info("Additional PSE Climax detected. Is that an Encore, or did you change rooms?")
                    prints.print_info(f"Enemies killed since last PSE Climax: {BColors.LIGHT_PURPLE}"
                                      f"{encore_enemies - ENEMIES}")
                    ENEMIES = encore_enemies


def action_loop():
    # Get initial values
    f, date = get_file_obj("ActionLog")

    while True:
        if PSE:
            global ENEMIES
            if ENEMIES == -1:
                f, date = get_file_obj("ActionLog")
                f.readlines()
                ENEMIES = latest_trial()

            # Check for UTC Midnight to update values
            if int(datetime.now(timezone.utc).strftime("%Y%m%d")) > date:
                f, date = get_file_obj("ActionLog")
            # Check for new lines in the ActionLog File
            lines = f.readlines()
            if lines:
                action_parser(lines)


def action_parser(lines):
    for line in lines:
        # Split line into a list, seperated by Tabulator Legend: ['<DATE>T<TIME>', '<MESSAGE_ID>', <'ACTION_TYPE'>,
        # '<PLAYER_ID>', '<PLAYER_NAME>', '<ITEM>', '<AMOUNT>', '<MISC>']
        # "ITEM" for Meseta is empty; instead it is only referred in AMOUNT as "Meseta(12)".
        line_list = line.split("\t")
        if len(line_list) >= 7:
            action_type = line_list[2].strip()
            amount = line_list[6].strip()
            if action_type == "[Pickup]" and amount.startswith("N-Meseta"):
                global ENEMIES
                ENEMIES += 1


def latest_trial():
    f, _ = get_file_obj("ActionLog")
    enemies = 0

    lines = f.readlines()
    lines = reversed(lines)
    for i, line in enumerate(lines):
        # Check function action_listener for Legend.
        line_list = line.split("\t")
        if len(line_list) >= 7:
            action_type = line_list[2].strip()
            amount = line_list[6].strip()
            if action_type == "[Pickup]" and amount.startswith("N-Meseta"):
                if amount == "N-Meseta(1000)" or amount == "N-Meseta(1500)":
                    break
                enemies += 1
    f.close()
    return enemies


if __name__ == "__main__":
    try:
        init()

        # Create Enemy Logging Thread
        t = Thread(target=action_loop, daemon=True)
        t.start()

        chat_loop()
    except KeyboardInterrupt:
        prints.print_info(BColors.YELLOW + "Program closed by user (CTRL+C)")
        exit()
