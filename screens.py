import threading
import tkinter as tk
from tkinter import (filedialog, Frame, Button, Label, Spinbox, Entry, Menu, 
                     Checkbutton, Listbox, Scrollbar, messagebox, Tk, 
                     HORIZONTAL, ACTIVE, NORMAL, DISABLED, GROOVE, END, TclError)
import time, datetime
import json
import os
from tools import stream_gen
from convert import Convert
from settings import Settings_Parser

settings_file = os.getcwd()+"/settings.ini"

class Screen(object):
    """ Inherited by all screen objects and provides common solutions """
    def __init__(self):
        self.next_window=None
        # create widgets for screen
        self.create_widgets()
        
    def get_next_window(self):
        # get the next screen to be loaded
        return self.next_window
    
    def kill_window(self):
        # kill the screen
        self.master.destroy()

class Main_Menu(Frame, Screen):
    """ The first and youtube_downloader menu that appears when the program starts. """
    def __init__(self,master):
        super(Main_Menu, self).__init__(master)
        Screen.__init__(self)

    def create_widgets(self):
        Button(height=1, width=8, 
               font=('times',35,'bold'), text='Download', 
               command=self.download_pressed).place(x=80, y=40)
        Button(height=1, width=8, 
               font=('times',25), text='Settings', 
               command=self.settings_pressed).place(x=120, y=140)

    def download_pressed(self):
        self.kill_window()
        self.next_window = 'download_input'

    def settings_pressed(self):
        self.kill_window()
        self.next_window = 'settings'

class Settings(Frame, Screen):
    """ Allows user to change program settings via a GUI """
    def __init__(self,master):
        super(Settings, self).__init__(master)
        self.s_parser = Settings_Parser(settings_file)
        self.settings_conf = self.s_parser.get_settings()
        self.download_directory = tk.StringVar()
        self.default_format = tk.StringVar()
        Screen.__init__(self)

    def create_widgets(self):
        # Change program defaults section
        Label(text='Defaults', font=('times',16,'bold')).place(x=10, y=10)
        # download folder location
        Label(text='Download Folder: ', font=('times',10)).place(x=10, y=40)
        self.download_entry_widget = Entry(font=('times',10),
                                           textvariable=self.download_directory,
                                           relief=GROOVE,
                                           width=33)
        self.download_entry_widget.place(x=125, y=40)
        directory = self.settings_conf["LOCATIONS"]["download"]
        self.download_entry_widget.insert(0, directory)
        Button(height=1,font=('times',10), text='Browse',
               command=self.browse_download_folder_pressed).place(x=335, y=37)
        # choose default file format
        Label(text='Download format: ',font=('times',10)).place(x=10, y=65)
        format_options = self.get_format_options()
        self.format_input_widget=Spinbox(textvariable=self.default_format,
                                         width=6,
                                         wrap=True,
                                         values=[x["format"] for x in format_options],
                                         font=('times', 10))
        self.default_format.set(self.settings_conf["FORMAT"]["default_format"])
        self.format_input_widget.place(x=125, y=65)
        Button(font=('times',15,'bold'), text='Back',
               command=self.back_pressed).place(x=10, y=100)
        Button(font=('times',15,'bold'), text='Save',
               command=self.save_pressed).place(x=330, y=100)

    def browse_download_folder_pressed(self):
        # Add path from selected directory to the entry box
        directory = filedialog.askdirectory(initialdir=self.download_directory.get())
        if directory:
            self.download_entry_widget.delete(0, END)
            self.download_entry_widget.insert(0, directory)

    def get_format_options(self):
        # Return list of supported file formats from configuration file
        format_options = []
        audio_formats = self.settings_conf["FORMAT"]["supported_audio_only_formats"].split(",")
        for audio_format in audio_formats:
            format_options.append({"type":"a", "format":audio_format})
        video_formats = self.settings_conf["FORMAT"]["supported_video_only_formats"].split(",")
        for video_format in video_formats:
            format_options.append({"type":"v", "format":video_format})
        audio_video_formats = self.settings_conf["FORMAT"]["supported_audio_and_video_formats"].split(",")
        for audio_video_format in audio_video_formats:
            format_options.append({"type":"av", "format":audio_video_format})
        return format_options

    def save_pressed(self):
        # Save new settings to configuration file
        self.s_parser.set_option("LOCATIONS", "download", self.download_directory.get())
        self.s_parser.set_option("FORMAT", "default_format", self.default_format.get())
        self.kill_window()
        self.next_window = 'main_menu'
        return None

    def back_pressed(self):
        # Return to youtube_downloader menu
        self.kill_window()
        self.next_window = 'main_menu'
        return None

