# GM Commands Reference
Tags: gm, admin, command, additem, tele, learn, npc, spawn, levelup, modify, lookup, cast, server
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- GM (Game Master) commands are dot-commands typed in the in-game chat window (e.g., .additem 12345).
- Commands require an appropriate GM level to use. GM levels: 0 = player, 1 = moderator, 2 = GM, 3 = full admin.
- To set a GM level: in the worldserver console, type account set gmlevel youremail@example.com 3 -1 (3 = admin, -1 = all realms).
- Commands are case-insensitive. Arguments are separated by spaces.

## Common Commands

### Items
- .additem [itemId] [count] -- Add items to your inventory. Count is optional (default 1).
- .lookup item [name] -- Search for items by name. Returns matching item IDs.

### Teleport
- .tele [location] -- Teleport to a named location (e.g., .tele stormwind).
- .go creature [guid] -- Teleport to a creature by its spawn GUID.
- .go object [guid] -- Teleport to a game object by its spawn GUID.
- .go xyz [x] [y] [z] [mapId] -- Teleport to exact coordinates.

### Spells and Auras
- .learn [spellId] -- Teach yourself a spell.
- .cast [spellId] -- Cast a spell on yourself.
- .aura [spellId] -- Apply an aura to yourself.
- .unaura [spellId] -- Remove a specific aura.
- .unaura all -- Remove all auras from yourself.
- .lookup spell [name] -- Search for spells by name.

### NPCs and Creatures
- .npc add [creatureId] -- Spawn a creature at your location.
- .npc delete -- Delete the targeted creature.
- .npc move -- Move the targeted creature to your location.
- .npc set level [level] -- Set the targeted NPC's level.
- .lookup creature [name] -- Search for creatures by name.

### Player Modification
- .levelup [levels] -- Increase your level by the specified amount.
- .modify speed [1-10] -- Change your run speed multiplier (1 = normal, 10 = very fast).
- .modify money [amount] -- Add copper to your inventory (10000 = 1 gold).
- .modify hp [amount] -- Set your max health.
- .modify mana [amount] -- Set your max mana.

### Quests
- .quest add [questId] -- Add a quest to your quest log.
- .quest complete [questId] -- Force-complete a quest.
- .quest remove [questId] -- Abandon/remove a quest.
- .quest reward [questId] -- Give quest rewards without completing objectives.
- .lookup quest [name] -- Search for quests by name.

### Server Info
- .server info -- Show server uptime, player count, and build info.
- .server restart [seconds] -- Schedule a server restart.
- .server shutdown [seconds] -- Schedule a server shutdown.

### Phase and Visibility
- .mod phase [phaseId] -- Change your current phase.
- .gm on -- Enable GM mode (invisible to players).
- .gm off -- Disable GM mode (visible to players).
- .gm fly on -- Enable GM flying.

### Account Management
- bnetaccount create [email] [password] -- Create a new account (worldserver console only).
- account set gmlevel [email] [level] [realmId] -- Set GM level (worldserver console only). Level 3 = full admin, -1 = all realms.
- account set password [email] [newpass] [newpass] -- Change account password.

## Common symptoms
- "How do I give myself items?" -- Use .additem [id]. Find item IDs with .lookup item [name] or on Wowhead.
- "How do I fly?" -- Use .gm fly on for GM flying, or enable Skyriding if available.
- "How do I teleport?" -- Use .tele [name] for named locations or .go xyz for coordinates.
- "How do I spawn NPCs?" -- Use .npc add [creatureId]. Find creature IDs with .lookup creature [name].
- "My commands don't work" -- Check your GM level. You need level 1+ for most commands, level 3 for admin commands.

## Escalate when
- The user needs a command that does not exist in TrinityCore.
- The user reports that a command is not working despite having the correct GM level.
- The user asks about RBAC permissions or fine-grained command access control.
