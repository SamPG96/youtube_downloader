from tkinter import Tk
import os
from settings import Settings_Parser
import screens

SETTINGS_FILE = os.getcwd() + "/settings.ini"

class App():
    def __init__(self):
        # start at the 'main_menu' screen
        self.next_window = 'main_menu'
        self.download_list = []
        self.settings = Settings_Parser(SETTINGS_FILE)

    def run(self):
        # the main loop for the program, when the loop breaks the
        # program ends.
        program_finished = False
        while not program_finished:
            if self.next_window == 'main_menu':
                self.run_main_menu()
            elif self.next_window == 'download_input':
                self.run_download_input()
            elif self.next_window == 'download_streams':
                self.run_stream_download(self.download_list)
            elif self.next_window == 'settings':
                self.run_settings_window()
            else:
                # will exit the main loop
                program_finished=True
                
    # all the methods below are responsible for setting up and 
    # configuring individual screens.
    # -------start of individual screen configuration--------
    def run_main_menu(self):
        # Runs main menu
        self.next_window = None
        m_menu = screens.Main_Menu(self.settings)
        m_menu.mainloop()
        self.check_next_window(m_menu)

    def run_download_input(self):
        # Runs the download list input screen
        self.next_window = None
        download_input = screens.Download_Input_Screen(self.settings,
                                                       download_list=self.download_list)
        download_input.mainloop()
        self.check_next_window(download_input)
        # get list of streams to download if the next screen isn't the main menu
        if self.next_window == "main_menu":
            self.download_list = []
        else:
            self.download_list=download_input.get_download_list()

    def run_stream_download(self, download_list):
        # Run download and monitoring screen
        self.next_window = None
        download_stream = screens.Download_Streams(self.settings, download_list=download_list)
        download_stream.mainloop()
        self.check_next_window(download_stream)
        # clear download list if the next window is the main menu
        if self.next_window == "main_menu":
            self.download_list = []

    def run_settings_window(self):
        # Run settings window
        self.next_window = None
        settings = screens.Settings(self.settings)
        settings.mainloop()
        self.check_next_window(settings)
        
    # --------end of individual screen configuration---------

    def check_next_window(self, frame):
        # will get the name of the next screen to run
        if frame.get_next_window():
            self.next_window=frame.get_next_window()
        
program = App()
program.run()