class Download_Input_Screen(Frame, Screen):
    """ Creates an input screen for streams to download """
    def __init__(self,master,download_list=[]):
        super(Download_Input_Screen, self).__init__(master)
        self.s_parser = Settings_Parser(settings_file)
        self.settings_conf = self.s_parser.get_settings()
        # Initialise tkinter variables
        self.url_input = tk.StringVar()
        self.format_input = tk.StringVar()
        self.start_time_hour_input = tk.StringVar()
        self.start_time_minute_input = tk.StringVar()
        self.start_time_second_input = tk.StringVar()
        self.end_time_hour_input = tk.StringVar()
        self.end_time_minute_input = tk.StringVar()
        self.end_time_second_input = tk.StringVar()
        self.start_time_checkbox_value = tk.BooleanVar()
        self.end_time_checkbox_value = tk.BooleanVar()

        # Get file format options
        # TODO: Parsing the settings file for file format options is already done in the same way in the 
        #       Settings screen. To make the code less repetitive maybe make the settings parser portable?
        self.format_options = []
        audio_formats = self.settings_conf["FORMAT"]["supported_audio_only_formats"].split(",")
        for audio_format in audio_formats:
            self.format_options.append({"type":"a", "format":audio_format})
        video_formats = self.settings_conf["FORMAT"]["supported_video_only_formats"].split(",")
        for video_format in video_formats:
            self.format_options.append({"type":"v", "format":video_format})
        audio_video_formats = self.settings_conf["FORMAT"]["supported_audio_and_video_formats"].split(",")
        for audio_video_format in audio_video_formats:
            self.format_options.append({"type":"av", "format":audio_video_format})
        self.default_format = self.settings_conf["FORMAT"]["default_format"]
        # Initialise variables
        self.streams_to_download = []
        self.session_meta = []
        self.to_download = download_list
        self.list_boxes = []
        self.main_button_widgets = []
        self.session_timestamp=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
        Screen.__init__(self)
        self.add_download_list_to_table()

    def create_widgets(self):
        # creates a menu bar at the top of the window to display useful tools
        menu_bar = Menu()
        session_menu = Menu(menu_bar)
        session_menu.add_command(label="Load session", command=self.load_session_pressed)
        session_menu.add_command(label="Clear current session", command=self.clear_session)
        menu_bar.add_cascade(label="Session", menu=session_menu)
        self.master.config(menu=menu_bar)
        
        # create a label to show what the program is currently doing
        Label(text='Status: ',font=('times',10,'bold')).place(x=10,y=5)
        self.set_status("Ok")
        
        self.create_entry_boxes()
        self.create_download_list_table()
        
    def create_entry_boxes(self):
        # create entry widgets
        self.url_input_widget=Entry(textvariable=self.url_input, width=45, font=('times', 11))
        self.url_input_widget.place(x=10, y=50)
        self.format_input_widget=Spinbox(textvariable=self.format_input, width=6,
                                         wrap=True, values=[x["format"] for x in self.format_options], 
                                         font=(26))
        self.format_input_widget.place(x=335, y=50)
        self.start_time_checkbox_widget = Checkbutton(onvalue=True, offvalue=False, 
                                                      command=self.start_time_checkbox_pressed,
                                                      variable=self.start_time_checkbox_value)
        self.start_time_checkbox_widget.place(x=408, y=50)
        self.start_time_hour_widget = Spinbox(textvariable=self.start_time_hour_input,
                                              from_=00, to=23,
                                              format="%02.0f",
                                              width=3,
                                              font=(26))
        self.start_time_hour_widget.place(x=428, y=50)
        Label(text=':',font=('times',10,'bold')).place(x=471, y=50)
        self.start_time_minute_widget = Spinbox(textvariable=self.start_time_minute_input,
                                                from_=00, to=59,
                                                format="%02.0f",
                                                width=3,
                                                font=(26))
        self.start_time_minute_widget.place(x=482, y=50)
        Label(text=':',font=('times',10,'bold')).place(x=525, y=50)
        self.start_time_second_widget = Spinbox(textvariable=self.start_time_second_input,
                                                from_=00, to=59,
                                                format="%02.0f",
                                                width=3,
                                                font=(26))
        self.start_time_second_widget.place(x=535, y=50)
        self.end_time_checkbox_widget = Checkbutton(onvalue=True, offvalue=False, 
                                                    command=self.end_time_checkbox_pressed,
                                                    variable=self.end_time_checkbox_value)
        self.end_time_checkbox_widget.place(x=580, y=50)
        self.end_time_hour_widget = Spinbox(textvariable=self.end_time_hour_input,
                                              from_=00, to=23,
                                              format="%02.0f",
                                              width=3,
                                              font=(26))
        self.end_time_hour_widget.place(x=600, y=50)
        Label(text=':',font=('times',10,'bold')).place(x=643, y=50)
        self.end_time_minute_widget = Spinbox(textvariable=self.end_time_minute_input,
                                                from_=00, to=59,
                                                format="%02.0f",
                                                width=3,
                                                font=(26))
        self.end_time_minute_widget.place(x=653, y=50)
        Label(text=':',font=('times',10,'bold')).place(x=696, y=50)
        self.end_time_second_widget = Spinbox(textvariable=self.end_time_second_input,
                                                from_=00, to=59,
                                                format="%02.0f",
                                                width=3,
                                                font=(26))
        self.end_time_second_widget.place(x=706, y=50)
        # add entry box labels
        # TODO: Use a cleaner way of creating these headings
        Label(text='\t\t Youtube URL\t\t                File format       Trim start time (HH:MM:SS)      Trim end time (HH:MM:SS)',
              font=('times',10,'bold')).place(x=10,y=28)
        self.reset_control_widgets()
        self.add_button = Button(width= 5, font=('times',15,'bold'), text='Add', bd=4, command=self.add_pressed)
        self.add_button.place(x=815, y=38)
        self.clear_button = Button(width= 5, font=('times',12), text='Clear', command=self.reset_control_widgets)
        self.clear_button.place(x=755, y=43)
        
    def create_download_list_table(self):
        # Create a table to show streams to be downloaded
        self.scrollbar_widget_y=Scrollbar(command=self.track_scrollbar_y)
        self.scrollbar_widget_y.place(x=875, y=120, height=370)
        self.scrollbar_widget_x_name=Scrollbar(orient=HORIZONTAL, command=self.track_scrollbar_x_name)
        self.scrollbar_widget_x_name.place(x=10, y=490, width=284)
        self.scrollbar_widget_x_url=Scrollbar(orient=HORIZONTAL, command=self.track_scrollbar_x_url)
        self.scrollbar_widget_x_url.place(x=294, y=490, width=275)

        Label(borderwidth=1, relief=GROOVE, text='Name', font=('times',10,'bold'), width=40).place(x=9, y=102)
        self.name_list_widget=Listbox(highlightthickness=0,
                                    selectmode="multiple",
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    xscrollcommand=self.scrollbar_widget_x_name.set,
                                    exportselection=False,
                                    width=47,
                                    height=23)
        self.name_list_widget.place(x=9, y=120)
        self.name_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE, text='URL',font=('times',10,'bold'), width=39).place(x=293, y=102)
        self.url_list_widget = Listbox(highlightthickness=0,
                                    selectmode="multiple",
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    xscrollcommand=self.scrollbar_widget_x_url.set,
                                    exportselection=False,
                                    width=46,
                                    height=23)
        self.url_list_widget.place(x=293,y=120)
        self.url_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE,text='Format',font=('times',10,'bold'),width=11).place(x=568, y=102)
        self.format_list_widget = Listbox(highlightthickness=0,
                                    selectmode="multiple",
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    exportselection=False,
                                    width=12,
                                    height=23)
        self.format_list_widget.place(x=568, y=120)
        self.format_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE, text='Convert', font=('times',10,'bold'), width=9).place(x=642, y=102)
        self.con_req_list_widget = Listbox(highlightthickness=0,
                                    selectmode="multiple",
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    exportselection=False,
                                    width=11,
                                    height=23)
        self.con_req_list_widget.place(x=642, y=120)
        self.con_req_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE, text='Start', font=('times',10,'bold'), width=8).place(x=705, y=102)
        self.start_list_widget = Listbox(highlightthickness=0,
                                    selectmode="multiple",
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    exportselection=False,
                                    width=9,
                                    height=23)
        self.start_list_widget.place(x=705, y=120)
        self.start_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE, text='End', font=('times',10,'bold'), width=8).place(x=759, y=102)
        self.end_list_widget = Listbox(highlightthickness=0,
                                    selectmode="multiple",
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    exportselection=False,
                                    width=9,
                                    height=23)
        self.end_list_widget.place(x=759, y=120)
        self.end_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE, text='Duration', font=('times',10,'bold'), width=9).place(x=813, y=102)
        self.duration_list_widget = Listbox(highlightthickness=0,
                                    selectmode="multiple",
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    exportselection=False,
                                    width=10,
                                    height=23)
        self.duration_list_widget.place(x=813, y=120)
        self.duration_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE, width=2).place(x=874, y=102)

        self.list_boxes.extend((self.name_list_widget,
                                self.url_list_widget,
                                self.format_list_widget,
                                self.con_req_list_widget,
                                self.start_list_widget,
                                self.end_list_widget,
                                self.duration_list_widget))
        for tList in self.list_boxes:
            tList.bind('<<ListboxSelect>>', self.list_box_selection)
        
        self.delete_widget=Button(width= 5, font=('times',15), text='Delete',state=DISABLED, command=self.delete_from_list)
        self.delete_widget.place(x=580, y=495)
        self.edit_widget=Button(width= 5, font=('times',15), text='Edit',state=DISABLED, command=self.edit_pressed)
        self.edit_widget.place(x=655, y=495)
        self.start_button = Button(width= 5, font=('times',21,'bold'), text='Start', command=self.start_pressed)
        self.start_button.place(x=796, y=538)
        self.back_button = Button(width= 5, font=('times',21,'bold'), text='Back', command=self.back_pressed)
        self.back_button.place(x=7, y=538)
        self.main_button_widgets = [self.back_button,
                                   self.start_button,
                                   self.clear_button,
                                   self.add_button]
        
    def add_download_list_to_table(self):
        # Add the contents of the download list to the table
        if not self.to_download:
            return
        temp_download = self.to_download
        self.to_download = []
        for stream in temp_download:
            self.add_to_GUI_list([self.submit_stream(stream)[1]])

    def track_scrollbar_y(self,*args):
        # Move up and down in all list boxes via a scroll bar
        for tList in self.list_boxes:
            tList.yview(*args)

    def track_scrollbar_x_name(self,*args):
        # Move side to side in the name list box via a scroll bar
        self.name_list_widget.xview(*args)

    def track_scrollbar_x_url(self,*args):
        # Move side to side in the URL list box via a scroll bar
        self.url_list_widget.xview(*args)

    def on_mouse_wheel(self, event):
        # Control scrolling off all list boxes via the mouse wheel 
        for tList in self.list_boxes:
            tList.yview("scroll", event.delta,"units")
        return "break"

    def disable_all_control_widgets(self):
        # Disable control buttons
        for button in self.main_button_widgets:
            button.configure(state=DISABLED)
        
    def reset_control_widgets(self):
        # Reset the following widgets to the windows default state
        self.url_input_widget.delete(0, END)
        self.format_input.set(self.default_format)
        self.start_time_checkbox_widget.deselect()
        self.end_time_checkbox_widget.deselect()
        self.reset_start_time_widgets()
        self.reset_end_time_widgets()
        for button in self.main_button_widgets:
            button.configure(state=NORMAL)
            
    # TODO: Combine the following methods to remove duplication of code
    def reset_start_time_widgets(self):
        # Clear and disable start time widgets
        self.start_time_hour_input.set("00")
        self.start_time_hour_widget.configure(state=DISABLED)
        self.start_time_minute_input.set("00")
        self.start_time_minute_widget.configure(state=DISABLED)
        self.start_time_second_input.set("00")
        self.start_time_second_widget.configure(state=DISABLED)

    def reset_end_time_widgets(self):
        # Clear and disable end time widgets
        self.end_time_hour_input.set("00")
        self.end_time_hour_widget.configure(state=DISABLED)
        self.end_time_minute_input.set("00")
        self.end_time_minute_widget.configure(state=DISABLED)
        self.end_time_second_input.set("00")
        self.end_time_second_widget.configure(state=DISABLED)

    # TODO: Combine the following methods to remove duplication of code
    def start_time_checkbox_pressed(self):
        # Runs every time the start time check box is pressed
        if (self.start_time_checkbox_value.get()):
            # Enable start time widgets
            self.start_time_hour_widget.configure(state=NORMAL)
            self.start_time_minute_widget.configure(state=NORMAL)
            self.start_time_second_widget.configure(state=NORMAL)
        else:
            self.reset_start_time_widgets()
            
    def end_time_checkbox_pressed(self):
        # Runs every time the end time check box is pressed
        if (self.end_time_checkbox_value.get()):
            # Enable end time widgets
            self.end_time_hour_widget.configure(state=NORMAL)
            self.end_time_minute_widget.configure(state=NORMAL)
            self.end_time_second_widget.configure(state=NORMAL)
        else:
            self.reset_end_time_widgets()

    def list_box_selection(self, event):
        # Highlight/unhighlight the cell in every column in the row selected or not selected
        self.selected_lines = event.widget.curselection()
        if not event.widget.curselection():
            for tList in self.list_boxes:
                tList.selection_clear(first=0, last=END)
            self.delete_widget.configure(state=DISABLED)
            self.edit_widget.configure(state=DISABLED)
            return
        for tList in self.list_boxes:
            tList.selection_clear(first=0, last=END)
            for line in self.selected_lines:
                tList.selection_set(first=line)
        if len(self.selected_lines) == 1:
            self.edit_widget.configure(state=ACTIVE)
        else:
            self.edit_widget.configure(state=DISABLED)
        self.delete_widget.configure(state=ACTIVE)

    def delete_from_list(self):
        # Delete entire row(s) of a table and remove from download list
        ordered_lines = sorted(self.selected_lines, reverse=True)
        for line in ordered_lines:
            for tList in self.list_boxes:
                tList.delete(first=line)
            del self.to_download[int(line)]
            del self.session_meta[int(line)]
        self.delete_widget.configure(state=DISABLED)
        self.edit_widget.configure(state=DISABLED)
        self.update_session_file()

    def clear_session(self):
        # Empty table and download list
        self.to_download = []
        self.session_meta = []
        for tList in self.list_boxes:
            tList.delete(first=0, last=END)
        self.reset_control_widgets()
        self.update_session_file()
        
        
    def edit_pressed(self):
        # Add all input data for the selected stream back into the entry boxes
        # and remove from the table.
        self.reset_control_widgets()
        stream=self.to_download[int(self.selected_lines[0])]
        self.url_input_widget.insert(0,stream["url"])
        self.format_input.set(stream["chosen_format"])
        if stream["start_time"] != "00:00:00":
            start_time = stream["start_time"].split(":")
            self.start_time_checkbox_widget.select()
            self.start_time_hour_widget.configure(state=NORMAL)
            self.start_time_hour_input.set(start_time[0])
            self.start_time_minute_widget.configure(state=NORMAL)
            self.start_time_minute_input.set(start_time[1])
            self.start_time_second_widget.configure(state=NORMAL)
            self.start_time_second_input.set(start_time[2])
        if stream["end_time"] != stream["duration"]:
            end_time = stream["end_time"].split(":")
            self.end_time_checkbox_widget.select()
            self.end_time_hour_widget.configure(state=NORMAL)
            self.end_time_hour_input.set(end_time[0])
            self.end_time_minute_widget.configure(state=NORMAL)
            self.end_time_minute_input.set(end_time[1])
            self.end_time_second_widget.configure(state=NORMAL)
            self.end_time_second_input.set(end_time[2])  
        self.delete_from_list()

    def set_status(self, message):
        # Initialise status label
        self.status_label = Label(text=message, font=('times', 10))
        self.status_label.place(x=60, y=5)        

    def change_status(self, message, colour="black"):
        # Change status message and colour
        self.status_label.config(text=message, fg=colour)

    def update_session_file(self):
        # Update the json file with the current download list
        with open((os.getcwd()+"/sessions/"+self.session_timestamp+".json"),"w") as session_file:
            json.dump(self.session_meta, session_file, indent=4, sort_keys=True)

    def load_session_pressed(self):
        # Reads a json session file and creates a thread to add it to the download table and list
        session_file_location = filedialog.askopenfilename(initialdir="sessions")
        if not session_file_location:
            return
        self.change_status("Reading session file \'%s\'..." %session_file_location, colour="red")
        with open(session_file_location,'r') as session_file:
            session_contents = json.load(session_file)
        self.disable_all_control_widgets()
        self.session_contents = session_contents
        self.add_session_thread=threading.Thread(target=self.add_session_file_streams, args=(session_contents,))
        self.add_session_thread.daemon = True
        try:
            self.add_session_thread.start()
        except TclError:
            pass

    def add_session_file_streams(self, session_contents):
        # Add a session json to the download list and table
        total_sessions = len(session_contents)
        GUI_meta = []
        failed_urls = []
        for session_count, stream in enumerate(session_contents):
            self.change_status("Loading session %s of %s... " %(session_count+1, total_sessions), colour="red")
            success, output = self.submit_stream(stream)
            if success:
                GUI_meta.append(output)
            else:
                failed_urls.append(stream["url"])
        if not failed_urls:
            self.change_status("Ok")
        else:
            self.change_status("Failed to add: %s" %(", ".join(failed_urls)), colour="red")
        self.after(0, self.add_to_GUI_list, GUI_meta)

    def add_input_url(self, input_meta):
        # Get a stream object with a URL and some metadata
        success, output = self.submit_stream(input_meta)
        if success:
            self.add_to_GUI_list([output])
            self.change_status("Ok")
        else:
            self.change_status(output, colour="red")
            self.reset_control_widgets()            

    def add_pressed(self):
        # Collect input data from entry fields and create a thread to check and add the URL
        input_meta = {
                    "url":self.url_input.get(),
                    "chosen_format":self.format_input.get(),
                    "start_time":"00:00:00",
                    }
        if (self.start_time_checkbox_value.get()):
            input_meta["start_time"]=(self.start_time_hour_input.get() + ":" +
                                      self.start_time_minute_input.get() + ":" +
                                      self.start_time_second_input.get())
        if (self.end_time_checkbox_value.get()):
            input_meta["end_time"]=(self.end_time_hour_input.get() + ":" +
                                      self.end_time_minute_input.get() + ":" +
                                      self.end_time_second_input.get())
        self.change_status("Checking URL", colour="red")
        self.disable_all_control_widgets()        
        self.add_url_thread=threading.Thread(target=self.add_input_url, args=(input_meta,))
        self.add_url_thread.daemon = True
        try:
            self.add_url_thread.start()
        except TclError:
            pass    

    def submit_stream(self, stream_meta):
        # Creates a stream object and builds some meta data for it
        # A boolean is returned from this method as well as the meta_data to show if the 
        # stream and its meta data was added successfully
        def replace_special_characters(title):
            # replaces special characters in title to an alternative to avoid invalid argument error
            # If any of the following characters are in the title, they will be removed
            replace_with_empty = ['~', '#', '%', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '+', '|', '"']
            # special exceptions/replacements
            title = title.replace('"', '\'')
            title = title.replace('&', 'and')
            for character in replace_with_empty:
                title = title.replace(character, '')
            return title
        
        for f in self.format_options:
            if f["format"] == stream_meta["chosen_format"]:
                format_type = f["type"]
                stream_meta["format_type"] = format_type
        if not format_type:
            messagebox.showerror(title='Error', width =50, message=("File format %s is not supported" %stream_meta["chosen_format"]))
        stream = stream_gen(stream_meta)
        if stream.error_messages:
            return False, stream.error_messages
        stream_meta["stream"] = stream.get_stream()
        try:
            stream_meta["duration"] = stream.get_duration()
        except Exception as e:
            raise Exception(e)
        stream_title = stream_meta["stream"].title
        stream_title = replace_special_characters(stream_title)
        stream_meta["stream_title"] = stream_title
        stream_meta["save_location"] = os.path.join(self.settings_conf["LOCATIONS"]["download"],stream_title)
        while os.path.isfile(stream_meta["save_location"]+"."+stream_meta["chosen_format"]):
            stream_meta["save_location"] += " - Copy"
        if stream.sub_format:
            stream_meta["sub_format"] = stream.sub_format
        if "end_time" not in stream_meta:
            stream_meta["end_time"] = stream.get_duration()
        if stream.sub_format:
            stream_meta["convert_required"] = True
        else:
            stream_meta["convert_required"] = False
        self.to_download.append(stream_meta)
        self.session_meta.append({"url":stream_meta["url"],
                                  "chosen_format":stream_meta["chosen_format"],
                                  "start_time":stream_meta["start_time"],
                                  "end_time":stream_meta["end_time"]})
        self.update_session_file()
        return True, stream_meta

    def add_to_GUI_list(self, GUI_meta):
        # Adds stream meta to the table GUI
        for meta in GUI_meta:
            self.name_list_widget.insert(END,meta["stream_title"])
            self.url_list_widget.insert(END,meta["url"])
            self.format_list_widget.insert(END,meta["chosen_format"])
            if meta["convert_required"]:
                self.con_req_list_widget.insert(END,"Yes")
            else:
                self.con_req_list_widget.insert(END,"No")
            self.start_list_widget.insert(END, meta["start_time"])
            self.end_list_widget.insert(END, meta["end_time"])
            self.duration_list_widget.insert(END, meta["duration"])        
        self.reset_control_widgets()

    def start_pressed(self):
        # Go to the download screen and return the download list
        self.kill_window()
        self.next_window = 'download_streams'
        return self.to_download

    def back_pressed(self):
        # Return to youtube_downloader menu
        self.kill_window()
        self.next_window = 'main_menu'
        return None

    def get_download_list(self):
        # Return the download list
        return self.to_download
    
            
