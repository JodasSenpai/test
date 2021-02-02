import sys
import os
import win32api as api, win32process as proc

class LabelImg:
    def __init__(self):
        self.DIR_PATH = 'None'

    def set_dir_path(self, dir_path):
        if (dir_path != ''):
            self.DIR_PATH = dir_path

    def get_dir_path(self):
        return self.DIR_PATH

    def run_label_img(self):
        if (self.DIR_PATH == 'None'):
            return "No directory chosen"

        info = proc.STARTUPINFO()
        info.hStdInput = api.GetStdHandle(api.STD_INPUT_HANDLE)
        info.hStdOutput = api.GetStdHandle(api.STD_OUTPUT_HANDLE)
        info.hStdError = api.GetStdHandle(api.STD_ERROR_HANDLE)
        python = sys.executable
        scriptDir = os.path.dirname(self.DIR_PATH)
        scriptName = os.path.basename(self.DIR_PATH)
        # print(scriptName)
        proc.CreateProcess(
            None, " ".join((python, scriptName, "grandchild")), None,
            None, 1, 0, os.environ, scriptDir, info)
        sys.stdout.flush()