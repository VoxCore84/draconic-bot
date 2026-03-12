# Arctium Guide -- Products, Troubleshooting, and Safety
Tags: arctium, launcher, connection, custom-server, ban, eidolon, troubleshoot, crash, version, build
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Arctium Basics

Arctium makes two distinct products that players frequently confuse:

1. **Arctium App** (also called "Arctium Mod Launcher" or "Arctium Launcher"): A mod launcher for retail/live WoW. Available on the Microsoft Store. Used to load visual mods (model swaps, custom textures, UI overhauls) while connected to official Blizzard servers. Does NOT create private servers.

2. **Arctium Custom Server Launcher**: A connection tool for private servers. Downloaded from arctium.io (NOT the Microsoft Store). Redirects the WoW client to connect to a private server address instead of Blizzard's servers. This is what DraconicWoW uses.

**DraconicWoW requires the Custom Server Launcher.** The Arctium App from the Microsoft Store will NOT connect you to DraconicWoW. If someone says "I installed Arctium from the Store" -- they have the wrong product.

The Custom Server Launcher works by intercepting the WoW client's connection and redirecting it to the private server's IP/hostname. Without it, the WoW client will always try to connect to Blizzard's official servers and fail.

## "Unsupported game client version" Error

This is the single most common Arctium issue. Over 60 occurrences in the Arctium Discord support channel alone.

**What it means (for retail Arctium App users):** The Arctium App has not been updated to support the current WoW build yet. After Blizzard pushes a new patch, there is usually a short window (hours to a few days) before Arctium releases an update. During this window, the App will refuse to launch WoW with this error.

**What it means for DraconicWoW players:** This is a build mismatch. DraconicWoW runs on build **66263**. If your WoW client has been updated past this build by Battle.net, the Custom Server Launcher cannot use it. You need the correct 66263 client, NOT a launcher update.

