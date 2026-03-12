# Client Build Versions and Mismatches
Tags: client, build, version, mismatch, update, arctium, battle.net, auto-update, WOW51900319
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- Blizzard automatically updates the retail WoW client whenever a new patch or hotfix is released.
- The server expects a specific client build number. If the client build does not match the server build, the player is instantly disconnected.
- The most common error code for a build mismatch is WOW51900319 -- this is the generic "disconnected from server" error.
- The server's expected build number is shown in the worldserver console output at startup.
- The client's current build number is displayed on the login screen in the bottom-left corner.
- Arctium Launcher must also be compatible with the current client build -- outdated Arctium versions will fail to launch or crash.

## Common symptoms
- Instant disconnect upon entering credentials or reaching the character screen.
- Error code WOW51900319 appearing repeatedly.
- "The client and server builds don't match" or similar message in server logs.
- Client worked yesterday but fails today (Blizzard pushed an update overnight).

## Fix steps
1. Check the server build number in the worldserver console (printed at startup, e.g., "Client build: 66263").
2. Check the client build number on the WoW login screen (bottom-left corner).
3. If they do not match, the server operator needs to update the realmlist table in the auth database to accept the new build number. The SQL is: UPDATE realmlist SET gamebuild = <new_build> WHERE id = 1;
4. The server may also need a recompile if the new client build introduces protocol changes.
5. Download the latest Arctium Launcher from the Arctium Discord server. Old versions break with new builds.
6. To prevent unwanted client updates, disable auto-updates in the Battle.net launcher: Settings > Game Install/Update > uncheck automatic updates for WoW.
7. If the client already updated past the server's supported build, the player must wait for the server to catch up or find a way to roll back the client (difficult and unsupported).

## Escalate when
- The server operator needs to bump the server build (requires SQL update, possibly a recompile).
- The user reports that build numbers match but they still get WOW51900319 (could be a network or Arctium issue instead).
- A new WoW patch dropped and the server has not been updated yet.
