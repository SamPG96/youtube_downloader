#Youtube Downloader

##Introduction
This program uses a UI to allow a user to quickly and easily download multiple Youtube videos in one session.
In a short few steps the user can trim the video and select the file format they wish the video to be downloaded as. The following file formats are supported:
  - mp3
  - ogg
  - m4a
  - m4v
  - webm
  - mp4
  - flv
  - 3gp
  - avi
  
I created this program because I believe in time that it will become more efficient and easier to use than conventional '_Youtube Downloader_' program 
at '_http://download.cnet.com/YTD-Video-Downloader/3000-2071_4-10647340.html_'.

##Prerequisites
  - Only been tested with '_Python 3.3_' on a Windows 7/10 machine
  - '_ffmpeg_' must be installed and included in the main '_PATH_' variable. To get '_ffmpeg_' download '_http://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20150214-git-ac7fc44-win64-static.7z_'.
     Watch this tutorial for more help '_https://www.youtube.com/watch?v=YlF8kg5U2kc_'.
  - The Pafy Python module must be installed from '_http://np1.github.io/pafy/_', see the following links on how to install and develop with Pafy:
    - https://pypi.python.org/pypi/pafy
    - http://pythonhosted.org//Pafy/#pafy-attributes
    
##Download and install
  1. Pull down the git repository 'https://github.com/sammypg/youtube_downloader.git'
  
##How to use
  - Run the script '_youtube_downloader.py_' in the root repository directory.
  - To change default settings go to '_Settings_' to change the following options:
       - Default location to download the Youtube videos too.
       - Favourite(Default) download file format, this can be changed on a video by video basis.
  - Return to the '_Main Menu_' and select '_Download_'. To add one or more Youtube videos for download do the following:
      - Load the video on Youtube that you want to download.
      - Copy and paste the URL at the top of your web browser into the '_Youtube URL_' box.
      - Select the file format to use, by default it will be what was defined in '_Settings_'. Youtube may not always provide a video for the file format you require, if so in most cases
        the program will download the video in a similar file format and convert it after the download to the requested file format. Note that audio only formats
        such as MP3 will be quicker to download than video and audio combined formats such as MP4.
      - To trim the video check either check boxes under 'Trim start time' or 'Trim end time'.
      - To submit the URL select 'Add' or to clear the input boxes select 'Clear'
  - To remove a video from the download list, select it and press the '_Delete_' button.
  - To edit the options chosen for video download on the download list, select it from the table and press '_Edit_'.
  - The download list or session is auto saved every time a change is made to it(such as a new video to download) in a file named after the date and time the session was started.
    To restore a download list from another session, select '_Session_' on the top menu bar and select '_Load session_'. A window will pop up asking
    you to select a session. Choose a session and press '_Open_'. All the contents from the session should be loaded into the table, this can take time.
  - To clear the download list select '_Session_' and select '_Clear current session_'.
  - To start the download press '_Start_'.
  - A window will appear showing the download progress for each video.
  - If any videos failed to download select '_Error report_' for more information.
  
##Build for Windows
To build '_youtube_downloader_' into an '_.exe_' file for windows do the following(ensure py2exe
package for python is installed):
  1. Open the '_setup.py_' file in '_youtube_downloader_' and check the annotation for more details.
  2. Open CMD as administrator.
  3. Go into the '_youtube_downloader_' directory.
  4. Run the following command:
         _Python setup.py py2exe_
     Or if Python is not in your '_PATH_' then replace '_Python_' with the path to the Python
     executable file, for example '_C:\Python33\python.exe_'
  5. Youtube Downloader should now be built in the directory defined in '_setup.py_'.
NOTE: This process will require the third party module '_Pafy_' to be installed as it needs to take a copy of its libraries when building. The built program can be used on any machine without needing to
install '_Pafy_'. However '_ffmpeg_' will still need to be installed on every machine the built program is used on.

##Ideas for the future
  - Add a '_Help_' option in the menu bar or a button which will provide help for the current window.
  - Implement a more user friendly colour scheme.
  - Add a '_Retry_' button if a stream fails to download.
  - Add a '_Pause_' button to pause the download of a stream.
  - Add option to download a particular stream to a specific local location.
  - Add logging.
  - Make session file names more meaningful, give sessions names?
  - Set an option for a max number of session files in the '_session_' directory. This will involve deleting older sessions.
  - Option to disable auto save of sessions.
  - Option to manually save a session.
  - Make program settings portable.
  
##Known bugs
  - Sometimes deleting items in the download list in bulk doesn't always delete them all.
  - Sometimes Python will randomly crash, could be caused from the threading processes.
  - There can be a long period of time between when the download progress window is closed and the download input window is opened when the '_Cancel_' button is pressed in the download progress window.
  - Occasionally the program will just stop without any errors when the '_Cancel_' button is pressed in the download progress window.
  - The code in some areas could be improved and cleaned up such as:
      - The '_download_' method in the class '_Download_Streams_' in the file '_screens_'.
      - The stream submitting process in the class '_Download_Input_Screen_' in the file '_screens_'.
  - Fix window positing so it is not random every time a window opens.
       