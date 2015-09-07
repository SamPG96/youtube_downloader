# For building youtube_downloader on windows

from distutils.core import setup
import py2exe

# Define where you want youtube_downloader to be built to below
build_dir = 
data_files = [('',['settings.ini',
                   'LICENSE',
                   'README.md']),
              ('sessions',[])]

options = {'py2exe': {
                      'dist_dir': build_dir}}
setup(
      windows=['youtube_downloader.py'],
      data_files=data_files,
      options=options)