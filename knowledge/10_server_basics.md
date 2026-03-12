# Server Basics -- DraconicWoW Overview
Tags: server, trinitycore, private, midnight, 12.x, client, wow
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## What Is DraconicWoW?
- DraconicWoW is a private World of Warcraft server built for roleplay. It runs on the retail 12.x / Midnight client (build 66263).
- The server engine is VoxCore, a heavily customized fork of TrinityCore that is approximately 15,000 commits ahead of upstream. VoxCore is maintained by VoxCore84 on GitHub.
- This is NOT a retail server. There are no paid subscriptions, no microtransactions, and no cash shop. It is a community-run project.
- DraconicWoW is specialized for immersive RP with custom transmog, visual effects, companion NPCs, player morphing, professions, and more.

## Server Architecture
- The server runs two executables:
  - **bnetserver** -- handles authentication and login. Players connect to this first.
  - **worldserver** -- handles all game logic, NPC AI, spells, chat, movement, and custom systems. This is where players spend their time.
- A bundled **worldserver-restarter.bat** automatically restarts the worldserver if it crashes. Players may see a brief disconnect followed by reconnection.
- The server uses **5 databases** on MySQL 8.0:
  - **auth** -- accounts, login credentials, RBAC permissions, IP bans.
  - **characters** -- player character data (inventory, quests, achievements, etc.).
  - **world** -- game world data (creatures, gameobjects, spawns, quests, loot tables, SmartAI scripts).
  - **hotfixes** -- client hotfix overrides managed by SicasForge 2.0. This is how the server patches item stats, spell data, and broadcast text without modifying the client files.
  - **roleplay** -- custom DraconicWoW tables: creature extras, custom NPC definitions, player extras, server settings.
- MySQL is bundled via **UniServerZ** in the repack. No separate MySQL installation is needed if you use the repack.

## Client and Connection
- Players need the **retail WoW client** matching the server's target build (currently 66263).
- Connection requires the **Arctium WoW Launcher** -- this redirects the retail client to the private server. The standard Battle.net launcher will NOT work.
- The client connects to bnetserver on ports 1119 (auth) and 8085 (world) by default.

## Hotfix Data Management
- DraconicWoW uses **SicasForge 2.0** for hotfix data management. SicasForge handles the pipeline that converts DB2 data into server-side hotfix overrides.
- The hotfixes database contains ~400K spell entries and ~237K hotfix_data rows.
- When the server says a spell, item, or creature "doesn't exist," it usually means the hotfix data is missing or mismatched -- not that the server code is broken.

## Scripting
- Server-side Lua scripting is provided by **Eluna**. Eluna scripts handle helper systems, professions, world chat, and various convenience commands.
- Core gameplay systems (transmog, companions, morphing, visual effects) are implemented in C++ for performance and reliability.

## Custom Systems Overview

### Helpers / Companion Squad
- Six named NPC companions that follow the player with role-based AI (tank, healer, DPS).
- Managed via `.comp` commands (`.comp summon`, `.comp dismiss`, `.comp role`, etc.).
- Companions use formation movement, auto-follow, and level alongside the player.
- Database entries are in the 500001-500005 range.

### Transmog Outfits
- Full wardrobe/outfit system adapted for the 12.x client transmog UI.
- Players can save and load multiple outfits covering all armor slots plus main-hand and off-hand weapons with multiple options each.
- Supports hidden appearances (head, shoulders, cloak, belt, etc.) and enchant visuals.

### Display Overrides (.display)
- Per-slot appearance overrides that let players change the look of individual equipment slots independently of transmog outfits.
- Part of the `RoleplayCore::DisplayHandler` system.

### Visual Effects (.effect)
- Persistent SpellVisualKit effects applied to players or NPCs.
- Effects are stored in the database and automatically re-applied on login.
- Supports late-join sync so other players see effects when they enter the area.

### Player Morph (.wmorph / .wscale / .remorph)
- `.wmorph [displayId]` -- morph the player to a different creature model.
- `.wscale [scale]` -- change the player's size.
- `.remorph` -- re-apply the current morph after zoning or reconnecting.
- Morphs are persistent across logout and login.

### Professions (.prof)
- Custom `.prof` commands covering 13 professions with learn, unlearn, max, and reset sub-commands.
- A client-side addon (`/profs`) provides a UI accessible through the Addon Compartment button.

### Custom NPCs (.cnpc)
- Player-race NPCs with fully customizable equipment and appearance.
- Created and managed via `.cnpc` (or `.customnpc`) commands.
- Custom NPC templates start at creature ID 400000+.

### Collector's Bounty
- A reward system for collectors that tracks and rewards exploration and acquisition milestones.

### Dragonriding / Skyriding (AdvFly)
- Custom spell support for 12.x dynamic flight (Skyriding).
- Available in supported zones.

### TimeIsTime
- Syncs the in-game time and weather to real-world time and conditions. When it is raining outside, it rains in Stormwind.

### SoloLFG
- Allows players to queue for and complete dungeon content solo or in small groups without the usual group size requirements.

### WorldChat
- A global cross-zone chat channel so players can communicate regardless of where they are in the world.

## Server Requirements (for self-hosting the repack)
- Windows 10/11 (64-bit).
- WoW retail client matching the server build (currently 66263).
- Arctium WoW Launcher.
- The repack bundle (includes worldserver, bnetserver, UniServerZ MySQL, and all databases).
- Extracted map data: maps, vmaps, mmaps (generated from the client using extractors included in the repack, or pre-extracted and bundled).
- At least 8 GB of RAM (16+ recommended). The worldserver alone uses 2-4 GB.
- Around 15 GB of disk space for databases + map data.

## Common Questions

- **"What kind of server is this?"** -- A TrinityCore-based roleplay private server running the Midnight (12.x) retail client. It is heavily customized with systems built specifically for RP.
- **"What expansion is this?"** -- 12.x / Midnight. You use the retail WoW client with the Arctium launcher to connect.
- **"Is this like MaNGOS or AzerothCore?"** -- No. VoxCore is based on TrinityCore but is roughly 15,000 commits diverged. It shares the TrinityCore architecture but has extensive custom systems.
- **"Do I need a retail subscription?"** -- No. You need the retail client files, but you do not need an active subscription. The Arctium launcher bypasses Battle.net authentication entirely.
- **"Can I play on Mac or Linux?"** -- The server itself is Windows-only. The client runs on Windows natively. Mac and Linux players may be able to run the client through compatibility layers (Wine/Proton) but this is not officially supported.

## Escalate When
- The player asks about server lore, storyline, or RP rules (these are community/staff decisions, not technical).
- The player asks about server hosting costs, hardware specifications, or uptime guarantees.
- The player asks about upcoming features or release timelines (only staff can commit to dates).
- The player reports a bug that requires server-side investigation or a code fix.
