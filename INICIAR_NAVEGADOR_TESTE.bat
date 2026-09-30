@echo off
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\edge_debug_profile" "https://helpdesk-sme.netcenter.com.br/login.php"
