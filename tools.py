import pafy
import datetime

class stream_gen():
    """ Creates a stream object based on user input, such as URL and download format """
    def __init__(self,url_conf):
        self.url_conf = url_conf
        self.sub_format = None
        self.error_messages = None
        # Checks if URL exists
        try:
            #logger.log_debug('Checking if URL exists \'%s\'' % url)
            self.vid = pafy.new(url_conf["url"])
            #logger.log_debug('URL found.')
        except (IOError, ValueError): # Catches the exception if the URL wasn't found
            self.error_messages = ('URL not found: %s' %self.url_conf["url"])
            return
        # handle any unexpected pafy exceptions
        except Exception:
            self.error_messages = ('An unexpected error occurred when searching for URL \'%s\', please try again.' 
                                   %self.url_conf["url"])
            return
            #logger.log_debug('URL not found. Exception: %s' % e)
        # check that the user specified start/end time will fit with the stream
        if ('start_time' or 'end_time') in self.url_conf:
            self.check_time()
        # if there have been no error messages, set the stream format
        if not self.error_messages:
            self.set_media_format()

    def check_time(self):
        # carry's out various checks on the start and end time
        duration = datetime.datetime.strptime('%s' %self.get_duration(), '%H:%M:%S').time()
        # check if a start time has been defined
        if "start_time" in self.url_conf:
            try:
                start_time = datetime.datetime.strptime('%s' %self.url_conf["start_time"], 
                                                        '%H:%M:%S').time()
            except ValueError:
                # catch an exception when the time does not match the pattern 'HH:MM:SS'
                self.error_messages = ("The \'start time\' does not match the format \'HH:MM:SS\' for URL: \'%s\'."
                                       %self.url_conf["url"])
                return
            # check that the start time is less than the duration
            if start_time > duration:
                self.error_messages = ("The start time must be less than the duration for URL: \'%s\'" 
                                       %self.url_conf["url"])
        # check if a end time has been defined
        if "end_time" in self.url_conf:
            try:
                end_time = datetime.datetime.strptime('%s' %self.url_conf["end_time"], '%H:%M:%S').time()
            except ValueError:
                self.error_messages = ("The \'end time\' does not match the format \'HH:MM:SS\' for URL: \'%s\'."
                                       %self.url_conf["url"])
                return
            if end_time > duration:
                self.error_messages = ("The end time must be less than the duration for URL: \'%s\'" 
                                       %self.url_conf["url"])
        if ((("start_time" and "end_time") in self.url_conf) and start_time > end_time):
            self.error_messages = ("The start time must be less than the end time for URL: \'%s\'" 
                                   %self.url_conf["url"])
            return
        
    def set_media_format(self):
        # set the stream type based on the file format the user defined.
        chosen_format = self.url_conf["chosen_format"] # the file format such as mp3
        format_type = self.url_conf["format_type"] # media type such as just audio or audio and video
        # cycle through all streams available to check if the user defined file format is supported
        for s in self.get_allstreamlist():
            if s.extension == chosen_format and s.mediatype == "normal":
                self.stream = self.get_bestnormal(chosen_format)
                return
            if s.extension == chosen_format and s.mediatype == "audio":
                self.stream = self.get_bestaudio(chosen_format)
                return
        # if the chosen file format is not in the stream list, get the best quality stream of 
        # the same format type 
        if format_type=='av':
            self.stream = self.get_bestnormal()
        elif format_type=='a':
            self.stream = self.get_bestaudio()
        # get the format of the stream generated
        self.sub_format = self.stream.extension

    def get_stream(self):
        # return stream object
        return self.stream                       
        
    def get_title(self):
        # return URL title
        return self.vid.title

    def get_duration(self):
        # return URL duration
        return self.vid.duration

    def get_published(self):
        # return URL publish date
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

