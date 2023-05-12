import subprocess, os, platform


class server:
    '''
    start server through use terimal cmd
    '''

    def __init__(self, port=21):
        self.port = port
        self.system = platform.system()

    def start_server(self, directory, user="", passwd=""):
        '''
        start server
        :param directory: the dict need be shared
        :param stdout: redirect standard output
        :param stderr: redirect error output
        :return:
        '''
        global py_path
        if self.system == "Darwin":
            py_path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "MacOS"), "python")
        else:
            py_path = "python"
        py_path = r"D:\Program Files\JetBrains\pythonProject\FTP4.0\venv\Scripts\python.exe"
        cmd_list = [py_path, "-u", "-m", "pyftpdlib"]
        if directory == "":
            args = [str(self.port)]
        else:
            args = ["-d", directory, "-p", str(self.port)]
        if user == "" or passwd == "":
            pass
        else:
            args.extend(["-u", user, "-P", passwd])
        cmd_list.extend(args)

        if self.system == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.dwFlags |= subprocess.STARTF_USESTDHANDLES

            self.process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        startupinfo=startupinfo)
        else:
            self.process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def stop_server(self):
        '''
        stop server
        :return: close state and close message
        '''
        if hasattr(self, "process"):
            self.process.terminate()
            self.process.wait()
            msg = "Close successfully!"
            return True, msg
        msg = "You don't create server?"
        return False, msg

    def get_server_state(self):
        '''
        get server running state
        :return: True is running, False is stop
        '''
        if hasattr(self, "process"):
            if self.process.poll() is None:
                return True
            return False
        return False

    def getLocalIP(self):
        '''
        get localhost ip for transfer files
        '''
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip, self.port