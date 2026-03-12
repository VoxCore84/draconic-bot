# Setup and Connection Guide
Tags: setup, connect, login, realmlist, config, port, bnetserver, worldserver, 127.0.0.1, Config.wtf, account, arctium, install
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- A full setup requires: WoW retail client, Arctium Launcher, MySQL database, and the server binaries (bnetserver + worldserver).
- The WoW client is installed via the official Battle.net launcher, then patched to connect to the private server using Arctium.
- Arctium Launcher must be placed inside the WoW _retail_ folder (e.g., C:\WoW\_retail_\).
- The server address is configured in Config.wtf (located in the WoW WTF folder).
- For local (same-machine) play, the portal and realmlist address should be 127.0.0.1.
- For LAN or remote play, use the server machine's LAN IP or public IP, and ensure port forwarding is set up.

## Fix steps
1. **Install WoW**: Use the Battle.net launcher to install World of Warcraft retail. Let it fully download and update.
2. **Download Arctium**: Get the latest Arctium Launcher from the Arctium Discord. Place Arctium WoW Launcher.exe (and its files) directly inside the _retail_ folder.
3. **Start MySQL**: Launch your MySQL server (UniServerZ, XAMPP, or standalone MySQL 8.0). Ensure it is running on port 3306.
4. **Start bnetserver**: Run bnetserver.exe. Wait until it says it is listening for connections. This handles login/authentication.
5. **Start worldserver**: Run worldserver.exe. Wait until it prints "World initialized" in the console. This is the game server.
6. **Edit Config.wtf**: Open WTF\Config.wtf in a text editor. Add or change: SET portal "127.0.0.1" (use the server's IP if connecting remotely).
7. **Create an account**: In the worldserver console, type: bnetaccount create youremail@example.com yourpassword
8. **Set GM level** (optional): In the worldserver console, type: account set gmlevel youremail@example.com 3 -1 (3 = full admin, -1 = all realms).
9. **Launch the game**: Double-click Arctium WoW Launcher.exe inside the _retail_ folder. Do NOT launch from Battle.net.
10. **Log in**: Use the email and password you created in step 7.

## Common symptoms
- "Can't connect to server" -- bnetserver or worldserver is not running, or Config.wtf portal is wrong.
- Stuck on "Connecting" -- Firewall blocking port 1119 (bnet) or 8085 (world), or wrong IP in Config.wtf.
- "Wrong password" -- Account was not created, or email/password was typed incorrectly.
- Client crashes on launch -- Arctium is not in the _retail_ folder, or Arctium version is outdated, or CPU does not support AVX2 (required by some Arctium builds).
- "World server is down" -- worldserver.exe is not running or crashed during startup. Check its console for errors.

## Connection Troubleshooting Checklist
1. Is MySQL running? (Check UniServerZ tray icon, or run netstat -an | findstr 3306)
2. Is bnetserver running and showing "Listening on 0.0.0.0:1119"?
3. Is worldserver running and showing "World initialized"?
4. Does Config.wtf contain SET portal "127.0.0.1" (or the correct server IP)?
5. Is the realmlist table in the auth database set to 127.0.0.1 (or the server IP)?
6. Is Windows Firewall allowing bnetserver.exe and worldserver.exe through? (Or temporarily disable firewall to test.)
7. Is Arctium inside the _retail_ folder, not the WoW root folder?
8. Does the CPU support AVX2? (Check with CPU-Z or similar.)

## Escalate when
- The user has followed all steps and still cannot connect.
- The user is trying to set up remote/LAN access and needs port forwarding help.
- The user is trying to set up a dedicated server on a VPS or cloud instance.
