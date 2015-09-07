import configparser

class Settings_Parser():
    """ Settings parser which will read and write to the configuration file """
    # TODO: Make the settings parser portable
    def __init__(self, settings_file):
        self.file_location = settings_file

    def read_config(self):
        # Read the settings file
        self.config = configparser.SafeConfigParser()
        self.config.read(self.file_location)

    def get_settings(self):
        # Return the configuration parser
        self.read_config()
        return self.config

    def set_option(self, section, option, value):
        # Overwrite an configuration option
        self.read_config()
        self.config.set(section, option, value)
        self.write_config()

    def write_config(self):
        # Write changes to the configuration file
        with open(self.file_location, 'w') as configfile:
            self.config.write(configfile)

