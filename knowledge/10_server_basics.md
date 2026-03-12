# Server Basics -- DraconicWoW Overview
Tags: server, trinitycore, private, midnight, 12.x, client, wow
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- DraconicWoW is a TrinityCore-based private WoW server targeting the 12.x / Midnight client expansion.
- The server is roleplay-focused, with custom systems designed for immersive RP experiences.
- It runs on a fork called VoxCore, which is approximately 15,000 commits ahead of upstream TrinityCore.
- The server uses 5 databases: auth, characters, world, hotfixes, and roleplay.
- MySQL 8.0 is the required database engine (typically bundled via UniServerZ).
- The server consists of two executables: bnetserver (authentication) and worldserver (game logic).

## Custom Systems
- **Transmog Outfits** -- Full wardrobe/outfit system adapted for the 12.x client transmog UI.
- **Companion Squad** -- DB-driven NPC companions that follow the player with role-based AI (tank, healer, DPS).
- **Custom NPCs** -- Player-race NPCs with custom equipment and appearance, created via .cnpc commands.
- **Visual Effects** -- Persistent SpellVisualKit effects applied via .effect commands with late-join sync.
- **Player Morph** -- Persistent morph and scale via .wmorph, .wscale, and .remorph commands.
- **Professions** -- Custom .prof commands for learning and managing professions.
- **Dragonriding / Skyriding** -- Custom spell support for 12.x dynamic flight.

## Requirements
- WoW retail client (matching the server's target build number).
- Arctium Launcher (required to connect a retail client to a private server).
- Server binaries: bnetserver and worldserver (compiled from VoxCore source or distributed as a repack).
- MySQL 8.0 database server.
- Extracted map data: maps, vmaps, mmaps (generated from the client).

## Common symptoms
- "What kind of server is this?" -- It is a TrinityCore-based roleplay server on the Midnight (12.x) client.
- "What expansion is this?" -- 12.x / Midnight. The retail client is used with Arctium to connect.
- "Is this like MaNGOS or AzerothCore?" -- No, it is based on TrinityCore but heavily customized.

## Escalate when
- The user asks about the server's lore, storyline, or RP rules (these are community/staff decisions, not technical).
- The user asks about server hosting costs, hardware, or uptime guarantees.
