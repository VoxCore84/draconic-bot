# GM Commands Reference
Tags: gm, admin, command, additem, tele, learn, npc, spawn, levelup, modify, lookup, cast, server, display, effect, morph, companion, profession, bestiary, customnpc, transmog
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- GM (Game Master) commands are dot-commands typed in the in-game chat window (e.g., `.additem 12345`).
- Commands require an appropriate GM level. GM levels: 0 = player, 1 = moderator, 2 = GM, 3 = full admin.
- To create an account: in the worldserver console, type `bnetaccount create email password`.
- To set a GM level: in the worldserver console, type `account set gmlevel email level realmid`. Use level 3 for admin and -1 for all realms.
- Commands are case-insensitive. Arguments are separated by spaces.
- DraconicWoW includes custom commands beyond the standard TrinityCore set (see Custom DraconicWoW Commands below).

## Account Management (worldserver console only)
- `bnetaccount create [email] [password]` -- Create a new Battle.net account. Must be run from the worldserver console, not in-game chat.
- `account set gmlevel [email] [level] [realmid]` -- Set GM level for an account. Levels: 0 = player, 1 = moderator, 2 = GM, 3 = admin. Use -1 for realmid to apply to all realms.
- `account set password [email] [newpass] [newpass]` -- Change an account password from the worldserver console.

## Character and Player Commands
- `.character level [playername] [level]` -- Set a character's level directly to the specified value.
- `.levelup [levels]` -- Increase your character's level by the specified amount.
- `.modify speed [value]` -- Change your movement speed multiplier (1 = normal, 10 = very fast).
- `.modify fly [value]` -- Change your flying speed multiplier.
- `.modify money [amount]` -- Add or remove gold. Amount is in copper (10000 = 1 gold). Use negative values to remove.
- `.modify hp [amount]` -- Set your max health.
- `.modify mana [amount]` -- Set your max mana.
- `.revive` -- Resurrect the targeted player (or yourself if no target).
- `.die` -- Kill the targeted unit.
- `.freeze [playername]` -- Freeze a player in place, preventing all movement and actions.
- `.unfreeze [playername]` -- Unfreeze a previously frozen player.
- `.gm on` -- Enable GM mode (invisible to normal players).
- `.gm off` -- Disable GM mode (visible to players again).
- `.gm fly on` -- Enable GM flying without a mount.

## Teleportation
- `.tele [name]` -- Teleport to a named location (e.g., `.tele stormwind`, `.tele orgrimmar`). Use `.lookup tele [name]` to search for available locations.
- `.go xyz [X] [Y] [Z] [mapid]` -- Teleport to exact world coordinates on the specified map.
- `.go creature [guid]` -- Teleport to a creature by its spawn GUID.
- `.go object [guid]` -- Teleport to a game object by its spawn GUID.
- `.appear [playername]` -- Teleport yourself to the specified player's location.
- `.summon [playername]` -- Summon the specified player to your current location.

## Items
- `.additem [itemid] [count]` -- Add the specified item to your inventory. Count is optional (default 1).
- `.additemset [setid]` -- Add every item from a complete item set to your inventory.
- `.lookup item [name]` -- Search for items by name. Returns matching item IDs.

## Spells and Auras
- `.learn [spellId]` -- Teach yourself a spell permanently.
- `.cast [spellId]` -- Cast a spell on yourself or your target.
- `.aura [spellId]` -- Apply a persistent aura to yourself.
- `.unaura [spellId]` -- Remove a specific aura.
- `.unaura all` -- Remove all auras from yourself.
- `.lookup spell [name]` -- Search for spells by name. Returns matching spell IDs.

## NPCs and Creatures
- `.npc add [creatureId]` -- Spawn a creature permanently at your location. Find creature IDs with `.lookup creature`.
- `.npc delete` -- Delete the currently targeted creature from the world and database.
- `.npc move` -- Move the targeted creature to your current position.
- `.npc set model [displayid]` -- Change the targeted NPC's display model.
- `.npc set level [level]` -- Set the targeted NPC's level.
- `.npc info` -- Display detailed information about the targeted NPC (entry, GUID, faction, health, flags, etc.).
- `.lookup creature [name]` -- Search for creatures by name. Returns matching creature IDs.

