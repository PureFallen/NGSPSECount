# NGSPSECount
A python script which keeps track of enemies killed during an PSE in PSO2:NGS. That's it.

The code has been thrown together in a couple of minutes. It is just supposed to work, it is not going to win any engineering awards. The code performance is questionable. I know.

![image](https://user-images.githubusercontent.com/68307987/163992942-83caf225-2cf0-4478-8d73-3750657cf9ac.png)


# Why?

There has been research going on in which people look for correlations between the amount of killed enemies during a PSE and the appearance of a so called "PSE Encore". For that, people have kept track of their progress in Title Tasks such as `Huntsman of Retem Alnothe VI` (kill 60000 Enemies) at the beginning and end of an PSE, noted those numbers down and also noted if an Encore occurred. However, as more people hit the latest Tier of this Title Task, the progress stops counting.

This script is supposed to be a cheap alternative for keeping track of enemies killed during an PSE for those researchers. However, it might as well be used for practice or comparison purposes by anyone.

More information:

https://web.archive.org/web/20220417020420/https://twitter.com/dilute_rin/status/1515107043891642369 \
https://web.archive.org/web/20220417020643/https://twitter.com/dilute_rin/status/1515108153628983297 \
https://web.archive.org/web/20220417020835/https://twitter.com/dilute_rin/status/1515109040984313860 \
https://nitter.net/TheuberClips/status/1515109226561286145 \
https://nitter.net/flowerint1034/status/1515111429355245568 \
https://nitter.net/flowerint1034/status/1515660633236467715

Snapshots:
https://web.archive.org/web/20220417021041/https://twitter.com/TheuberClips/status/1515109226561286145 \
https://web.archive.org/web/20220417021223/https://twitter.com/flowerint1034/status/1515111429355245568 \
https://web.archive.org/web/20220419113238/https://twitter.com/flowerint1034/status/1515660633236467715

## Current State of Research

The Chance for a PSE Encore to appear is guessed at 20%. There seems to be no relationship between "Enemies Killed" and the Chance to gain a PSE Burst.

(Exception: Killing 0 PSE Enemies will reward no PSE Burst with Sample size n=20)

https://docs.google.com/spreadsheets/d/1N0WPMFXLnHK76RzznlI15psfP73i46YTNteehrxOSEQ \
https://docs.google.com/spreadsheets/d/1_OgubzM5QFe4rua4Xu0GSMAI8Idoq8r2yI8Ioyec6oY

# How?

Almost every interaction and chat message send in PSO2 is logged towards their logfiles in the `Documents/SEGA` directory. We can use this to check for the start and end of a PSE (via. an automatically send text message) as well of killed enemies as enemies in Combat Zones of PSO2 have a guaranteed Meseta Drop on kill.

# Setup?

[Download](https://github.com/PureFallen/NGSPSECount/releases/latest) the latest version from The Releases Page. Configure the `config.ini` as described below.

When running into problems, try running the executable via. `Windows Terminal` instead of the Command Prompt, Powershell or other Shell of your choice. For that execute `run.cmd` instead.

As alternative, you can [clone](https://github.com/PureFallen/NGSPSECount/archive/refs/heads/main.zip) the project and run the python script `NGSPSECount.py` directly. Please note that this will require a basic installation of Python 3.

## Configuration

| Config Value | Meaning                                                                                                                                                         |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PLAYER_ID    | Your PlayerID Number. Prevents double triggering through other players with equal PSE Auto Chats. Can be found in your character information or in the logfile. |
| BURST_MSG    | The **exact** message send by Auto Chat-Feature when a PSE Burst occurs                                                                                         |
| CLIMAX_MSG   | The **exact** message send by Auto Chat-Feature when a PSE Climax occurs                                                                                        |

Be sure that the sending of Autowords is enabled for your character.

`ESC -> System -> Options -> Sound/Chat -> Auto Chat Usage -> Set to "Use"`

Auto Chat Messages can be set at:

`ESC -> Chat -> Auto Chat Settings -> Events -> At PSE Burst Start/At PSE Climax`

# Known limitations

## Script only allows for one Auto Chat to be set per Event Type at the same time

This is mostly a simplicity decision at the moment. It would not be hard to add support for several messages to look for, but it rather hit performance of the script and seems unnecessary.
