# Common Failures and Error Diagnosis
Tags: crash, error, disconnect, dc, mysql, uniserverz, database, maps, extractors, antivirus, port, WOW51900319, arctium, eluna, sicasforge, lag, rubberbanding, mmap
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- Most DraconicWoW server issues fall into these categories: MySQL/UniServerZ problems, missing map data, build mismatches, database import errors, Arctium issues, antivirus interference, or config mistakes.
- The worldserver console and log files (Server.log, DBErrors.log) are the primary diagnostic sources.
- Map data (maps, vmaps, mmaps) must be extracted from the WoW client using four extractor tools run in sequence.
- Antivirus software frequently quarantines server executables and extractors because they are unsigned binaries.
- DraconicWoW requires build 66263 with Arctium Launcher -- no other build or launcher will work.

## Common Failure: MySQL / UniServerZ won't start
- **Cause**: Port 3306 is already in use by another MySQL instance (XAMPP, WAMP, standalone MySQL, MariaDB), or UniServerZ itself is not running.
- **Symptoms**: UniServerZ MySQL indicator stays red, or worldserver exits immediately with "Cannot connect to MySQL."
- **Fix steps**:
  1. Check if another MySQL process is using port 3306: open Command Prompt and run `netstat -ano | findstr :3306`.
  2. If another process owns port 3306, stop it via Task Manager (look for mysqld.exe) or Services (look for "MySQL80" or similar).
  3. If you need both MySQL instances, change the port in UniServerZ: open `UniServerZ\core\mysql\my.ini`, change `port=3306` to an unused port (e.g., 3307), then update the port in worldserver.conf and bnetserver.conf connection strings to match.
  4. Make sure you start UniServerZ **before** starting the server executables.
  5. Test the connection manually: `mysql -u root -padmin -h 127.0.0.1 -P 3306` (default UniServerZ credentials are root/admin).

## Common Failure: worldserver crashes on startup (missing map data)
- **Cause**: Map, vmap, or mmap data files have not been extracted from the WoW client, or they were extracted from the wrong client version.
- **Symptoms**: worldserver.exe crashes or exits shortly after startup with errors about missing map files, or crashes when a player logs into a zone.
- **Fix steps**:
  1. You need to run four extractors **in order** from inside your WoW `_retail_` folder: `mapextractor` -> `vmap4extractor` -> `vmap4assembler` -> `mmaps_generator`.
  2. Make sure WoW is fully downloaded first (not just "Playable" -- wait until it says "Up to date" or reaches 100%).
  3. Copy the four extractor executables into your `_retail_` folder and run them from there.
  4. After extraction, copy the output folders (maps/, vmaps/, mmaps/) to the server's data directory.
  5. Verify that `DataDir` in worldserver.conf points to the folder containing these subdirectories.
  6. Note: mmaps_generator can take several hours. It is optional but strongly recommended -- without it, NPC pathfinding will not work properly.
  7. If extractors disappear or won't run, check antivirus (see the antivirus section below).

## Common Failure: Can't connect / WOW51900319
- **Cause**: Build mismatch between your WoW client and the DraconicWoW server. DraconicWoW requires **build 66263** specifically.
- **Symptoms**: Instant disconnect with error code WOW51900319 after entering credentials, or the client refuses to connect at all.
- **Fix steps**:
  1. DraconicWoW only works with **build 66263**. Check your client build on the login screen (bottom-left corner).
  2. You **must** use Arctium Launcher to connect -- the standard Battle.net launcher will not work and will auto-update your client past the supported build.
  3. If your client has already updated past 66263, you will need to obtain the correct client version.
  4. Verify your realmlist is set correctly in the Arctium configuration to point to the DraconicWoW server address.

## Common Failure: "Database not found" errors
- **Cause**: One or more of the five databases (auth, characters, world, hotfixes, roleplay) have not been created or imported.
- **Symptoms**: worldserver exits with database connection errors, or loads but is missing data (no NPCs, no items, no quests).
- **Fix steps**:
  1. Check `DBErrors.log` in the server runtime directory -- it will tell you exactly which database or table is missing.
  2. Ensure all five databases exist in MySQL: auth, characters, world, hotfixes, and roleplay.
  3. Re-import the SQL files for the missing database using SQLyog, HeidiSQL, or the mysql command line: `mysql -u root -padmin < filename.sql`.
  4. For large imports (world database), use the command line -- GUI tools may time out.
  5. After importing, restart the worldserver.