## Game Objects
- `.gobject add [entry]` -- Spawn a game object permanently at your location.
- `.gobject delete` -- Delete the targeted game object.
- `.gobject near [distance]` -- List all game objects within the specified distance (default 10 yards).
- `.gobject info` -- Display information about the targeted game object.

## Quests
- `.quest add [questId]` -- Add a quest to your quest log.
- `.quest complete [questId]` -- Force-complete a quest, marking all objectives as done.
- `.quest remove [questId]` -- Remove/abandon a quest from your log.
- `.quest reward [questId]` -- Give quest rewards without requiring objective completion.
- `.lookup quest [name]` -- Search for quests by name.

## Lookup Commands
- `.lookup item [name]` -- Search items by name.
- `.lookup spell [name]` -- Search spells by name.
- `.lookup creature [name]` -- Search creatures by name.
- `.lookup area [name]` -- Search area/zone names.
- `.lookup tele [name]` -- Search available teleport destinations.
- `.lookup quest [name]` -- Search quests by name.

## Custom DraconicWoW Commands
These commands are unique to DraconicWoW and are not found on standard TrinityCore servers.

### Appearance and Roleplay
- `.display` -- Transmog and appearance display system. Allows per-slot visual overrides for roleplay outfits without changing actual gear.
- `.effect` -- Visual spell effect management. Apply persistent SpellVisualKit effects to your character that sync to other players.
- `.wmorph [displayid]` -- Morph your character into any creature model by display ID. Persists through logout.
- `.wscale [value]` -- Scale your character's visual size. Persists through logout.
- `.remorph` -- Reapply your saved morph appearance on login or after zoning.

### Custom NPCs
- `.cnpc` / `.customnpc` -- Create and manage custom NPCs with player-race appearances, custom equipment, and full outfit control. Allows spawning NPCs that look like player characters.

### Professions
- `.prof learn [profname]` -- Learn a profession (e.g., `.prof learn blacksmithing`).
- `.prof unlearn [profname]` -- Unlearn a profession.
- `.prof max [profname]` -- Max out a profession's skill level.
- `.prof reset` -- Reset all professions.

### Companion Squad
- `.comp` -- Companion squad commands. Manage AI-controlled NPC party members that follow you, fight with role-based AI (tank, healer, DPS), and maintain formation.

### BestiaryForge (admin only)
- `.bestiary` -- Creature spell and aura sniffer tool. Records what spells and auras creatures use in real-time for database documentation. Requires GM level 3.

## Server Management (admin only)
- `.server info` -- Display server uptime, connected player count, and build information.
- `.server restart [seconds]` -- Schedule a server restart with a countdown broadcast to all players.
- `.server shutdown [seconds]` -- Schedule a server shutdown with a countdown broadcast.
- `.reload all` -- Reload all server data tables from the database without restarting.
- `.reload eluna` -- Reload all Eluna Lua scripts without restarting the server.

## Common Symptoms
- "How do I give myself items?" -- Use `.additem [id]`. Find item IDs with `.lookup item [name]` or search on Wowhead.
- "How do I fly?" -- Use `.gm fly on` for GM flying, or enable Skyriding if available.
- "How do I teleport?" -- Use `.tele [name]` for named locations (try `.tele stormwind`) or `.go xyz` for exact coordinates.
- "How do I spawn NPCs?" -- Use `.npc add [creatureId]`. Find creature IDs with `.lookup creature [name]`.
- "My commands don't work" -- Check your GM level with `.gm`. Most commands need level 1+, admin commands need level 3. If you just set your GM level, you may need to relog.
- "How do I change my appearance?" -- DraconicWoW has `.wmorph [displayid]` to morph into creatures and `.display` for transmog overrides.
- "How do I get a companion?" -- Use `.comp` to manage your companion squad. See the companion system documentation for full details.
- "How do I manage professions?" -- Use `.prof learn [name]` to learn, `.prof max [name]` to max skill, `.prof unlearn [name]` to remove.

## Escalate When
- The user needs a command that does not exist in TrinityCore or DraconicWoW's custom set.
- The user reports that a command is not working despite having the correct GM level.
- The user asks about RBAC permissions or fine-grained command access control.
- The user needs account-level actions performed (bans, character recovery, password resets via console).
