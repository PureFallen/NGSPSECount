# NGSPSECount
A python script which keeps track of enemies killed during an PSE in PSO2:NGS. That's it.

The code has been thrown together in a couple of minutes. It is just supposed to work, it is not going to win any engineering awards. The code performance is questionable. I know.

# Why?

There has been research going on in which people look for correlations between the amount of killed enemies during a PSE and the appearance of a so called "PSE Encore". For that, people have kept track of their progress in Title Tasks such as `Huntsman of Retem Alnothe VI` (kill 60000 Enemies) at the beginning and end of an PSE, noted those numbers down and also noted if an Encore occurred. However, as more people hit the latest Tier of this Title Task, the progress stops counting.

This script is supposed to be a cheap alternative for keeping track of enemies killed during an PSE for those researchers. However, it might as well be used for practice or comparison purposes by anyone.

More information:

https://nitter.net/dilute_rin/status/1515107043891642369

https://nitter.net/dilute_rin/status/1515108153628983297

https://nitter.net/dilute_rin/status/1515109040984313860

https://nitter.net/TheuberClips/status/1515109226561286145

https://nitter.net/flowerint1034/status/1515111429355245568

Snapshots:

https://web.archive.org/web/20220417020420/https://twitter.com/dilute_rin/status/1515107043891642369

https://web.archive.org/web/20220417020643/https://twitter.com/dilute_rin/status/1515108153628983297

https://web.archive.org/web/20220417020835/https://twitter.com/dilute_rin/status/1515109040984313860

https://web.archive.org/web/20220417021041/https://twitter.com/TheuberClips/status/1515109226561286145

https://web.archive.org/web/20220417021223/https://twitter.com/flowerint1034/status/1515111429355245568

# How?

Almost every interaction and chat message send in PSO2 is logged towards their logfiles in the `Documents/SEGA` directory. We can use this to check for the start and end of a PSE (via. an automatically send text message) as well of killed enemies as enemies in Combat Zones of PSO2 have a guaranteed Meseta Drop on kill.

# Setup?

The script requires Python 3 to run. It only uses default packages and local packages, most versions of Python 3 should do.

[Download](https://github.com/PureFallen/NGSPSECount/archive/refs/heads/main.zip) the Project, edit `main.py` with a Text Editor of your choice and change the constants at the very top to your needs. Nothing fancy like config file yet.

| Constant   | Meaning                                                                                                                                                         |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PATH       | Path towards your PSO2NGS Logfiles                                                                                                                              |
| PLAYER_ID  | Your PlayerID Number. Prevents double triggering through other players with equal PSE Auto Chats. Can be found in your character information or in the logfile. |
| BURST_MSG  | The **exact** message send by Auto Chat-Feature when a PSE Burst occurs                                                                                         |
| CLIMAX_MSG | The **exact** message send by Auto Chat-Feature when a PSE Climax occurs                                                                                        |

Be sure that the sending of Autowords is enabled for your character.

`ESC -> System -> Options -> Sound/Chat -> Auto Chat Usage -> Set to "Use"`

Auto Chat Messages can be set at:

`ESC -> Chat -> Auto Chat Settings -> Events -> At PSE Burst Start/At PSE Climax`

# Known limitations | Issues

## Script only allows for one Auto Chat to be set per Event Type at the same time

This is mostly a simplicity decision at the moment. It would not be hard to add support for several messages to look for, but it rather hit performance of the script and seems unnecessary.

## Some Enemies are not counted at the Start of a PSE Burst

The script starts counting once the PSE Auto Chat Message is posted. This message is posted once the "PSE Burst" UI Element is displayed, which can be delayed by NPC communications of the previous Emergency Trial and similar. As such, the real amount of killed enemies is a bit higher than the one displayed.

This can probably be fixed by looking for another Action in the ActionLog that suggest the clearance of an Emergency Trial (required to enter the PSE Burst) or for a Meseta Increase that is bigger than the usual Enemy one (Emergency Trial Reward), but this could hurt the complexity of the script and maybe break with future updates.

## Encore Enemies are not counted | Displays "0"

An PSE Encore does not trigger the Auto Chat for the Event "PSE Burst", but does so for "PSE Climax". As such, the script never starts to log for enemies but runs the finish-portion later.

As Encore Enemy Count are currently not part of the research, simply removing this message would be an easy fix. However, I may end adding support for it when fixing the previous issue.

## Different Encodings for the Logfiles varying in Windows Version and Game Version

This one is just theoretical, as I stumbled over something similar when using Logfiles to create a Chat Bridge between PSO2 and Discord. It seems like that the Logfiles are encoded differently for different versions of Windows and PSO2 (Steam, XBox, ...).

As I not own to have 3+ different Windows Versions with all 4 variants of PSO2:NGS on each, this will probably not get fixed until someone brings awareness to this in an Issue, Pull Request or by messaging me privately.