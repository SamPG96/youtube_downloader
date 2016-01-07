import configparser

class Settings_Parser():
    """ Settings parser which will read and write to the configuration file """
    def __init__(self, settings_file):
        self.file_location = settings_file
        self.parse()

    def parse(self):
        # read and parse settings
        self.parse_config_file()
        self.set_defaults()

    def parse_config_file(self):
        # read in parse the config file
        # set up config file parser
        self.read_config()
        self.download_directory = self.config_file_parser["LOCATIONS"]["download"]
        self.default_file_format = self.config_file_parser["FORMAT"]["default_format"]
        self.audio_only_formats = self.config_file_parser["FORMAT"]["supported_audio_only_formats"].split(",")
        self.video_only_formats = self.config_file_parser["FORMAT"]["supported_video_only_formats"].split(",")
        self.audio_and_video_formats = self.config_file_parser["FORMAT"]["supported_audio_and_video_formats"].split(",")

    def set_defaults(self):
        # set any default settings for the program
        pass

    def read_config(self):
        # Read the config file
        self.config_file_parser = configparser.SafeConfigParser()
        self.config_file_parser.read(self.file_location)

    def write_config(self):
        # Write changes to the configuration file
        with open(self.file_location, 'w') as configfile:
            self.config_file_parser.write(configfile)

    def set_option(self, section, option, value):
        # Overwrite an configuration option
        self.config_file_parser.set(section, option, value)
        self.write_config()
        self.parse_config_file()

    def set_download_directory(self, directory):
        # overwrites the download directory path in the config file
        self.set_option("LOCATIONS", "download", directory)

    def set_default_file_format(self, file_format):
        # overwrites the default file format in the config file
        self.set_option("FORMAT", "default_format", file_format)

    def get_audio_only_formats(self):
        # return all file format that support audio only
        return self.audio_only_formats

    def get_video_only_formats(self):
        # return all file format that support video only
        return self.video_only_formats

    def get_audio_and_video_formats(self):
        # return all file format that support audio and video
        return self.audio_and_video_formats

    def get_format_type(self, file_format):
        # returns the format type code for the given format
        # a - audio only
        # v - video only
        # av - audio and video
        if file_format in self.audio_only_formats:
            return 'a'
        elif file_format in self.video_only_formats:
            return 'v'
        elif file_format in self.audio_and_video_formats:
            return 'av'

    def get_supported_formats(self):
        # return all supported download/convert formats
        return self.get_audio_only_formats() + self.get_video_only_formats() + self.get_audio_and_video_formats()

    def get_default_file_format(self):
        # returns the default file format
        return self.default_file_format

    def get_download_directory(self):
        # returns the download directory path
        return self.download_directory
