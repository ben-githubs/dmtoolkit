# DMToolKit

The DM Tool Kit project aims to provide several quality-of-life services for DMs to reference during sessions. It's currently a work in progress, but as more time passes, more features will be added! This is essentially me knocking items off my DM wishlist.

## How to Use

In an ideal world, you would host this on a server and connect to it, but in reality you're probably running this locally. You can install all the required dependecies using poetry (`poetry install`) and then run the server by running `wsgi.py` from within the virtual environment. Then, navigate to `localhost:8080` in your web browser.

## Tools

### Better Initiative Tracker

DMToolKit includes a initiative tracker to use during combat rounds. My biggest issue after using multiple trackers online is that none of them seemed to allow you to view the statblock of a creature alongside the initiative list. As someone who frequently references statblocks during combat, this was really annoying! I decided to roll my own, and this is the result.

Alongside statblock rendering, the tracker also has the following features of note:

* Renamable Creatures
  * I use this to give nicknames to enemies based on their mini's differentiating features. If my players are facing a trio of goblins, I can use 3 goblin minis with different weapons and nickname each statblock in the tracker with the weapon on the mini; i.e. Sword, Whip, and XBow
* Automatic Initiative Rolling
  * Because we already have the statblock information for every creature, we can dynamically roll initiaitve for all creatures with the appropriate modifiers!
* Encounter Saving
  * DM's can set up their encounters ahead of a session and quickly load them up if/when their players trigger them. This helps streamline combat during a session as you aren't wasting time adding in a bunch of enemies to the tracker.
* XP & Loot Totalling
  * The tracker keeps count of the total XP and loot to award for each encounter!
* Persistant Players
  * You can input specific players to your encounters and have them persist across encounters.
* HP Calculation
  * Nobody likes mental math. When editing the HP of a player/enemy, you can simply type +/- before the amount to add/subtract and let the tool handle the calculation. If you need to explicitly set a creature's HP to a specific value, it's easy: just don't include the +/- sign!

## Credits
This project is only possible thanks to the fine people below!

- Large swaths of data regarding monsters, items, and spells come from [5e.tools](https://5e.tools)
- Status marker icons are created originally for Roll20 by [u/JinxShadow](https://www.reddit.com/user/JinxShadow/)
