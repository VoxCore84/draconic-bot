# Setup and Connection Guide -- DraconicWoW
Tags: setup, connect, login, realmlist, config, port, bnetserver, worldserver, 127.0.0.1, Config.wtf, account, arctium, install, repack, UniServerZ, port-forward
Last reviewed: 2026-03-12
Owner: DraconicWoW Staff

## Facts
- DraconicWoW is distributed as a repack -- a self-contained package with server binaries, databases, and tools.
- The repack includes UniServerZ (a bundled MySQL server), so players do not need to install MySQL separately.
- Two server processes must be running: **bnetserver** (handles authentication/login) and **worldserver** (handles the game world).
- The WoW client connects through the **Arctium WoW Launcher**, which redirects the retail client to the private server.
- Default database credentials are `root` / `admin` on `127.0.0.1:3306`.

---

## Repack Setup (Self-Hosted / Single-Player)

### Step-by-step installation

1. **Extract the repack.** Unzip the repack archive to a folder on your drive. **Avoid** `C:\Program Files\`, paths with spaces, or deeply nested directories. Good example: `C:\DraconicWoW\` or `D:\Servers\DraconicWoW\`.

2. **Start UniServerZ (MySQL).** Navigate to the `UniServerZ` folder inside the repack. Run `UniController.exe`. Click **"Start Apache"** and **"Start MySQL"**. Both indicators should turn green. MySQL must be running before the server can start.

3. **Import databases.** The repack comes with SQL files to create and populate the 5 databases: `auth`, `characters`, `world`, `hotfixes`, and `roleplay`. Follow the included import instructions (usually a batch file or README). If importing manually, use the MySQL command line or a tool like HeidiSQL.

4. **Edit worldserver.conf (if needed).** The config file is in the server's `bin` folder. Key settings:
   - Database connection strings default to `127.0.0.1;3306;root;admin` -- these match UniServerZ defaults and usually need no changes.
   - `BindIP = "127.0.0.1"` -- correct for local play, change to `"0.0.0.0"` for remote play (see below).

5. **Run map extractors (if needed).** The server requires extracted map data to function. If the repack does not include pre-extracted maps, you need to run the extractors from the `bin` folder against your WoW client directory:
   - `mapextractor.exe` -- extracts base map data
   - `vmap4extractor.exe` -- extracts visual/collision map data
   - `vmap4assembler.exe` -- assembles vmaps into usable format
   - `mmaps_generator.exe` -- generates movement/pathfinding meshes (this one takes a long time)
   - Copy the resulting `maps/`, `vmaps/`, `mmaps/` folders into the server's `bin` directory.

6. **Start bnetserver.** Run `bnetserver.exe` from the `bin` folder. Wait until the console says it is listening for connections. This must start **before** worldserver.

7. **Start worldserver.** Run `worldserver.exe` (or `worldserver-restarter.bat` for auto-restart on crash). Wait until the console prints **"World initialized"** -- this means the server is ready to accept players.

8. **Launch WoW with Arctium.** Use the **Arctium WoW Launcher** to start the game. Set the realmlist/portal to `127.0.0.1` for local play. Do NOT launch through Battle.net.

9. **Create an account.** In the worldserver console window, type:
   ```
   bnetaccount create email@email.com password
   ```
   Replace with your desired email and password. This is what you will use to log in.

10. **Set GM level (optional).** In the worldserver console, type:
    ```
    account set gmlevel email@email.com 3 -1
    ```
    Level 3 = full administrator. `-1` = all realms.

---

## Remote Play (Playing with Friends)

If you want friends to connect to your server over the internet:

1. **Change BindIP.** In `worldserver.conf`, change `BindIP` from `"127.0.0.1"` to `"0.0.0.0"` so the server listens on all network interfaces.

2. **Update the realmlist table.** In the `auth` database, update the `realmlist` table so the `address` column contains your **public IP address** (not 127.0.0.1). You can find your public IP at https://whatismyip.com. SQL:
   ```sql
   UPDATE realmlist SET address = 'YOUR.PUBLIC.IP' WHERE id = 1;
   ```

3. **Port-forward on your router.** Forward these ports to your server machine's local IP:
   - **3724** (TCP) -- Battle.net authentication (bnetserver)
   - **8085** (TCP) -- World server (game traffic)
   - **8086** (TCP) -- Instance server (dungeon/raid traffic)

4. **Allow through Windows Firewall.** Add firewall exceptions for `bnetserver.exe` and `worldserver.exe`, or allow inbound TCP on ports 3724, 8085, and 8086.

5. **Friends connect.** Your friends set their realmlist/portal to your **public IP address** in the Arctium Launcher and log in with accounts you created for them.

### Common remote play issues
- **"Can't connect"** -- Ports not forwarded, or Windows Firewall is blocking the server executables.
- **Router doesn't support port forwarding** -- Some ISPs use CGNAT (carrier-grade NAT), which prevents port forwarding. You may need to contact your ISP or use a VPN/tunneling service like ZeroTier or Tailscale.
- **Friends can connect to bnet but get "World server is down"** -- Port 8085 is not forwarded, or the `realmlist` table still has 127.0.0.1 instead of your public IP.
- **IP changed** -- Most home internet connections have dynamic IPs. If your IP changes, update the `realmlist` table and tell your friends the new IP. Consider a dynamic DNS service.

---

## Connection Troubleshooting Checklist

Run through this list in order when someone cannot connect:

1. **Is UniServerZ MySQL running?** Open UniController.exe and check that the MySQL indicator is **green**. If it is red or missing, click "Start MySQL".

2. **Is bnetserver running?** There should be an open console window for bnetserver. It should say it is listening for connections. If it crashed or was never started, launch it first.

3. **Is worldserver running?** There should be an open console window showing **"World initialized"**. If it shows errors or is not open, check the server logs for the cause.

4. **Is Arctium Launcher pointing to the right IP?** For local play: `127.0.0.1`. For remote play: the host's public IP. The setting is in the Arctium Launcher or in Config.wtf (`SET portal "127.0.0.1"`).

5. **Is the client build correct?** Build must be **66263**. Check the login screen bottom-left. See the client builds knowledge article for details.

6. **Are ports forwarded? (remote play only)** Ports 3724, 8085, and 8086 must be forwarded to the server machine. Test with an online port checker.

7. **Is Windows Firewall allowing the servers?** Add exceptions for `bnetserver.exe` and `worldserver.exe`, or temporarily disable the firewall to test.

8. **Does the auth.realmlist table have the correct address?** For local play it should be `127.0.0.1`. For remote play it should be the host's public IP. Check with:
   ```sql
   SELECT id, name, address, port FROM realmlist;
   ```

9. **Is the account created?** If login fails with "wrong password", the account may not exist. Create it in the worldserver console with `bnetaccount create`.

10. **Check server logs.** Look at `Server.log` and `DBErrors.log` in the server's log directory for specific error messages.

## Escalate when
- The player has followed all steps and still cannot connect after checking every item in the troubleshooting list.
- The player needs help with port forwarding on a specific router model.
- The player is trying to host on a VPS or cloud server and needs Linux setup help.
- The player reports that bnetserver or worldserver crashes on startup (likely a database or config issue that needs staff investigation).
