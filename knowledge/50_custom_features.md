# DraconicWoW Custom Features
Tags: transmog, companion, roleplay, custom, npc, visual, effect, morph, outfit, profession
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- DraconicWoW includes several custom systems built specifically for roleplay and quality-of-life improvements.
- These systems are actively in development and may have bugs or incomplete features. Report issues to staff.

## Transmog Outfits
- Full wardrobe/outfit system adapted for the 12.x client transmog UI.
- Players can save and load multiple transmog outfits.
- Supports armor, weapons (main-hand and off-hand with multiple options), hidden appearances, and enchant visuals.
- Uses the .display command family for per-slot appearance overrides.
- Known quirk: some slots may require re-equipping to refresh the visual.

## Companion Squad
- DB-driven NPC companions that follow the player.
- Companions have role-based AI: tank, healer, or DPS.
- Managed via the .comp command family (e.g., .comp summon, .comp dismiss, .comp role).
- Companions use formation movement and follow the player automatically.
- Companion entries are in the 500001-500005 range in the database.

## Custom NPCs
- Player-race NPCs with fully customizable equipment and appearance.
- Created and managed via .cnpc (or .customnpc) commands.
- Custom NPCs start at creature template ID 400000+.
- Supports custom outfits, equipment slots, and racial appearances.

## Visual Effects
- Persistent SpellVisualKit effects applied via .effect commands.
- Effects are stored in the database and re-applied on login.
- Supports late-join sync so other players see effects when they enter the area.
- Part of the Noblegarden::EffectsHandler system.

## Player Morph
- .wmorph [displayId] -- Morph the player to a different creature display.
- .wscale [scale] -- Change the player's scale (size).
- .remorph -- Re-apply the current morph (useful after zoning or reconnecting).
- Morphs are persistent across logout/login.

## Professions
- .prof command family for managing professions.
- Supports 13 professions with learn, unlearn, max, and reset sub-commands.
- Client-side addon (/profs) provides a UI with an Addon Compartment button.

## Dragonriding / Skyriding
- Custom spell support for 12.x dynamic flight (Skyriding).
- Players can use Skyriding in supported zones.

## Common symptoms
- "How do I transmog?" -- Use the transmog NPC or the wardrobe UI. Custom overrides use .display commands.
- "How do I get a companion?" -- Use .comp summon to summon a companion. You need GM permissions or a designated command for players.
- "My morph disappeared" -- Try .remorph to re-apply it.
- "Can I fly?" -- Skyriding is available in supported zones. Check with staff which zones have it enabled.

## Escalate when
- The user reports a bug with a custom system (transmog visual glitch, companion AI issues, morph not persisting).
- The user wants a feature that does not exist yet.
- The user encounters a crash related to a custom system.
