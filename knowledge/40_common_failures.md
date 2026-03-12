# Common Failures and Error Diagnosis
Tags: crash, error, disconnect, dc, mysql, database, maps, extractors, antivirus, openssl, port, WOW51900319, black screen, loading
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- Most server issues fall into a few categories: database problems, missing map data, build mismatches, config errors, or antivirus interference.
- The worldserver console and log files (Server.log, DBErrors.log) are the primary diagnostic sources.
- Map data (maps, vmaps, mmaps) must be extracted from the WoW client using dedicated extractor tools.
- Antivirus software frequently quarantines or deletes server executables and extractors because they are unsigned binaries.

## Common Failure: Server crashes on player login
- **Cause**: Missing or incomplete map/vmap/mmap data.
- **Symptoms**: Server runs fine until a player logs in or loads into a zone, then crashes.
- **Fix steps**:
  1. Verify that the maps/, vmaps/, and mmaps/ folders exist in the server's data directory.
  2. Check that DataDir in worldserver.conf points to the correct location.
  3. If missing, re-extract using the 4 extractors in order: mapextractor -> vmapextractor -> vmap4assembler -> mmaps_generator.
  4. Extractors must be run from inside the _retail_ folder (they read client data files).
  5. Copy the output folders (maps, vmaps, mmaps) to the server's data directory.
  6. Check if antivirus quarantined any extractor executables. Add exclusions for the server directory.

## Common Failure: Database connection failed
- **Cause**: MySQL is not running, port 3306 is in use by another process, or credentials in worldserver.conf are wrong.
- **Symptoms**: worldserver.exe exits immediately with "Cannot connect to MySQL" or similar error.
- **Fix steps**:
  1. Confirm MySQL is running (check UniServerZ tray icon, or run netstat -an | findstr 3306).
  2. If port 3306 is in use by another MySQL instance, stop the conflicting instance or change the port.
  3. Verify the MySQL credentials in worldserver.conf and bnetserver.conf match your MySQL root user (default: root/admin for UniServerZ).
  4. Test the connection manually: mysql -u root -padmin -h 127.0.0.1 -P 3306.
  5. If using XAMPP, MariaDB, or another MySQL variant, ensure compatibility with MySQL 8.0 syntax.

## Common Failure: Build mismatch / WOW51900319
- **Cause**: Client auto-updated to a newer build than the server supports.
- **Symptoms**: Instant disconnect with error WOW51900319 after entering credentials.
- **Fix steps**:
  1. Compare build numbers: worldserver console vs. client login screen (bottom-left).
  2. If mismatched, server operator must update auth.realmlist gamebuild column.
  3. Get latest Arctium from their Discord.
  4. Disable Battle.net auto-updates to prevent future mismatches.

## Common Failure: Map extraction problems
- **Cause**: Extractors were run from the wrong directory, or WoW was still downloading when extraction started.
- **Symptoms**: Missing map files, server crashes when loading zones, or "Map X not found" errors in logs.
- **Fix steps**:
  1. Ensure WoW is fully downloaded (no "Playable" vs "Optimal" -- wait for Optimal).
  2. Place all 4 extractors in the _retail_ folder.
  3. Run in order: mapextractor, vmapextractor, vmap4assembler, mmaps_generator.
  4. mmaps_generator takes a very long time (hours). It is optional but recommended for pathfinding.
  5. Copy the output (maps/, vmaps/, mmaps/) to the server data directory.
  6. Verify DataDir in worldserver.conf points to the folder containing these subdirectories.

## Common Failure: OpenSSL build errors
- **Cause**: Wrong OpenSSL version or wrong library path during compilation.
- **Symptoms**: CMake errors about missing OpenSSL, or linker errors referencing SSL symbols.
- **Fix steps**:
  1. Install OpenSSL 3.x full (not Light) for Win64.
  2. Set OPENSSL_ROOT_DIR CMake variable to the OpenSSL install path.
  3. Use the lib/VC/x64/MD/ libraries, NOT the lib/ root.
  4. Ensure the OpenSSL DLLs are in the server's runtime directory or in PATH.

## Common Failure: Port already in use
- **Cause**: Another instance of bnetserver/worldserver is still running, or another application uses port 1119/8085/3306.
- **Symptoms**: "Address already in use" or "Bind failed" error on startup.
- **Fix steps**:
  1. Run netstat -ano | findstr :1119 (bnet) or netstat -ano | findstr :8085 (world) to find the conflicting process.
  2. Kill the process using Task Manager or taskkill /PID <pid> /F.
  3. If another MySQL instance is on 3306, stop it or change the port in worldserver.conf.

## Common Failure: Config issues
- **Cause**: DataDir, MySQLExecutable, or connection strings in worldserver.conf are incorrect.
- **Symptoms**: Varies -- database errors, missing data errors, or silent failures.
- **Fix steps**:
  1. Open worldserver.conf and verify DataDir points to the folder containing maps/vmaps/mmaps.
  2. Verify all DatabaseInfo connection strings have the correct host, port, user, password, and database name.
  3. Ensure MySQLExecutable (if set) points to a valid mysql.exe path.
  4. Check BindIP is 0.0.0.0 (all interfaces) or the correct specific IP.

## Common Failure: Black screen or infinite loading
- **Cause**: Usually missing client data, corrupted cache, or addon conflicts.
- **Symptoms**: Client shows a black screen after character select, or the loading bar never completes.
- **Fix steps**:
  1. Delete the WoW cache folder: _retail_/Cache/.
  2. Disable all addons and try again.
  3. If the issue is zone-specific, the server may be missing map data for that zone.
  4. Check worldserver console for errors when the player enters the problematic zone.

## Escalate when
- The user has provided logs and the error does not match any known pattern.
- The server is crashing with a C++ exception or access violation (needs developer investigation).
- The issue is specific to one player's character (possible data corruption).
- Database migration or schema issues are involved.
