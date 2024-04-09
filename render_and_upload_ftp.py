# If you have the Mac App Store version of DaVinci Resolve, place ~/Library/Containers/com.blackmagic-design.DaVinciResolveAppStore/Data/Library/Application\ Support/Fusion/Scripts/Deliver/

print("Script starting: XDCAM render export + FTP upload.")

import sys

#Setup ResolveAPI 
projectManager = resolve.GetProjectManager()
currentProject = projectManager.GetCurrentProject()
currentTimeline = currentProject.GetCurrentTimeline() 


# Get user directory
import getpass as gt
currentUser = gt.getuser()
home = "/Users/" + currentUser
targetDirectory = home + "/Movies/ResolveExport/"

#Setup render format and codec
renderFormats = currentProject.GetRenderFormats()
print(renderFormats)
codecFormats = currentProject.GetRenderCodecs("mxf_op1a")
print(codecFormats)
format = "mxf_op1a"
codec = "XDMPEG2"

currentProject.SetCurrentRenderFormatAndCodec(format, codec)


# Setup render export parameters
exportClipName = currentTimeline.GetName() + "_XDCAM"
TimecodeIn = currentTimeline.GetStartFrame()
TimecodeOut = currentTimeline.GetEndFrame()

settings = {
        "CustomName": exportClipName,
        "TargetDir": targetDirectory,
        "MarkIn": TimecodeIn,
        "MarkOut": TimecodeOut,
        "ExportVideo": True, 
        "ExportAudio": True,
        "FormatWidth": 1920,
        "FormatHeught": 1080,
        "Audio Codec": "lpcm",
        "AudioBitDepth": 16,
        "ColorSpaceTag": "Rec.709",
        "GammaTag": "Rec.709",
        # // The settings below in the settings array doesn't work. Apparently the Resolve Python API doesn't support setting interlaced options.
        # // Render settings always default to progressive. If you need interlaced you can load a preset instead using a script, instead of scripting the settings.
        #"FieldRendering": True,
        #"FieldOrder": "TopFieldFirst",
        #"FrameRate": 50,
        #"PixelAspectRatio": "square",
        #"VideoQuality": 0, # 0 is automatic, other values treated as bitrate
    }
currentProject.SetRenderSettings(settings)

# Add current timeline to render cue
currentProject.AddRenderJob()

# Get RenderJob ID of the last item in the render cue. This should be the same render job as in the previous command.
jobs = currentProject.GetRenderJobList()
lastJob = jobs[-1]
lastJobID = lastJob.get("JobId")
print(lastJobID)

# Start Rendering
currentProject.StartRendering(lastJobID)

# Setup tracking of render progress.
import time
wasCancelled = False
renderingComplete = False
percentage = 0

# Loop to track render progress. If job is cancelled, the script is 
while percentage < 100:
    jobStatus = currentProject.GetRenderJobStatus(lastJobID)
    print(currentProject.GetRenderJobStatus(lastJobID))
    
    if jobStatus.get("JobStatus") == "Cancelled":
        wasCancelled = True
        break

    percentage = jobStatus.get("CompletionPercentage")
    print("Rendering is " + str(percentage) + "%" + " complete.")
    time.sleep(2) #This should reduce performance cost. Also the API doesn't seem update as often as the GUI, so its just a waste of recsources to do it as fast as possible.
    

# Confirmation of Render completion
print(currentProject.GetRenderJobStatus(lastJobID))
if jobStatus.get("JobStatus") == "Completed":
        renderingComplete = True
        print("Rendering Complete: " + renderingComplete)


# After Rendering. Exits script if rendering was cancelled.
if wasCancelled:
    print("Rendering job was cancelled!")
    sys.exit()

elif renderingComplete: 
    print("Rendering Complete!!")


#Check Rendered file
fileExtension = ".mxf"
exportedFilePath = targetDirectory + exportClipName + fileExtension
exportedFileName = exportClipName + fileExtension
print(exportedFilePath)

#Check if exported file exists before trying to upload. Exit script if file doesn't exist
import os
exportfileExists = os.path.isfile(exportedFilePath)
print(exportfileExists)
            
if not exportfileExists:
    print("File does not exist")
    sys.exit()

print("Ready for FTP Upload!")


# Setup for FTP Upload
import base64
import ftplib

# FTP Session Data as Base64 - to avoid storting passwords as clear text. This still isn't quite safe, but it is slightly better than storing login info as clear text.
FTP_U = " insert your username encoded as base 64 "
FTP_P = " insert your password encoded as base 64 "
FTP_S = " insert your ftp-server address / IP encoded as base 64 here "

#Decode obfuscated data
def dec(b_64) :
    b64_bytes = b_64.encode("ascii")
    bytes_b = base64.b64decode(b64_bytes)
    return bytes_b.decode("ascii")
p_string = dec(FTP_P)
u_string = dec(FTP_U)
s_string = dec(FTP_S)

# Create session
session = ftplib.FTP(s_string, u_string, p_string)

#List contents on server before upload
contents = session.retrlines('LIST')
print(contents)


#Get file size
sizeWritten = 0
totalSize = os.path.getsize(exportedFilePath)
print('Total file size : ' + str(round(totalSize / 1024 / 1024 ,1)) + ' Mb')



# Class to calculate progress
class FtpUploadTracker:
    sizeWritten = 0
    totalSize = 0
    lastShownPercent = 0
    
    def __init__(self, totalSize):
        self.totalSize = totalSize
    
    def handle(self, block):
        self.sizeWritten += 1024
        percentComplete = round((self.sizeWritten / self.totalSize) * 100)
        
        if (self.lastShownPercent != percentComplete):
            self.lastShownPercent = percentComplete
            print("File upload is " + str(percentComplete) + "% percent complete.")


# Instanciate FTP upload progress tracker
uploadTracker = FtpUploadTracker(int(totalSize))

print("File Name to be uploaded is called: " + exportedFileName)
print("File Path to be uploaded is: " + exportedFilePath)

# Start upload File to FTP Server
with open(exportedFilePath, "rb") as file:
    session.storbinary(f"STOR {exportedFileName}", file, 1024, uploadTracker.handle)

print("Upload complete")
session.quit()
sys.exit()
