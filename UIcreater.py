import shutil, random, string, os, tkinter, re, multiprocessing, threading
import time
from tkinter import *
from tkinter.messagebox import *
import tkinter.ttk as ttk
from tkinterdnd2 import *
import ftpserver
import pyperclip
import httpserver
import logic


class GUI:
    def __init__(self):
        self.ftp_share_path = None
        self.http_share_path = None
        self.ftpserver = ftpserver.server()
        self.httpserver = httpserver.server()

    def main(self):
        '''
        UI main entrance
        :return:
        '''
        win = TkinterDnD.Tk()
        win.title("file server")

        w = 500
        h = 700
        # get screen width and height for make software locate center in screen
        ws = win.winfo_screenwidth()
        hs = win.winfo_screenheight()

        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))

        win.geometry(f"{w}x{h}+{x}+{y}")
        win.resizable(False, False)
        win.update()

        def on_close():
            if askokcancel("Quit", "Do you want to quit?"):
                if hasattr(self, "ftp_share_path") and not self.ftp_share_path is None:
                    shutil.rmtree(self.ftp_share_path, ignore_errors=True)
                    self.ftp_share_path = None
                if hasattr(self, "http_share_path") and not self.http_share_path is None:
                    shutil.rmtree(self.http_share_path, ignore_errors=True)
                    self.http_share_path = None
                self.ftpserver.stop_server()
                self.httpserver.stop_server()
                win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        self.content(win)

        win.mainloop()

    def content(self, root):
        '''
        draw all widget
        :param root: windows
        :return:
        '''
        Label(root, text="服务端", font=("黑体", 15)).pack(side=TOP, fill=X)
        Label(root, text="copyright@2023-2024 Lucas sun", font=("宋体", 10), anchor="w", relief="groove").pack(
            side=BOTTOM,
            fill=X)

        description = LabelFrame(root, text="Readme")
        description.pack(side=TOP, fill=X, padx=5)
        text = '''本软件用于局域网下传送文件。
本软件主要针对比较大型的文件,下面有两种传输协议可供选择。
操作简单，容易上手，新手教程如下：
  1.选择传输协议(http协议需要客户端在浏览器输入，
      ftp需要客户端在文件管理器或支持ftp协议下载的软件使用)
  2.需要这份文件的其他用户在局域网内相应位置输入网址即可访问'''
        Label(description, text=text, justify=LEFT, font=("黑体", 12), wraplength=480).pack(side=TOP, fill=BOTH,
                                                                                          expand=True)
        Label(description, text="注意：文件列表不可更改，如需更改，重新拖动文件覆盖即可", anchor=W, foreground="red", font=("黑体", 10)).pack(
            side=TOP, fill=BOTH, expand=True)

        url = LabelFrame(root, text="url")
        url.pack(side=TOP, fill=X, padx=5)
        self.IPLabel = Entry(url, relief="flat", font=("consolas", 25), bg='gray94', justify=CENTER)
        self.IPLabel.pack(side=LEFT, fill=X, padx=5, expand=True)
        self.IPLabel.config(state="readonly")

        def copy(str):
            pyperclip.copy(str)

            def timer():
                self.button.config(text="复制成功", state=DISABLED)
                time.sleep(1)
                self.button.config(text="复制", state=NORMAL)

            threading.Thread(target=timer, daemon=True).start()

        self.button = Button(url, text="复制", width=10, command=lambda: copy(self.IPLabel.get()))
        self.button.config(state=DISABLED)
        self.button.pack(side=LEFT, fill=X, padx=3)

        tab_Style = ttk.Style()
        tab_Style.configure('TNotebook.Tab', font=('黑体', '14'))
        ttk.Style().configure('my.TNotebook', tabposition="nesw")
        tab = ttk.Notebook(root, style="my.TNotebook")
        tab.pack(side=TOP, fill=BOTH, padx=5, pady=(10, 5), expand=True)
        self.ftpFrame = Frame(root)
        self.httpFrame = Frame(root)
        tab.add(self.ftpFrame, text="ftp协议")
        tab.add(self.httpFrame, text="http协议")

        def ftp_content(Frame):
            '''
            ftp notebook content
            :param Frame: ftp notebook frame
            :return:
            '''
            upassword = tkinter.Frame(Frame)
            upassword.pack(side=TOP)
            Label(upassword, text="账号：").grid(row=0, column=0, pady=(10, 5))
            self.user = Entry(upassword)
            self.user.grid(row=0, column=1, columnspan=2, pady=(10, 5))
            Label(upassword, text="密码：").grid(row=0, column=3, pady=(10, 5))
            self.passwd = Entry(upassword)
            self.passwd.grid(row=0, column=4, columnspan=2, pady=(10, 5))

            self.Fdrag = Label(Frame, text="拖拽文件到这里", background="gray", font=("黑体", 14))
            self.Fdrag.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
            self.Fdrag.drop_target_register(DND_FILES)

            self.Fdrag.dnd_bind("<<Drop>>", self.ftp_drag)

            def white_color(event):
                self.Fdrag.configure(background="white")

            self.Fdrag.dnd_bind("<<DropEnter>>", white_color)

            def gray_color(event):
                self.Fdrag.configure(background="gray")

            self.Fdrag.dnd_bind("<<DropLeave>>", gray_color)

            file_path = LabelFrame(Frame, text="文件列表")
            file_path.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
            yBar = Scrollbar(file_path, orient=VERTICAL)
            yBar.pack(side=RIGHT, fill=Y)
            xBar = Scrollbar(file_path, orient=HORIZONTAL)
            xBar.pack(side=BOTTOM, fill=X)
            self.ftpfileList = Listbox(file_path, height=1, font=("consolas", 12), xscrollcommand=xBar.set,
                                       yscrollcommand=yBar.set)
            self.ftpfileList.pack(fill=BOTH, expand=True)
            yBar.config(command=self.ftpfileList.yview)
            xBar.config(command=self.ftpfileList.xview)

        def http_content(Frame):
            '''
            http notebook content
            :param Frame: http notebook frame
            :return:
            '''
            iszipped = tkinter.Frame(Frame)
            iszipped.pack(side=TOP)
            self.protocol = StringVar()
            self.protocol.set("zip")
            R1 = Radiobutton(iszipped, text="压缩", font=("黑体", 12), anchor=W, variable=self.protocol, value="zip")
            R1.grid(row=0, column=0, padx=(0, 20))
            R2 = Radiobutton(iszipped, text="不压缩", font=("黑体", 12), anchor=W, variable=self.protocol, value="nozip")
            R2.grid(row=0, column=1, padx=(20, 0))

            self.Hdrag = Label(Frame, text="拖拽文件到这里", background="gray", font=("黑体", 14))
            self.Hdrag.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
            self.Hdrag.drop_target_register(DND_FILES)

            self.Hdrag.dnd_bind("<<Drop>>", self.http_drag)

            def white_color(event):
                self.Hdrag.configure(background="white")

            self.Hdrag.dnd_bind("<<DropEnter>>", white_color)

            def gray_color(event):
                self.Hdrag.configure(background="gray")

            self.Hdrag.dnd_bind("<<DropLeave>>", gray_color)

            file_path = LabelFrame(Frame, text="文件列表")
            file_path.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
            yBar = Scrollbar(file_path, orient=VERTICAL)
            yBar.pack(side=RIGHT, fill=Y)
            xBar = Scrollbar(file_path, orient=HORIZONTAL)
            xBar.pack(side=BOTTOM, fill=X)
            self.httpfileList = Listbox(file_path, height=1, font=("consolas", 12), xscrollcommand=xBar.set,
                                        yscrollcommand=yBar.set)
            self.httpfileList.pack(fill=BOTH, expand=True)
            yBar.config(command=self.httpfileList.yview)
            xBar.config(command=self.httpfileList.xview)

        ftp_content(self.ftpFrame)
        http_content(self.httpFrame)

    def show_IP(self, text):
        self.IPLabel.config(state=NORMAL)
        self.IPLabel.delete("0", END)
        self.IPLabel.insert(END, text)
        self.IPLabel.config(state="readonly")
        self.button.config(state=NORMAL)

    def clear_IP(self):
        self.IPLabel.config(state=NORMAL)
        self.IPLabel.delete("0", END)
        self.IPLabel.config(state="readonly")
        self.button.config(state=DISABLED)

    def show_ftpfile(self, text):
        if hasattr(self, "ftpfileList"):
            self.ftpfileList.insert(END, text)

    def clear_ftpfile(self):
        if hasattr(self, "ftpfileList"):
            self.ftpfileList.delete("0", END)

    def show_httpfile(self, text):
        if hasattr(self, "httpfileList"):
            self.httpfileList.insert(END, text)

    def clear_httpfile(self):
        if hasattr(self, "httpfileList"):
            self.httpfileList.delete("0", END)

    @classmethod
    def get_all_path(cls, paths):
        '''
        Class Method: Split path from string to list
        :param paths: string
        :return: list
        '''
        dirString = paths
        file_path = []
        pattern = re.compile(r"{(.+?)}")
        file_path.extend(pattern.findall(dirString))
        for dir in file_path:
            dirString = dirString.replace("{" + dir + "}", "").replace("  ", " ").strip()
        file_path.extend(dirString.split())
        del dirString
        return file_path

    @classmethod
    def Move(cls, directorys, targetpath, pipe):
        '''
        Move folders and files to cache
        :return:
        '''
        share_path = targetpath
        if not os.path.exists(share_path):
            os.mkdir(share_path)
        for directory in directorys:
            if os.path.isdir(directory):
                shutil.copytree(directory, os.path.join(share_path, os.path.basename(directory)))
            else:
                shutil.copy(directory, os.path.join(share_path, os.path.basename(directory)))
        pipe.send(share_path)
        pipe.close()

    def ftp_drag(self, event):
        try:
            self.ftpserver.stop_server()
            self.httpserver.stop_server()
            if hasattr(self, "Fdrag"):
                self.Fdrag.configure(background="gray")
            file_paths = GUI.get_all_path(event.data)
            self.clear_ftpfile()
            for path in file_paths:
                self.show_ftpfile(path)
                if not self.ftp_share_path is None and (
                        os.path.basename(self.ftp_share_path) in path or os.path.basename(path) in self.ftp_share_path):
                    raise Exception("缓存文件不允许分享！！！请检查你的分享文件")
            self.ftp_share()
        except Exception as e:
            self.clear_IP()
            showerror("错误", str(e))

    def ftp_share(self):
        try:
            if hasattr(self, "ftpfileList"):
                directorys = self.ftpfileList.get("0", END)
            else:
                raise Exception("没有路径")
            if not self.ftp_share_path is None:
                shutil.rmtree(self.ftp_share_path, ignore_errors=True)

            dirname = "".join(random.sample(string.ascii_letters, 6))
            share_path = os.path.join(os.getcwd(), dirname)
            for dir in directorys:
                if self.ftp_share_path is None and os.path.basename(dir) in share_path:
                    raise Exception("缓存文件不允许分享！！！请检查你的分享文件")
            (con1, con2) = multiprocessing.Pipe()
            move = multiprocessing.Process(target=GUI.Move, args=(directorys, share_path, con1), daemon=True)
            move.start()

            def Share(T: multiprocessing.Process):
                try:
                    T.join(timeout=10)
                    if T.is_alive():
                        T.terminate()
                        T.join()
                        T.close()
                        raise Exception("文件太大啦~")
                    share_path = con2.recv()
                    con2.close()
                    self.ftp_share_path = share_path
                    if hasattr(self, "user") and hasattr(self, "passwd"):
                        self.ftpserver.start_server(self.ftp_share_path, self.user.get(), self.passwd.get())
                    else:
                        self.ftpserver.start_server(self.ftp_share_path)

                    def check_server():
                        try:
                            for i in range(10):
                                pipe = self.ftpserver.process.stdout.readline().decode()
                                pattern = re.compile(r"starting FTP server")
                                if not pattern.search(pipe) is None:
                                    self.show_IP(f"ftp://{self.ftpserver.getLocalIP()[0]}")
                                    return 0
                            raise Exception("启动失败！")
                        except Exception as e:
                            self.clear_IP()
                            showerror("错误", str(e))

                    threading.Thread(target=check_server, daemon=True).start()
                except Exception as e:
                    self.clear_IP()
                    showerror("错误", str(e))

            share = threading.Thread(target=Share, args=(move,), daemon=True)
            share.start()

        except Exception as e:
            self.clear_IP()
            showerror("错误", str(e))

    @classmethod
    def preprocessing(cls, directorys, pipe):
        '''
        preprocess path
        :param directory:
        :return:
        '''
        dirname = "".join(random.sample(string.ascii_letters, 6))
        perfect_dir = False
        share_path = os.path.join(os.getcwd(), dirname)
        if not os.path.exists(share_path):
            os.mkdir(share_path)
        for directory in directorys:
            result = logic.judge_file_type(directory)
            if result[0] == logic.PATH:
                if result[1]:
                    perfect_dir = True
                    shutil.copytree(directory, os.path.join(share_path, os.path.basename(directory)))
                else:
                    perfect_dir = False
                    logic.zip_item(directory, os.path.join(share_path,
                                                           os.path.basename(directory).split(r".")[0] + ".zip"))
            elif result[0] == logic.TEXT:
                perfect_dir = False
                logic.zip_item(directory, os.path.join(share_path,
                                                       os.path.basename(directory).split(r".")[0] + ".zip"))
            elif result[0] == logic.STREAM:
                perfect_dir = False
                shutil.copy(directory, share_path)
            elif result[0] == logic.APP:
                dir_name = "".join(random.sample(string.ascii_letters, 6))
                temp_path = os.path.join(os.path.dirname(directory), dir_name)
                shutil.copytree(directory, os.path.join(temp_path, os.path.basename(directory)))
                logic.zip_item(temp_path, os.path.join(share_path,
                                                       os.path.basename(directory).split(r".")[0] + ".zip"))
                logic.delete_dir(temp_path)
        pipe.send((perfect_dir, share_path))
        pipe.close()

    def http_drag(self, event):
        global preprocessing
        self.httpserver.stop_server()
        self.ftpserver.stop_server()
        if hasattr(self, "Hdrag"):
            self.Hdrag.configure(background="gray")
        if not self.http_share_path is None:
            shutil.rmtree(self.http_share_path, ignore_errors=True)
        file_paths = GUI.get_all_path(event.data)
        self.clear_httpfile()
        for path in file_paths:
            self.show_httpfile(path)
            if not self.http_share_path is None and (
                    os.path.basename(self.http_share_path) in path or os.path.basename(path) in self.http_share_path):
                raise Exception("缓存文件不允许分享！！！请检查你的分享文件")

        (con1, con2) = multiprocessing.Pipe()
        if hasattr(self, "httpfileList"):
            preprocessing = multiprocessing.Process(target=GUI.preprocessing,
                                                    args=(self.httpfileList.get("0", END), con1), daemon=True)
            preprocessing.start()

        def Share(T: multiprocessing.Process):
            try:
                T.join(10)
                if T.is_alive():
                    T.terminate()
                    T.join()
                    T.close()
                    raise Exception("文件太大啦~")
                (_, share_path) = con2.recv()
                for dir in file_paths:
                    if self.http_share_path is None and os.path.basename(dir) in share_path:
                        raise Exception("缓存文件不允许分享！！！请检查你的分享文件")
                self.http_share_path = share_path
                con2.close()
                self.httpserver.start_server(self.http_share_path)
                for i in range(10):
                    pipe = self.httpserver.process.stdout.readline().decode()
                    pattern = re.compile(r"Serving HTTP on")
                    if not pattern.search(pipe) is None:
                        self.show_IP(f"{self.httpserver.getLocalIP()[0]}")
                        return 0
                raise Exception("启动失败")
            except Exception as e:
                self.clear_IP()
                showerror("错误", str(e))

        share = threading.Thread(target=Share, args=(preprocessing,), daemon=True)
        share.start()
