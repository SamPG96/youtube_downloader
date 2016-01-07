import pafy
import datetime
import os

class Stream_Generator():
    def __init__(self, url, start_time, end_time, format_type,
                 chosen_format, top_dir):
        self.url = url
        self.start_time = start_time
        self.end_time = end_time
        self.start_time_set = False
        self.end_time_set = False
        self.title = None
        self.duration = None
        self.stream = None
        self.vid = None
        self.chosen_format = chosen_format
        self.sub_format = None
        self.format_type = format_type
        self.file_path = None # final path to download stream to
        self.temp_file_path = None # temporary file path for convertion/trimming
        self.top_dir = top_dir
        self.error_messages = None
        self.disallowed_characters = ['~', '#', '%', '*', '{', '}', '\\',
                                      ':', '<', '>', '?', '/', '+', '|', '"']

    def generate(self):
        # build stream and set user configuration while handling errors
        self.set_url()
        if self.get_errors():
            return
        self.set_time()
        if self.get_errors():
            return
        self.set_media_format()
        if self.get_errors():
            return
        self.set_title()
        self.set_file_path()

    def set_url(self):
        # create a new pafy object from url
        try:
            #logger.log_debug('Checking if URL exists \'%s\'' % url)
            self.vid = pafy.new(self.url)
            #logger.log_debug('URL found.')
        except (IOError, ValueError): # Catches the exception if the URL wasn't found
            self.error_messages = ('URL not found: %s' %self.url)
        # handle any unexpected pafy exceptions
        except Exception as e:
            self.error_messages = ('An unexpected error occurred when searching for '
                                   'URL \'%s\', please try again.' %self.url)
            print(e)
            #logger.log_debug('URL not found. Exception: %s' % e)

    def set_title(self):
        # parse the title of the stream so that it is allowed to be used as a filename
        title = self.stream.title
        title = title.replace('"', '\'')
        title = title.replace('&', 'and')
        for character in self.disallowed_characters:
            title = title.replace(character, '')
        self.title = title

    def set_file_path(self):
        # builds a file path for the stream to be downloaded to and builds a temporary
        # path if a conversion is required or the stream needs to be trimmed. duplicate
        # filenames are checked and handled here.
        file_path = os.path.join(self.top_dir, self.title)
        # add ' - Copy' to the filename until its unique
        while os.path.isfile(file_path + "." + self.chosen_format):
            file_path += " - Copy"
        if self.is_convert_required():
            temp_file_path = file_path + '_TEMP'
            # add '_TEMP' to the temporary file filename until its unique
            while os.path.isfile(temp_file_path + '.' + self.sub_format):
                temp_file_path += '_TEMP'
            self.temp_file_path = temp_file_path + '.' + self.sub_format
        elif self.is_trimmed():
            temp_file_path = file_path + '_TEMP'
            # add '_TEMP' to the temporary file filename until its unique
            while os.path.isfile(temp_file_path + '.' + self.chosen_format):
                temp_file_path += '_TEMP'
            self.temp_file_path = temp_file_path + '.' + self.chosen_format
        self.file_path = file_path + '.' + self.chosen_format

    def set_time(self):
        # carry's out various checks and sets the start and end time
        duration = datetime.datetime.strptime('%s' %self.get_duration(), '%H:%M:%S').time()
        # check if a start time has been defined
        if self.start_time:
            self.start_time_set = True
            try:
                self.start_time = datetime.datetime.strptime('%s' %self.start_time,
                                                        '%H:%M:%S').time()
            except ValueError:
                # catch an exception when the time does not match the pattern 'HH:MM:SS'
                self.error_messages = ("The \'start time\' does not match the format \'HH:MM:SS\' for URL: \'%s\'."
                                       %self.url)
                return
            # check that the start time is less than the duration
            if self.start_time > duration:
                self.error_messages = ("The start time must be less than the duration for URL: \'%s\'" 
                                       %self.url)
        else:
            self.start_time = datetime.datetime.strptime('00:00:00',
                                                        '%H:%M:%S').time()
        # check if a end time has been defined
        if self.end_time:
            self.end_time_set = True
            try:
                self.end_time = datetime.datetime.strptime('%s' %self.end_time, '%H:%M:%S').time()
            except ValueError:
                self.error_messages = ("The \'end time\' does not match the format \'HH:MM:SS\' for URL: \'%s\'."
                                       %self.url)
                return
            if self.end_time > duration:
                self.error_messages = ("The end time must be less than the duration for URL: \'%s\'" 
                                       %self.url)
        else:
            self.end_time = duration
        if self.start_time > self.end_time:
            self.error_messages = ("The start time must be less than the end time for URL: \'%s\'" 
                                   %self.url)
            return
        self.duration = duration

    def set_media_format(self):
        # cycle through all streams available to check if the user defined file format is supported
        for s in self.get_allstreamlist():
            if s.extension == self.chosen_format and s.mediatype == "normal":
                self.stream = self.get_bestnormal(self.chosen_format)
                return
            if s.extension == self.chosen_format and s.mediatype == "audio":
                self.stream = self.get_bestaudio(self.chosen_format)
                return
        # if the chosen file format is not in the stream list, get the best quality stream of
        # the same format type as a substitution for now
        if self.format_type == 'av':
            self.stream = self.get_bestnormal()
        elif self.format_type == 'a':
            self.stream = self.get_bestaudio()
        # get the format of the stream generated
        self.sub_format = self.stream.extension

    def update_properties(self):
        # update stream attributes to account for internal/environment changes
        self.set_title()
        self.set_file_path()

    def is_convert_required(self):
        # check if the video needs to be converted to the chosen_format
        if self.sub_format:
            return True
        else:
            return False

    def is_start_time_set(self):
        # check if user has defined the start_time
        return self.start_time_set

    def is_end_time_set(self):
        # check if user has defined the end_time
        return self.end_time_set

    def is_trimmed(self):
        # checks if the user has trimmed the times of the video
        if self.start_time_set or self.end_time_set:
            return True
        else:
            return False

    def get_errors(self):
        return self.error_messages

    def get_stream(self):
        # return stream object
        return self.stream                

    def get_title(self):
        # return video title
        return self.title

    def get_url(self):
        # return youtube URL
        return self.url

    def get_start_time(self):
        # returns user specified start time
        return self.start_time

    def get_end_time(self):
        # returns user specified end time
        return self.end_time

    def get_chosen_format(self):
        # return user chosen format
        return self.chosen_format

    def get_file_path(self):
        # returns the designated file path
        return self.file_path

    def get_temp_file_path(self):
        # returns the temporary file path for use with convertion and trimming
        return self.temp_file_path

    def get_duration(self):
        # return video duration in its standard form
        return self.vid.duration

    def get_published(self):
        # return video publish date
        return self.vid.published

    def get_allstreamlist(self):
        # return all streams available
        return self.vid.allstreams

    def get_bestnormal(self, stream_format= "any"):
        # return the best audio and video stream
        return self.vid.getbest(preftype=stream_format)

    def get_bestaudio(self, stream_format = "any"):
        # return the best audio stream only
        return self.vid.getbestaudio(preftype=stream_format)