**Workarounds (retail Arctium App):**
- Disable automatic game updates in Battle.net: Settings > Game Install/Update > uncheck auto-update for WoW.
- Uncheck "Auto Login" in the Arctium App so it doesn't try to launch immediately on startup.
- Wait for Arctium to push an update supporting the new build (check their Discord #announcements).

**Fix for DraconicWoW:**
- Verify your client build on the login screen (bottom-left corner). It must say 66263.
- If your build is higher than 66263, your client has been auto-updated. You need to obtain the correct client version.
- Keep a separate WoW installation folder for DraconicWoW that Battle.net does not manage.

## Launcher Won't Start / Crashes

Common error types seen in the Arctium community:

- **NullReferenceException**: Usually means the launcher could not find or parse expected game files. Verify you selected the correct Wow.exe from the `_retail_` folder.
- **System.InvalidOperationException**: Often caused by a leftover WoW process from a previous session. Kill it in Task Manager first.
- **HttpRequestException**: The launcher could not reach the Arctium update server or authentication endpoint. Check your internet connection and firewall rules.

**Fix steps (in order):**
1. Open Task Manager and kill any running `Wow.exe` or `WowT.exe` processes. Zombie WoW processes from previous sessions are the most common cause of launch failures.
2. Make sure you selected the correct executable. The launcher needs `Wow.exe` from inside the `_retail_` folder (e.g., `C:\WoW\_retail_\Wow.exe`), NOT the Battle.net launcher and NOT the `WowB.exe` beta executable.
3. Run the launcher as Administrator (right-click > Run as administrator). Some systems block unsigned executables from modifying other processes without elevation.
4. Check Windows Defender or your antivirus quarantine list. Arctium files are frequently flagged as false positives. Add the entire Arctium folder as an exclusion.
5. Verify that the .NET Desktop Runtime is installed. The Custom Server Launcher requires .NET 6.0 or newer. Download from https://dotnet.microsoft.com/download if missing.
6. If none of the above work, re-download the launcher from arctium.io (Custom Server) or the Microsoft Store (App). Your copy may be corrupted.

## Ban Safety

This section applies to the **Arctium App** used on retail/live Blizzard servers. The Custom Server Launcher for private servers has zero ban risk because you are not connecting to Blizzard at all.

**History:**
- The only ban wave involving Arctium occurred in **April 2019**. Blizzard mass-banned Arctium users.
- The bans were **fully reverted** by Blizzard within days. All affected accounts were restored.
- There have been **no bans** related to Arctium usage since then (as of March 2026).

**Why it's considered safe:**
- Arctium preserves all of WoW's security features. It does NOT disable, bypass, or tamper with Blizzard's anti-cheat systems (Warden, Eidolon).
- Arctium loads mods by redirecting file reads, not by injecting code into the game process.
- Blizzard CAN detect that Arctium is running (it is not invisible), but has chosen not to act on it since the 2019 reversal.

**Caveats:**
- Blizzard tracks hardware IDs (HWID). Creating a "burner account" to test with does not protect your main account if both are used on the same machine.
- Past safety does not guarantee future safety. Blizzard's enforcement policy could change at any time.
- Using Arctium alongside other tools (especially memory editors, bots, or iMorph) significantly increases risk. Arctium itself is not the problem, but stacking tools is.

**For DraconicWoW:** There is no ban risk. You are connecting to a private server, not to Blizzard. Blizzard has no visibility into your connection and no ability to ban you for playing on a private server through Arctium.

## Eidolon Anti-Cheat (11.2+)

Starting with patch 11.2, Blizzard introduced **Eidolon**, a new anti-tamper and anti-cheat system integrated into the WoW client.

**Key points:**
- Eidolon detects unauthorized memory modifications, code injection, and process tampering.
- The Arctium App is designed to work alongside Eidolon, not against it. Arctium does not tamper with WoW's memory in ways that trigger Eidolon. This was a deliberate design decision after the 2019 ban wave.
- **Crash code 0xC00000E5**: This Windows error code (STATUS_INVALID_IMAGE_FORMAT) means something attempted to modify WoW's memory in a way Eidolon rejected. This is NOT caused by Arctium. It typically means another tool (an overlay, injector, or memory editor) is interfering.
- If you see 0xC00000E5 crashes, close all overlays, screen recorders, performance monitors, and other tools that hook into game processes. Common culprits: RivaTuner/MSI Afterburner overlay, some Discord overlay configurations, ReShade with depth buffer access.

**For DraconicWoW:** Eidolon is not relevant. The private server build does not enforce Eidolon, and the Custom Server Launcher does not interact with it. If you see 0xC00000E5 on a private server, the cause is something else (likely antivirus or a corrupted executable).

## Common Troubleshooting

### "Nothing happens when I click Launch"
1. Check Task Manager for a zombie `Wow.exe` process and kill it. This is the cause in the majority of cases.
2. Verify you selected the correct .exe (`_retail_\Wow.exe`).
3. Try running the launcher as Administrator.
4. If using the Custom Server Launcher, make sure you entered the correct server address before clicking Launch.

### Visual LOD bugs with mods (Arctium App)
Some visual mods cause level-of-detail (LOD) issues where textures or models appear low-resolution or pop in at close range.
- **Fix**: Open the in-game chat and type `/console entityLodDist 300` (adjusts entity LOD distance).
- This setting does not persist across sessions in all cases. You may need to re-enter it after relaunching.
- Alternatively, add `SET entityLodDist "300"` to your `Config.wtf` file.

### Disconnects while playing
- Disconnects during gameplay are NOT caused by the Arctium Launcher. This has been confirmed by Fabian (the Arctium developer) multiple times in their Discord.
- Once the launcher has redirected your connection and WoW is running, the launcher is no longer in the data path. Disconnects are caused by server issues, network problems, or client bugs.
- For DraconicWoW: check your internet connection, check if the server is still running, and check the server's `Server.log` for crash information.

### Intel 13th/14th Gen CPU crashes
- Intel's 13th and 14th generation desktop CPUs (Raptor Lake / Raptor Lake Refresh) have a known hardware defect causing instability under sustained workloads. This affects ALL applications, not just WoW or Arctium.
- **Symptoms**: Random crashes, freezes, or BSODs, especially under load. May appear as WoW crashes with no clear error.
- **Workarounds**:
  - Apply Intel's latest microcode update (check your motherboard manufacturer for a BIOS update).
  - Lower the CPU's boost clock speed in BIOS (Intel has acknowledged the issue is related to excessive voltage at high clocks).
  - Try running WoW in DirectX 11 mode instead of DirectX 12 (`-d3d11` launch argument or set in System > Advanced in-game).

### Linux / Wine / Proton
- The Arctium Custom Server Launcher works under Wine/Proton on Linux.
- Common issue: Wine's Windows version registry keys may be set incorrectly. The launcher expects Windows 10 or newer.
- **Fix**: Run `winecfg`, go to the Applications tab, and set the Windows version to "Windows 10" or "Windows 11".
- Some users report needing to install `dotnet6` via `winetricks` for the Custom Server Launcher.
- The Arctium App (MS Store version) does NOT work under Wine due to MSIX packaging.

## Sandbox vs Launcher vs iMorph

Players frequently confuse these three tools. They are completely different products with different purposes:

### Arctium Sandbox
- A local-only exploration server. Lets you load WoW zones and walk around without connecting to any server (official or private).
- Primarily used for exploring alpha/beta content or zones that are not normally accessible.
- Does NOT support gameplay features (no NPCs, no quests, no combat, no multiplayer).
- NOT a playable server. Cannot be used instead of DraconicWoW or any other private server.
- You cannot "play on" the Sandbox. It is a development/exploration tool only.

### Arctium Launcher (App or Custom Server)
- The actual connection tool. The App connects to retail with mods; the Custom Server Launcher connects to private servers.
- This is the tool DraconicWoW players need.
- Actively maintained by the Arctium team (Fabian and contributors).

### iMorph
- A completely separate tool. NOT made by Arctium. NOT affiliated with Arctium.
- Allows real-time visual morphing (changing your character's appearance, race, gear visuals) client-side only. Other players do not see your changes.
- Works by modifying WoW's memory at runtime -- this is fundamentally different from how Arctium works.
- **Higher ban risk** than Arctium because it directly modifies game memory, which is exactly what Warden and Eidolon are designed to detect.
- DraconicWoW has its own built-in morph commands (`.wmorph`, `.wscale`, `.remorph`) that work server-side and are visible to all players. You do not need iMorph.

## Escalate when
- The player has tried all troubleshooting steps and the launcher still will not start.
- The player is getting errors not listed here (especially .NET errors with specific exception details).
- The player is asking about Arctium Sandbox setup for development purposes (this is not a standard player support topic).
- The player reports being banned and believes it is related to Arctium usage.
- The player is trying to use the Arctium App (retail) on DraconicWoW or vice versa and is confused about which product they need.
