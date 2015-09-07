from subprocess import Popen, PIPE
import os

class Convert():
    """ Use ffmpeg to convert a media file """
    def __init__(self, instructions):
        command = self.build_command(instructions)
        self.execute_command(command)
        self.remove_original(instructions["save_location"], instructions["sub_format"])

    def build_command(self, instructions):
        # builds command for ffmpeg based on instructions
        command = ("ffmpeg -i \"%s.%s\" -ss %s -t %s -async 1 \"%s.%s\""
                %(instructions["save_location"],
                  instructions["sub_format"],
                  instructions["start_time"],
                  instructions["end_time"],
                  instructions["save_location"],
                  instructions["chosen_format"]
                ))
        return command

    def execute_command(self, cmd):
        # execute command
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        proc.communicate()

    def remove_original(self,location, file_format):
        # remove the old format
        os.remove("%s.%s" %(location, file_format))