class Download_Streams(Frame, Screen):
    """ Download and monitors all streams from the download list"""
    def __init__(self,master,download_list):
        super(Download_Streams, self).__init__(master)
        self.list_boxes = []
        self.download_report = []
        self.error_list = []
        self.to_download = download_list
        self.count = None
        self.stop_download = False
        Screen.__init__(self)

    def create_widgets(self):
        # Creates the table to see the download information about all the streams
        self.scrollbar_widget_y=Scrollbar(command=self.track_scrollbar_y)
        self.scrollbar_widget_y.place(x=782,y=30,height=482)
        self.scrollbar_widget_x_name=Scrollbar(orient=HORIZONTAL,command=self.track_scrollbar_x_name)
        self.scrollbar_widget_x_name.place(x=10,y=510, width=266)
        self.scrollbar_widget_x_url=Scrollbar(orient=HORIZONTAL,command=self.track_scrollbar_x_url)
        self.scrollbar_widget_x_url.place(x=276,y=510, width=275)

        Label(borderwidth=1, relief=GROOVE,text='Name',font=('times',10,'bold'),width=38).place(x=9,y=12)
        self.name_list_widget=Listbox(highlightthickness=0,
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    xscrollcommand=self.scrollbar_widget_x_name.set,
                                    exportselection=False,
                                    width=44,
                                    height=30)
        self.name_list_widget.place(x=9,y=30)
        self.name_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE,text='URL',font=('times',10,'bold'),width=40).place(x=275,y=12)
        self.url_list_widget = Listbox(highlightthickness=0,
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    xscrollcommand=self.scrollbar_widget_x_url.set,
                                    exportselection=False,
                                    width=46,
                                    height=30)
        self.url_list_widget.place(x=275,y=30)
        self.url_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE,text='Progress',font=('times',10,'bold'),width=11).place(x=553,y=12)
        self.progress_list_widget = Listbox(highlightthickness=0,
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    exportselection=False,
                                    width=13,
                                    height=30)
        self.progress_list_widget.place(x=553,y=30)
        self.progress_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE,text='Status',font=('times',10,'bold'),width=22).place(x=630,y=12)
        self.status_list_widget = Listbox(highlightthickness=0,
                                    yscrollcommand=self.scrollbar_widget_y.set,
                                    exportselection=False,
                                    width=25,
                                    height=30)
        self.status_list_widget.place(x=630,y=30)
        self.status_list_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        Label(borderwidth=1, relief=GROOVE,width=2).place(x=782,y=12)

        self.list_boxes.extend((self.name_list_widget,
                                self.url_list_widget,
                                self.progress_list_widget,
                                self.status_list_widget))
        for tList in self.list_boxes:
            tList.bind('<<ListboxSelect>>',self.list_box_selection)

        self.previous_widget = Button(height= 1, width= 8,
                                      font=('times',18,'bold'),
                                      text='Cancel',
                                      command=self.previous_pressed)
        self.previous_widget.place(x=5,y=550)
        self.done_widget = Button(height= 1, width= 8,
                                  font=('times',18,'bold'),
                                  text='Done',
                                  command=self.done_pressed,
                                  state=DISABLED)
        self.done_widget.place(x=683,y=550)
        self.error_report_widget = Button(height= 1,
                                          font=('times',12),
                                          text='Error Report',
                                          command=self.create_error_report_box,
                                          state=DISABLED)
        self.error_report_widget.place(x=555, y=515)

        # Add meta of all streams to be downloaded to the table
        for stream in self.to_download:
            self.name_list_widget.insert(END,stream["stream"].title)
            self.url_list_widget.insert(END,stream["url"])
            self.progress_list_widget.insert(END,"            -")
            self.status_list_widget.insert(END,"                  Queued")

        self.download_thread=threading.Thread(target=self.download)
        self.download_thread.daemon = True
        # Start stream download
        try:
            self.download_thread.start()
        except TclError:
            pass

    def track_scrollbar_y(self, *args):
        # Move up and down in all list boxes via a scroll bar
        for tList in self.list_boxes:
            tList.yview(*args)

    def track_scrollbar_x_name(self, *args):
        # Move side to side in the name list box via a scroll bar
        self.name_list_widget.xview(*args)

    def track_scrollbar_x_url(self, *args):
        # Move side to side in the URL list box via a scroll bar
        self.url_list_widget.xview(*args)

    def on_mouse_wheel(self, event):
        # Control scrolling off all list boxes via the mouse wheel
        for tList in self.list_boxes:
            tList.yview("scroll", event.delta,"units")
        return "break"

    def list_box_selection(self,event):
        # Highlight/unhighlight the cell in every column in the row selected or not selected
        if not event.widget.curselection():
            return
        self.selected_line=event.widget.curselection()[0]
        for tList in self.list_boxes:
            tList.selection_clear(first=0,last=END)
            tList.selection_set(first=self.selected_line)

    def download(self):
        # Downloads each stream in the download list
        download_attempts = 0
        # A stream download should only be attempted the following maximum number of times
        download_attempts_limit = 3
        status = ""
        force_stop = False
        for count,stream in enumerate(self.to_download):
            downloaded = False
            download_attempts = 0
            # the stream_report will store the stream download status and will store any errors
            stream_report = {"stream":stream}
            self.count = count
            status = "Downloading"
            self.update_list(self.status_list_widget,('              '+ status))
            try:
                while not downloaded and not force_stop:
                    try:
                        # if no stream supports the user specified file format then download with a
                        # substitution file format
                        if "sub_format" in stream:
                            filepath = ("%s" %stream["save_location"]+'.'+stream["sub_format"])
                        else:
                            filepath = ("%s" %stream["save_location"]+'.'+stream["chosen_format"])
                        stream["stream"].download(quiet=True,
                                                  callback=self.download_callback,
                                                  filepath=filepath)
                        downloaded = True
                    except Exception as e:
                        if self.stop_download is True:
                            # this will exit the download loop
                            force_stop = True
                        else:
                            download_attempts += 1
                        # TODO: More useful action to take when the limit has been reached
                        if download_attempts == download_attempts_limit:
                            raise Exception("Exceeded maximum download attempts")
                        time.sleep(1)
                if stream["convert_required"] == True:
                    # convert the file if required(when a sub file format is used)
                    status = "Converting"
                    self.update_list(self.status_list_widget,('                 '+status))
                    Convert(stream)
                status="Done"
                stream_report["status"] = "Successful"
                self.update_list(self.status_list_widget,("                     "+status))
            except Exception as e:
                # add stream meta to failed files list
                self.error_list.append({
                                       "name": stream["stream"].title,
                                       "error": e})
                stream_report["status"]=("Failed: ",e)
                # update GUI table status for stream
                if status == "Downloading":
                    self.update_list(self.status_list_widget,"      Error during download")
                elif status == "Converting":
                    self.update_list(self.status_list_widget,"     Error during converting")
                else:
                    self.update_list(self.status_list_widget,"     Unknown error occurred")
            self.download_report.append(stream_report)
            # if one or more streams failed to download activate the error report button
            if self.error_list:
                self.error_report_widget.configure(state=ACTIVE)
        self.previous_widget.configure(text='Back')
        self.done_widget.configure(state=NORMAL)
            
    def download_callback(self, total, recvd, ratio, rate, eta):
        # Updates download progress for a stream on the table
        spaces = "         "
        progress = int(ratio*100)
        if progress == 100:
            spaces = "         "
        self.update_list(self.progress_list_widget, (spaces+str(progress)+'%'))

    def create_error_report_box(self):
        # Creates a window to display a report on the streams that have failed to download or convert
        if self.check_error_report_running():
            return
        self.tErrorReport = Tk()
        self.tErrorReport.title("Error Report")
        self.tErrorReport.geometry("595x400")
        self.tErrorReport.resizable(0,0)
        error_report = Error_Report(self.tErrorReport, self.error_list)
        error_report.mainloop()
        
    def update_list(self, list_widget, message):
        # Updates a cell contents in the table
        list_widget.delete(self.count)
        list_widget.insert(self.count, message)

    def check_error_report_running(self):
        # check if error report window is open
        try:
            self.tErrorReport
        except AttributeError:
            return False
        try:
            if self.tErrorReport.state() == 'normal':
                return True
        except TclError:
            return False

    def previous_pressed(self):
        # Returns back to the input screen and kills the download thread if needed
        if self.check_error_report_running():
            return
        if self.download_thread.isAlive():
            self.download_thread._stopped=True
            self.stop_download = True
        self.kill_window()
        self.next_window = 'download_input'

    def done_pressed(self):
        # Returns to youtube_downloader menu
        if self.check_error_report_running():
            return
        self.kill_window()
        self.next_window = 'main_menu'

