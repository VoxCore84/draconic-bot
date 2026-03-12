# DraconicWoW Custom Features
Tags: helper, companion, transmog, display, effect, morph, wmorph, wscale, remorph, cnpc, customnpc, profession, prof, dragonriding, skyriding, advfly, timeistime, sololfg, worldchat, aio, collectorbounty, outfit
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- DraconicWoW includes a suite of custom systems built for roleplay, quality-of-life, and solo play.
- These features are unique to DraconicWoW and are not found on standard TrinityCore servers.
- Most custom features are actively maintained and updated. Report bugs to staff.

## Helpers / Companions
- DraconicWoW has 6 named NPC companions you can hire to fight alongside you: **Olaf**, **Kam'il**, **Elden**, **Fyrakk**, **Jamone**, and **Thane**.
- Helpers follow you around the world, fight enemies with you, gain XP, and level up as you play.
- Hiring a helper costs **5 gold**. You hire them through an in-game UI powered by the AIO addon system.
- You can customize your helper's appearance using transmog -- make them look however you want.
- **Commands**: Type the helper's name followed by an order in chat. Examples:
  - `Olaf attack` -- tells Olaf to attack your target.
  - `Elden defend` -- tells Elden to switch to a defensive stance.
  - `Thane return` -- tells Thane to return to your side.
  - Other orders include: follow, stay, dismiss.
- Helpers have role-based AI (tank, healer, DPS) and use formation movement to stay in position around you.
- **Requires AIO addon**: The helper hiring UI will not appear without the AIO addon installed on the client.

## Transmog / Display System
- Override the visual appearance of any equipment slot using the `.display` command system.
- Full wardrobe and outfit system with the ability to save and load multiple outfits.
- Works with the 12.x transmog UI -- you can use the standard wardrobe interface to browse and apply appearances.
- Supports armor slots, weapons (main-hand and off-hand with multiple visual options), hidden appearances, and enchant visuals.
- **Common question**: "How do I transmog?" -- Use the `.display` commands for per-slot overrides, or use the in-game transmog UI at a transmog NPC.
- **Known quirk**: Some slots may need you to re-equip the item to refresh the visual.

## Visual Effects (.effect)
- Apply persistent SpellVisualKit effects to your character using `.effect` commands.
- These are cosmetic visual effects -- glowing auras, elemental effects, particle trails, and more.
- Effects **persist across logout and login** -- you do not lose them when you disconnect.
- Effects sync to other players via late-join: when another player enters your area, they will see your effects.
- Great for roleplay scenes and character customization.

## Player Morph (.wmorph, .wscale, .remorph)
- `.wmorph [displayId]` -- Transform your character's appearance to any creature model in the game.
- `.wscale [scale]` -- Change your character's size. Values above 1.0 make you larger, below 1.0 make you smaller.
- `.remorph` -- Re-apply your current morph. Useful after zoning, disconnecting, or if the morph visual drops.
- Morphs are **persistent across sessions** -- your morph is saved and automatically reapplied when you log in.
- **Common question**: "My morph disappeared" -- Type `.remorph` to reapply it. This can happen after loading screens or zone transitions.

## Custom NPCs (.cnpc / .customnpc)
- Create player-race NPCs with fully customizable equipment and appearance.
- Uses the CreatureOutfit system to give NPCs custom armor, weapons, and racial features.
- Managed via `.cnpc` (or `.customnpc`) commands.
- Custom NPC template IDs start at 400000.
- Useful for populating roleplay scenes with unique characters.

## Professions (.prof)
- Eluna-based profession management with simple chat commands.
- 13 professions are available (all primary and secondary professions).
- **Commands**:
  - `.prof learn [profession]` -- Learn a profession.
  - `.prof unlearn [profession]` -- Unlearn a profession.
  - `.prof max` -- Max out all your current professions.
  - `.prof reset` -- Reset all professions.
- **Client addon**: Type `/profs` in chat to open the profession UI (accessed through the Addon Compartment button on the minimap).

## Collector's Bounty
- A special buff (spell 1300000) that gives a **+5% bonus chance** on rare boss drops.
- Applies to iconic rare drops like Sulfuras binding, Warglaives of Azzinoth, Ashes of Al'ar, Invincible's Reins, and other famous boss loot.
- Designed to make farming legacy content more rewarding for collectors.

## Dragonriding / Skyriding (AdvFly)
- Full dragonriding (dynamic flight / Skyriding) support with custom-tuned physics.
- Includes configurable parameters for air friction, maximum velocity, banking rates, and more.
- Players can use Skyriding in supported zones with dragonriding mounts.

## TimeIsTime
- Server time is synchronized with real-world time -- the in-game clock matches reality.
- Weather follows realistic patterns tied to the time system.

## SoloLFG
- Queue for dungeons solo without needing a full group.
- Allows solo players to experience dungeon content at their own pace.

## WorldChat
- Global chat channel accessible from anywhere in the game world.
- All players can communicate regardless of location, faction, or zone.

## AIO (Addon IO)
- Custom client-server addon communication framework unique to DraconicWoW.
- Powers the Helper hiring UI and other custom interfaces that require real-time server communication.
- **Players must install the AIO addon** in their WoW AddOns folder for AIO-powered features to work.
- Without AIO installed, features like the Helper UI will not appear.
- The AIO addon is provided with the DraconicWoW client files.

## Common Symptoms
- "How do I transmog?" -- Use the `.display` commands for per-slot overrides, or visit a transmog NPC to use the wardrobe UI.
- "How do I get a helper/companion?" -- Make sure the AIO addon is installed, then use the in-game hiring UI. Costs 5 gold.
- "My morph disappeared" -- Type `.remorph` to reapply it.
- "My effects are gone" -- Effects should persist through login. If they are missing, try re-logging. If still gone, re-apply with `.effect`.
- "Can I fly?" -- Skyriding/dragonriding is available in supported zones with dragonriding mounts.
- "How do I use professions?" -- Type `.prof learn [profession]` in chat. Use `/profs` for the addon UI.
- "What is AIO?" -- It is a required addon for some DraconicWoW features. Install it in your AddOns folder.
- "How do I get Collector's Bounty?" -- Ask staff about how to obtain the buff.

## Escalate when
- The user reports a bug with a custom system (transmog visual glitch, helper AI issues, morph not persisting after remorph, effects not syncing).
- The user wants a feature that does not exist yet.
- The user encounters a crash related to a custom system.
- Helper commands are not responding (may indicate Eluna or AIO issue -- check server logs).
