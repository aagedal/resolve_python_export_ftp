# DaVinci Resolve python script for render and export to ftp
DaVinci Resolve script to render and upload file to an FTP-server. Intended to be run from inside Resolve GUI.
Once installed it should be possible to run it from the menu-bar: Workspace -> Scripts

### Shorthand of what this does:
1. It gets info about the current project.
2. Finds the active timeline, then renders that timeline in the specified format: current version is in XDDCAM MPEG 2, but thats easy to change.
3. Once the file is done rendering the script will upload to the specified FTP-server using a password and username. Both encoded as base64.
4. Upload progress can be tracked if you open the DaVinci Resolve console: Workspace -> Console.

## Install location for the Python Script:

### Mac App Store version:
~/Library/Containers/com.blackmagic-design.DaVinciResolveAppStore/Data/Library/Application\ Support/Fusion/Scripts/Deliver/

### Blackmagic installer version:
~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Deliver/
