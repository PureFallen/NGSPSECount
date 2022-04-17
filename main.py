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
            global ENEMIES
            global PSE

            # Each Message ends with a Newline. No, I do not know why.
            msg = line_list[5].replace("\n", "")
            if msg == BURST_MSG:
                ENEMIES = -1
                PSE = True
                prints.print_info("PSE Burst detected. Logging Enemy Kills...")
            elif msg == CLIMAX_MSG:
                if PSE:
                    PSE = False
                    prints.print_info("PSE Climax detected.")
                    prints.print_info(f"Enemies killed during PSE: {BColors.LIGHT_PURPLE}{ENEMIES}")
                else:
                    prints.print_info("Additional PSE Climax detected. Is that an Encore, or did you change rooms?")
                    prints.print_info(f"Enemies killed since last PSE Climax: {BColors.LIGHT_PURPLE}{encore_routine()}")


def action_loop():
    # Get initial values
    date, path, old_count = init("ActionLog")

    while True:
        if PSE:
            global ENEMIES
            if ENEMIES == -1:
                date, path, _ = init("ActionLog")

                # PSE Auto Chat is delayed; Look for latest cleared Trial
                old_count = latest_trial(path)

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


def encore_routine():
    encore_enemies = 0

    _, path, _ = init("ActionLog")
    old_count = latest_trial(path)

    f = open(path, 'r', encoding='utf-16')
    new_count = sum(1 for _ in f) - 1
    f.seek(0, 0)
    lines = f.readlines()[-(new_count - old_count):]

    for line in lines:
        # Check function action_listener for Legend.
        line_list = line.split("\t")
        if len(line_list) >= 7:
            amount = line_list[6].replace("\n", "")
            if amount.startswith("N-Meseta"):
                encore_enemies += 1

    encore_enemies -= ENEMIES
    f.close()
    return encore_enemies


def latest_trial(path):
    old_count = 0

    f = open(path, 'r', encoding='utf-16')
    lines = f.readlines()
    for i, line in enumerate(lines):
        # Check function action_listener for Legend.
        line_list = line.split("\t")
        if len(line_list) >= 7:
            amount = line_list[6].replace("\n", "")
            if amount == "N-Meseta(1000)" or amount == "N-Meseta(1500)":
                old_count = i

    return old_count


if __name__ == "__main__":
    try:
        # Create Enemy Logging Thread
        t = Thread(target=action_loop, daemon=True)
        t.start()

        chat_loop()
    except KeyboardInterrupt:
        prints.print_info(BColors.YELLOW + "Program closed by user (CTRL+C)")
        exit()