## Common Failure: Arctium Launcher won't start
- **Cause**: Missing .NET runtime, or antivirus has quarantined the Arctium files.
- **Symptoms**: Arctium Launcher shows a .NET error dialog, crashes immediately, or simply does not appear after double-clicking.
- **Fix steps**:
  1. Install the latest .NET Desktop Runtime from Microsoft (https://dotnet.microsoft.com/download). Arctium requires .NET 6.0 or newer.
  2. Check Windows Defender (or your antivirus) quarantine list -- Arctium executables are frequently flagged as false positives.
  3. Add the entire Arctium folder as an exclusion in Windows Defender: Settings > Virus & threat protection > Exclusions > Add folder.
  4. Try running Arctium as Administrator.
  5. Get the latest Arctium version from the Arctium Discord if your copy is outdated.

## Common Failure: Server starts but no NPCs/creatures
- **Cause**: Map data was extracted but the world database was not imported, or `DataDir` in worldserver.conf points to the wrong location.
- **Symptoms**: You can log in and move around, but the world is empty -- no NPCs, no creatures, no vendors, no quest givers.
- **Fix steps**:
  1. This almost always means the **world database** is empty or was not imported. Check by running: `SELECT COUNT(*) FROM world.creature;` -- if it returns 0 or errors, the world DB needs to be imported.
  2. Import the world database SQL files. This is the largest database and may take several minutes.
  3. Also verify that `DataDir` in worldserver.conf is correct -- if it points to a nonexistent folder, the server will load but some data will be missing.
  4. Restart the worldserver after importing.

## Common Failure: Lag / rubber-banding
- **Cause**: mmaps (movement maps) were not generated, so NPC pathfinding is disabled. Or the host PC does not have enough resources.
- **Symptoms**: NPCs walk through walls, get stuck, or players experience rubber-banding and delayed movement.
- **Fix steps**:
  1. Check worldserver.conf for `mmap.enablePathFinding = 1`. If this is set to 0, pathfinding is disabled.
  2. If pathfinding is enabled but the mmaps/ folder is empty or missing, you need to run `mmaps_generator` from the `_retail_` folder.
  3. mmaps generation takes several hours but only needs to be done once.
  4. If lag persists with mmaps present, check your PC resources -- worldserver can be CPU-intensive. Close unnecessary background applications.
  5. Check the worldserver console for warnings about update diff time -- values consistently above 100ms indicate the server is struggling.

## Common Failure: Eluna script errors
- **Cause**: Lua scripts have errors, the AIO addon is missing on the client side, or the `lua_scripts` path in worldserver.conf is wrong.
- **Symptoms**: Features powered by Eluna (like Helpers/Companions UI, profession commands) do not work. Error messages appear in the worldserver console or in the eluna log folder.
- **Fix steps**:
  1. Check the worldserver console for Lua error messages -- they will show the file and line number.
  2. Verify `Eluna.ScriptPath` in worldserver.conf points to the correct lua_scripts folder.
  3. If the AIO (Addon IO) system features are broken, make sure the AIO addon is installed in the client's AddOns folder.
  4. After fixing scripts, you can reload them with `.reload eluna` in the worldserver console (no restart needed for most Lua changes).

## Common Failure: Antivirus false positives
- **Cause**: Windows Defender or other antivirus software quarantines or deletes unsigned server executables.
- **Symptoms**: worldserver.exe, bnetserver.exe, extractors, or Arctium files disappear or fail to run. Windows may show a "Threat detected" notification.
- **Fix steps**:
  1. Open Windows Security > Virus & threat protection > Protection history to see if files were quarantined.
  2. Restore any quarantined files.
  3. Add folder exclusions for: the server directory, the Arctium folder, and the WoW `_retail_` folder (where extractors run).
  4. In Windows Defender: Settings > Virus & threat protection > Manage settings > Exclusions > Add or remove exclusions > Add a folder.
  5. If using third-party antivirus (Norton, McAfee, Kaspersky, etc.), add the same exclusions in that software's settings.
  6. After adding exclusions, re-extract or re-copy any files that were deleted.

## Common Failure: SicasForge errors
- **Cause**: Hotfix data tool failures, usually due to a database schema mismatch between the SicasForge version and the current database state.
- **Symptoms**: SicasForge tools fail with SQL errors, missing column errors, or produce corrupted hotfix data. The worldserver may crash or show hotfix-related errors on startup.
- **Fix steps**:
  1. Make sure you are using the SicasForge tools from the correct `SicasForge2.0` folder that matches your server version.
  2. Re-run the SicasForge tools from scratch rather than trying to fix partial output.
  3. Check that the hotfixes database schema matches what SicasForge expects -- if you have applied custom SQL updates, they may have changed the schema.
  4. If errors persist, reimport the hotfixes database from the base SQL files, then re-run SicasForge.

## Escalate when
- The user has provided logs and the error does not match any of the categories above.
- The server is crashing with a C++ exception or access violation (needs developer investigation).
- The issue is specific to one player's character (possible data corruption -- may need database-level fixes).
- Database migration or schema upgrade issues are involved.
- The user has tried all fix steps for their category and the problem persists.
