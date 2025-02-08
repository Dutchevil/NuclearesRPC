# NuclearesRPC, an RPC client for Nucleares
Welcome to the repository for the Python-based Discord Rich Presence Client for Nucleares

# Installation (Standalone)
To run NuclearesRPC, simply unzip a Release zip file and run the client

# Installation (Steam)
To install NuclearesRPC for Steam
- unzip a Release zip file, move the contents to the root of your Nucleares install
(typically "C:\Program Files (x86)\Steam\steamapps\common\Nuclear Last Darkness")
- Shift+Right Click the nuclearesrpc.exe file and select Copy As Path
- In Steam, select Nucleares, then Properties
- Paste into the Launch Options, and add %command%
- It should look like `"C:\Program Files (x86)\Steam\steamapps\common\Nuclear Last Darkness\nuclearesrpc.exe" %command%`
- Once in-game, in the tablet, go to Status, and press Start Webserver. The client will start automatically (THIS MUST BE DONE EVERY TIME THE GAME RESTARTS!)

# Reporting a bug
When reporting a bug with the client, please be sure to reproduce the bug while running the RPC in debug mode so a debug log is generated.
## Through Steam
To debug through steam, add `-d` after the exe path and before `%command%`
For Example: `"C:\Program Files (x86)\Steam\steamapps\common\Nuclear Last Darkness\nuclearesrpc.exe" -d %command%`
## Through CMD/PowerShell/Python
Simply add --debug or -d to the launch args
