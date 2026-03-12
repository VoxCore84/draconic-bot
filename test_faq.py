"""Test suite for FAQ pattern matching — run with: python test_faq.py"""
import json, re

with open('data/faq_responses.json', 'r', encoding='utf-8') as f:
    entries = json.load(f)
for entry in entries:
    entry['_compiled'] = re.compile(entry['pattern'], re.IGNORECASE)

def match(text):
    if len(text) < 8:
        return 'BLOCKED'
    for entry in entries:
        if entry['_compiled'].search(text):
            return entry['id']
    return None

tests = [
    # === Core regression (37) ===
    ('auth', 'BLOCKED'), ('auth server', 'build_mismatch'),
    ('the auth problem', 'build_mismatch'), ('auth issue', 'build_mismatch'),
    ('auth error', 'build_mismatch'), ('cant connect to the server', 'cant_connect'),
    ('connection refused error', 'cant_connect'), ('keeps loading forever', 'cant_connect'),
    ('wrong build version', 'build_mismatch'), ('Missing auth seed', 'build_mismatch'),
    ('auth table needs updating', 'build_mismatch'), ('my auth is broken', 'build_mismatch'),
    ('my cpu doesnt support avx2', 'arctium_launcher'), ('DataDir error', 'config_issues'),
    ('the black window just closes', 'server_crash'), ('it crashes at the loading screen', 'server_crash'),
    ('database connection error', 'mysql_setup'), ('my friend wants to join the server', 'create_account'),
    ('my friend cant connect to my server', 'play_with_friends'),
    ('dragonriding not working', 'flying_fix'), ('never done this before need help', 'repack_setup'),
    ('how do i download wow', 'get_client'), ('falling through the ground', 'extractor_issues'),
    ('worldserver.conf error', 'config_issues'), ('mysql wont start', 'mysql_setup'),
    ('how to apply sql updates', 'sql_updates'), ('how do i become admin', 'gm_setup'),
    ('how to create an account', 'create_account'), ('flying not working', 'flying_fix'),
    ('how to setup a private server', 'repack_setup'),
    ('only works on lan my friend cant join', 'play_with_friends'),
    ('access denied for user root', 'mysql_setup'), ('forgot my mysql password', 'mysql_setup'),
    ('no realms to pick', 'cant_connect'), ('realm list is empty', 'cant_connect'),
    ('realm incompatible', 'build_mismatch'),
    ('battle.net updated my wow and now i cant play', 'build_mismatch'),
    # === ChatGPT coverage (40) ===
    ('where do i put the arctium launcher', 'arctium_launcher'),
    ('walk through walls no collision', 'extractor_issues'),
    ('worldserver wont stay open', 'server_crash'),
    ('cant use gm commands', 'gm_setup'), ('mount wont fly stays on the ground', 'flying_fix'),
    ('just downloaded everything and im lost', 'repack_setup'),
    ('walk me through the server setup', 'repack_setup'),
    ('what ip do i send my friend', 'play_with_friends'),
    ('red x next to mysql in uniserverz', 'mysql_setup'),
    ('unknown database world', 'mysql_setup'), ('lost connection to mysql', 'mysql_setup'),
    ('stuck at retrieving realm list', 'cant_connect'),
    ('server is online but i cant connect', 'cant_connect'),
    ('theres no realms', 'cant_connect'),
    ('realm is red and says incompatible', 'build_mismatch'),
    ('small patch yesterday broke my server', 'build_mismatch'),
    ('wow updated itself overnight', 'build_mismatch'),
    ('arctium opens then closes', 'arctium_launcher'),
    ('windows defender deleted arctium', 'arctium_launcher'),
    ('datadir wrong path', 'config_issues'),
    ('i moved my repack folder and now config is broken', 'config_issues'),
    ('mobs pathing through walls', 'extractor_issues'),
    ('how do i know if mmaps finished', 'extractor_issues'),
    ('npcs move weird through terrain', 'extractor_issues'),
    ('closes instantly when i open it', 'server_crash'),
    ('server doesnt stay open', 'server_crash'),
    ('i own the server but have no admin', 'gm_setup'),
    ('dont have an account yet', 'create_account'),
    ('mount just runs on the ground', 'flying_fix'),
    ('fresh install server setup guide', 'repack_setup'),
    ('getting started guide', 'repack_setup'),
    # === Antigravity coverage (60+) ===
    ('my wife cant connect to my server', 'play_with_friends'),
    ('my brother keeps getting disconnected when he joins', 'play_with_friends'),
    ('how to setup multiplayer', 'play_with_friends'),
    ('make my server public for friends', 'play_with_friends'),
    ('my girlfriend cant log in to my realm', 'play_with_friends'),
    ('xampp is giving me a mysql error', 'mysql_setup'),
    ('apache starts but mysql is red', 'mysql_setup'),
    ('data base wont turn on', 'mysql_setup'),
    ('mysql keeps shutting off', 'mysql_setup'),
    ('start mysql button does nothing', 'mysql_setup'),
    ('getting WOW51900319 error code', 'cant_connect'),
    ('it kicks me back to login screen instantly', 'cant_connect'),
    ('stuck on handshaking forever', 'cant_connect'),
    ('you have been disconnected from server', 'cant_connect'),
    ('dc instantly after password', 'cant_connect'),
    ('realm text is showing in red', 'build_mismatch'),
    ('how to downgrade my wow folder', 'build_mismatch'),
    ('bnet stealth updated my game', 'build_mismatch'),
    ('retail or classic which one', 'get_client'),
    ('is there a torrent for the client', 'get_client'),
    ('how many gb is the download', 'get_client'),
    ('do i need to buy wow to play', 'get_client'),
    ('custom launcher crashes instantly', 'arctium_launcher'),
    ('how to launch without bnet', 'arctium_launcher'),
    ('bypass battle.net launcher', 'arctium_launcher'),
    ('patched exe keeps closing', 'arctium_launcher'),
    ('do i click wow.exe or what', 'arctium_launcher'),
    ('cant save the conf file permission denied', 'config_issues'),
    ('i dont have a worldserver.conf file', 'config_issues'),
    ('file extensions are hidden', 'config_issues'),
    ('my worldserver.conf.conf is wrong', 'config_issues'),
    ('notepad says access denied on conf', 'config_issues'),
    ('im swimming in the air', 'extractor_issues'),
    ('spawning in the void and falling', 'extractor_issues'),
    ('no buildings anywhere', 'extractor_issues'),
    ('empty world nothing visible', 'extractor_issues'),
    ('map extractor just flashes and closes', 'extractor_issues'),
    ('how long does mmaps take like 2 hours', 'extractor_issues'),
    ('cmd prompt flashes and vanishes', 'server_crash'),
    ('the exe just flashes on screen', 'server_crash'),
    ('closes without any error message', 'server_crash'),
    ('cant even read the error it closes', 'server_crash'),
    ('cmake cant find openssl on my pc', 'openssl_build'),
    ('light or full openssl which one', 'openssl_build'),
    ('win64openssl installer question', 'openssl_build'),
    ('where to download from slproweb', 'openssl_build'),
    ('what do i do with these .sql files', 'sql_updates'),
    ('drag and drop sql into heidi', 'sql_updates'),
    ('downloaded the sql file now what', 'sql_updates'),
    ('how to spawn items for myself', 'gm_setup'),
    ('turn on god mode on my server', 'gm_setup'),
    ('no such command when i type .add', 'gm_setup'),
    ('how to level myself to max', 'gm_setup'),
    ('is there a website to register', 'create_account'),
    ('whats the default login and password', 'create_account'),
    ('registration page link please', 'create_account'),
    ('do i use my real blizzard account to play', 'create_account'),
    ('pressing space does nothing on my mount', 'flying_fix'),
    ('dragon stuck on the ground wont fly', 'flying_fix'),
    ('why cant i fly in this zone', 'flying_fix'),
    ('dynamic flight is not working', 'flying_fix'),
    ('is there a youtube tutorial', 'repack_setup'),
    ('extracted the repack now what', 'repack_setup'),
    ('totally confused about the setup', 'repack_setup'),
    ('idiots guide to setting up', 'repack_setup'),
    ('the readme makes no sense to me', 'repack_setup'),
    ('what do i do after downloading the zip', 'repack_setup'),
]

passed = 0
failed = 0
for text, expected in tests:
    result = match(text)
    if result == expected:
        passed += 1
    else:
        failed += 1
        print(f'FAIL: "{text}" -> {result} (expected {expected})')

print(f'\n{passed}/{len(tests)} passed, {failed} failed')
print(f'\nPattern sizes:')
for entry in entries:
    print(f'  {entry["id"]}: {len(entry["pattern"])} chars')
