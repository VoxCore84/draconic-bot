# Client Build -- DraconicWoW Requires Build 66263
Tags: client, build, version, mismatch, update, arctium, battle.net, auto-update, WOW51900319, 66263
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- DraconicWoW requires WoW client build **66263** (12.x / The War Within / Midnight era). No other build will work.
- Players MUST use the **Arctium WoW Launcher** to connect. The standard Battle.net launcher will NOT connect to DraconicWoW.
- Arctium Launcher redirects the WoW client to connect to the DraconicWoW private server instead of Blizzard's official servers. Without it, the client will attempt to log in to Blizzard and fail.
- Players should **never let their WoW client auto-update** through Battle.net. Blizzard pushes patches that change the build number, which will break compatibility with DraconicWoW.
- The client's current build number is displayed on the WoW login screen in the **bottom-left corner** (e.g., "Version 12.0.1.66263").
- The server's expected build number is printed in the worldserver console at startup.
- If the client and server builds do not match, the player is instantly disconnected with no useful error message from the game.
- The most common error code for a build mismatch is **WOW51900319** -- this is a generic "disconnected from server" error that almost always means the builds don't match.

## Common symptoms
- Instant disconnect when entering credentials or reaching the character screen.
- Error code **WOW51900319** appearing repeatedly, especially right after logging in.
- Client worked yesterday but fails today -- Blizzard silently pushed a patch overnight and the client auto-updated past build 66263.
- "Connecting..." hangs briefly then disconnects -- client build is too new or too old for the server.

## How to check your build
1. Open WoW using the Arctium Launcher (or even the normal launcher -- you just need to reach the login screen).
2. Look at the **bottom-left corner** of the login screen.
3. You should see something like **"Version 12.0.1.66263"**. The number after the last dot is the build number.
4. If it says 66263, your client is correct. If it says a higher number (e.g., 66337, 66500, etc.), your client has been updated past the supported build.

## Fix steps
1. **Check your build first.** Look at the login screen bottom-left. If it says 66263, your client is fine -- the problem is something else (see setup guide or common failures).
2. **If your build is wrong (too high):** Your WoW client has been updated past the server's supported version. You need to obtain the correct 66263 build client files. Ask in the DraconicWoW Discord for help getting the right version.
3. **Prevent future auto-updates:** Do NOT open the Battle.net launcher with WoW installed, or if you do, disable auto-updates: Battle.net Settings > Game Install/Update > uncheck automatic updates for WoW. Better yet, keep a separate WoW installation folder for DraconicWoW that Battle.net doesn't know about.
4. **Update Arctium Launcher:** The Arctium Launcher must also match the client build. If you have the right client build but Arctium crashes or fails to launch, download the latest Arctium version from the Arctium Discord that supports build 66263.
5. **For repack operators:** If you updated the server to support a new build, update the `realmlist` table in the auth database: `UPDATE realmlist SET gamebuild = 66263 WHERE id = 1;`

## Escalate when
- The player has confirmed build 66263 but still gets WOW51900319 (likely a network, firewall, or Arctium issue instead of a build mismatch).
- A new WoW patch dropped and the community is asking when the server will update.
- The player cannot find or obtain the 66263 client files.
