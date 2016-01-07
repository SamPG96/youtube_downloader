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
        while program_finished == False:
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
        self.next_window=None
        tMainMenu = Tk()
        tMainMenu.title("Main Menu")
        tMainMenu.geometry("400x250")
        tMainMenu.resizable(0,0)
        m_menu = screens.Main_Menu(tMainMenu, self.settings)
        m_menu.mainloop()
        self.check_next_window(m_menu)

    def run_download_input(self):
        # Runs the download list input screen
        self.next_window=None
        tDownload_Input = Tk()
        tDownload_Input.title("Download List")
        tDownload_Input.geometry("900x600")
        tDownload_Input.resizable(0,0)
        download_input = screens.Download_Input_Screen(tDownload_Input, self.settings,
                                                       download_list=self.download_list)
        download_input.mainloop()
        self.check_next_window(download_input)
        # get list of streams to download if the next screen isn't the main menu
        if self.next_window == "main_menu":
            self.download_list = []
        else:
            self.download_list=download_input.get_download_list()

    def run_stream_download(self,download_list):
        # Run download and monitoring screen
        self.next_window=None
        tDownload_Streams = Tk()
        tDownload_Streams.title("Download Progress")
        tDownload_Streams.geometry("810x600")
        tDownload_Streams.resizable(0,0)
        download_stream = screens.Download_Streams(tDownload_Streams, self.settings,
                                                   download_list)
        download_stream.mainloop()
        self.check_next_window(download_stream)
        # clear download list if the next window is the main menu
        if self.next_window == "main_menu":
            self.download_list = []

    def run_settings_window(self):
        # Run settings window
        self.next_window=None
        tSettings = Tk()
        tSettings.title("Settings")
        tSettings.geometry("400x150")
        tSettings.resizable(0,0)
        settings = screens.Settings(tSettings, self.settings)
        settings.mainloop()
        self.check_next_window(settings)
        
    # --------end of individual screen configuration---------

    def check_next_window(self, frame):
        # will get the name of the next screen to run
        if frame.get_next_window():
            self.next_window=frame.get_next_window()
        
program = App()
program.run()