class Error_Report(Frame, Screen):
    """ Produces a window to show a list of failed streams and their error messages """
    def __init__(self, master, error_list):
        super(Error_Report, self).__init__(master)
        self.master = master
        self.error_list = error_list
        self.create_widgets()
        
    def create_widgets(self):
        Label(self.master, borderwidth=1, text='Error Report',font=('times',15,'bold')).place(x=230, y=5)
        # create a table to display the error meta data
        self.scrollbar_widget_y=Scrollbar(self.master, command=self.track_scrollbar_y)
        self.scrollbar_widget_y.place(x=563,y=50,height=275)
        self.scrollbar_widget_x_name=Scrollbar(self.master, orient=HORIZONTAL,command=self.track_scrollbar_x_name)
        self.scrollbar_widget_x_name.place(x=10,y=323, width=276)
        self.scrollbar_widget_x_error=Scrollbar(self.master, orient=HORIZONTAL,command=self.track_scrollbar_x_error)
        self.scrollbar_widget_x_error.place(x=286, y=323, width=277)
        Label(self.master, borderwidth=1, relief=GROOVE,text='Name',font=('times',10,'bold'),width=39).place(x=10,y=34)
        self.name_list_widget = Listbox(self.master,
                                         highlightthickness=0,
                                         yscrollcommand=self.scrollbar_widget_y.set,
                                         xscrollcommand=self.scrollbar_widget_x_name.set,
                                         exportselection=False,
                                         width=46,
                                         height=17)
        self.name_list_widget.place(x=10,y=50)
        Label(self.master, borderwidth=1, relief=GROOVE,text='Error message',font=('times',10,'bold'),width=40).place(x=285,y=34)
        self.error_list_widget = Listbox(self.master,
                                         highlightthickness=0,
                                         yscrollcommand=self.scrollbar_widget_y.set,
                                         xscrollcommand=self.scrollbar_widget_x_error.set,
                                         exportselection=False,
                                         width=46,
                                         height=17)
        self.error_list_widget.place(x=285,y=50)
        self.list_boxes = [self.name_list_widget,
                           self.error_list_widget]
        Label(self.master, borderwidth=1, relief=GROOVE,width=2).place(x=563,y=34)
        Button(self.master, width= 10,font=('times',15,'bold'), text='Done', command=self.done_pressed).place(x=220, y=350)
        self.add_errors()

    def track_scrollbar_y(self,*args):
        # Move up and down in all list boxes via a scroll bar
        for tList in self.list_boxes:
            tList.yview(*args)

    def track_scrollbar_x_name(self,*args):
        # Move side to side in the name list box via a scroll bar
        self.name_list_widget.xview(*args)

    def track_scrollbar_x_error(self,*args):
        # Move side to side in the name error box via a scroll bar
        self.error_list_widget.xview(*args)

    def add_errors(self):
        # Add error meta to table
        for error in self.error_list:
            self.name_list_widget.insert(END, error["name"])
            self.error_list_widget.insert(END, error["error"])

    def done_pressed(self):
        # Close window
        self.kill_window()