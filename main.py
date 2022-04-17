from datetime import datetime, timezone
from threading import Thread

from util.colors import BColors
from util import prints

PATH = "D:/Documents/SEGA/PHANTASYSTARONLINE2_NA_STEAM/log_ngs/"
PLAYER_ID = "11055664"
BURST_MSG = "/p Triggered PSE Burst."
CLIMAX_MSG = "/p Triggered PSE Climax."

PSE = False
ENEMIES = -1


def init(log_type):
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

    count = sum(1 for _ in f) - 1
    f.close()

    prints.print_info(f"{log_type} File for {date} found.")

    return date, path, count


def chat_loop():
    prints.print_info("Initialize script...")
    # Get initial values
    date, path, old_count = init("ChatLog")
    prints.print_info("Initialization complete.")

    while True:
        # Check for UTC Midnight to update values
        if int(datetime.now(timezone.utc).strftime("%Y%m%d")) > date:
            date, path, old_count = init("ChatLog")

        # Check for Changes in the Chatlog File
        f = open(path, 'r', encoding='utf-16')
        new_count = sum(1 for _ in f) - 1
        if new_count > old_count:
            chat_listener(f, old_count, new_count)
            old_count = new_count

        f.close()


def chat_listener(f, old_count, new_count):
    # Set File Cursor to begin of the file
    f.seek(0, 0)
    # Get List of last X lines of the file
    lines = f.readlines()[-(new_count - old_count):]

    for line in lines:
        # Split line into a list, seperated by Tabulator
        # Legend: ['<DATE>T<TIME>', '<MESSAGE_ID>', <'CHAT_TYPE'>, '<PLAYER_ID>', '<PLAYER_NAME>', '<MESSAGE>']
        line_list = line.split("\t")
        if line_list[3] == PLAYER_ID:
            global PSE

            msg = line_list[5].replace("\n", "")
            if msg == BURST_MSG:
                PSE = True
                prints.print_info("PSE Burst detected. Logging Enemy Kills...")
            elif msg == CLIMAX_MSG:
                global ENEMIES

                PSE = False
                prints.print_info("PSE Climax detected.")
                prints.print_info(f"Enemies killed during PSE: {BColors.LIGHT_PURPLE}{ENEMIES}")
                ENEMIES = -1


def action_loop():
    date, path, old_count = init("ActionLog")

    while True:
        if PSE:
            global ENEMIES
            if ENEMIES == -1:
                date, path, old_count = init("ActionLog")

                # PSE Auto Chat is delayed; Look for latest cleared Trial
                f = open(path, 'r', encoding='utf-16')
                lines = f.readlines()
                for i, line in enumerate(lines):
                    # Check function action_listener for Legend.
                    line_list = line.split("\t")
                    if len(line_list) >= 7:
                        amount = line_list[6].replace("\n", "")
                        if amount == "N-Meseta(1000)" or amount == "N-Meseta(1500)":
                            prints.print_info(i)
                            old_count = i

                ENEMIES += 1

            # Check for UTC Midnight to update values
            if int(datetime.now(timezone.utc).strftime("%Y%m%d")) > date:
                date, path, old_count = init("ActionLog")
            # Check for Changes in the ActionLog File
            f = open(path, 'r', encoding='utf-16')
            new_count = sum(1 for _ in f) - 1
            if new_count > old_count:
                action_listener(f, old_count, new_count)
                old_count = new_count
            f.close()


def action_listener(f, old_count, new_count):
    # Set File Cursor to begin of the file
    f.seek(0, 0)
    # Get List of last X lines of the file
    lines = f.readlines()[-(new_count - old_count):]

    for line in lines:
        # Split line into a list, seperated by Tabulator Legend: ['<DATE>T<TIME>', '<MESSAGE_ID>', <'ACTION_TYPE'>,
        # '<PLAYER_ID>', '<PLAYER_NAME>', '<ITEM>', '<AMOUNT>', '<MISC>']
        # "ITEM" for Meseta is empty; instead it is only referred in AMOUNT as "Meseta(12)".
        line_list = line.split("\t")
        if len(line_list) >= 7:
            amount = line_list[6].replace("\n", "")
            if amount.startswith("N-Meseta"):
                global ENEMIES
                ENEMIES += 1


if __name__ == "__main__":
    try:
        # Create Enemy Logging Thread
        t = Thread(target=action_loop, daemon=True)
        t.start()

        chat_loop()
    except KeyboardInterrupt:
        prints.print_info(BColors.YELLOW + "Program closed by user (CTRL+C)")
        exit()
