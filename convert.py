from subprocess import Popen, PIPE
import os

class Convert():
    """ Use ffmpeg to convert a media file """
    def __init__(self, dest_file_path, src_file_path, start_time, end_time):
        command = self.build_command(dest_file_path, src_file_path, start_time, end_time)
        print(command)
        self.execute_command(command)
        self.remove_original(src_file_path)

    def build_command(self, file_path, sub_file_path, start_time, end_time):
        # builds command for ffmpeg to convert stream
        command = ('ffmpeg -i \"%s\" -ss %s -to %s -async 1 \"%s\"'
                        %(sub_file_path, start_time, end_time, file_path))
        return command

    def execute_command(self, cmd):
        # execute command
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        proc.communicate()

    def remove_original(self, sub_file_path):
        # remove the old format
        os.remove(sub_file_path)