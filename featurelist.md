# Planned

## Encounters

- Save current encounter across page reloads as temporary encounter
- Delete encounters
- Be able to see encounter XP and monsters without opening the encounter (perhaps a `?` button with a popup?)
- Track creature conditions, like Paralyzed, Restratined, etc.
- Track turns (useful for the above, so you can autmatically remove effects if they expire after X turns)

## Proper Encounter Builder

- Make a separate page for building/editing encounters, which will provide features not seen in the tracker, like auto-generating encounters for specific biomes and party levels
- Encounters made here are obviously usable in the tracker
- Should let users load encounters from files, and save them to JSON as well
    - donjon lets users download dungeons as PDF; it'd be cool if we could load the encounters listed in those files

## Better Player Management

- Let users download players as JSON and upload player files
    - Find out what common formats players can be downloaded in from other tools; does dndbeyond have a download option?

## Proper Monsters API

- Have dedicated endpoints and pages for displaying/listing/searching monster info

## Crafting Module(s)

- Allow modules to control how loot dropping works and adding pages for crafting
- Modules will add new items, define crafting recipes, and other stuff
- Implement a module for Kibble's Crafting Guide

## Statblocks

- fix remaining `{@xx yy}` mappings
- render speeds with notes properly (see will-o-wisp for example)
- include cool picture in top corner like in 5e.tools
- render tagged monster type properly
