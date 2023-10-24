import shutil, random, string, os, tkinter, re, multiprocessing, threading, platform
import sys
import time
import pkg_resources
import ctypes
from tkinter import *
from tkinter.messagebox import *
import tkinter.ttk as ttk
from tkinterdnd2 import *
import pyperclip
import Logic.ftpserver as ftpserver
import Logic.httpserver as httpserver
import Logic.Logic as Logic


class GUI:
    def __init__(self):
        self.Hport = None
        self.Fport = None
        self.ftp_share_path = None
        self.http_share_path = None
        self.ftpserver = ftpserver.server()
        self.httpserver = httpserver.server()
        self.Fuse = True
        self.Huse = True

    def main(self):
        '''
        UI main entrance
        :return:
        '''
        win = TkinterDnD.Tk()
        win.title("file server")

        if platform.system() == "Windows":
            my_icon = pkg_resources.resource_filename(__name__, "Resource/server.ico")
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_icon)
            win.iconbitmap(my_icon)

        w = 600
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
                if hasattr(self, "http_share_path") and not self.http_share_path is None and not self.httpprotocol.get() == "nocache":
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
        Label(description, text=text, justify=LEFT, anchor=W, font=("黑体", 12), wraplength=480).pack(side=TOP, fill=BOTH,
                                                                                          expand=True)
        Label(description, text="注意：文件列表不可更改，如需更改，重新拖动文件覆盖即可", anchor=W, foreground="red", font=("黑体", 10)).pack(
            side=TOP, fill=BOTH, expand=True)

        url = LabelFrame(root, text="url")
        url.pack(side=TOP, fill=X, padx=5)
        self.IPLabel = Entry(url, relief="flat", font=("consolas", 25), bg='gray94', justify=CENTER)
        self.IPLabel.pack(side=LEFT, fill=X, padx=5, expand=True)
        self.IPLabel.config(state="readonly")

        def copy():
            try:
                pyperclip.copy(self.IPLabel.get())
                def timer():
                    self.button.config(text="复制成功", state=DISABLED)
                    time.sleep(1)
                    self.button.config(text="复制", state=NORMAL)

                threading.Thread(target=timer, daemon=True).start()
            except Exception as e:
                showerror("错误", str(e))

        self.button = Button(url, text="复制", width=10, command=copy)
        self.button.config(state=DISABLED)
        self.button.pack(side=LEFT, fill=X, padx=3)

        tab_Style = ttk.Style()
        tab_Style.configure('TNotebook.Tab', font=('黑体', '14'), anchor="nesw")
        ttk.Style().configure('my.TNotebook', tabposition="nesw")
        tab = ttk.Notebook(root, style="my.TNotebook")
        tab.pack(side=TOP, fill=BOTH, padx=5, pady=(10, 5), expand=True)
        self.ftpFrame = Frame(root)
        self.httpFrame = Frame(root)
        tab.add(self.httpFrame, text="http协议")
        tab.add(self.ftpFrame, text="ftp协议")

        def ftp_content(Frame):
            '''
            ftp notebook content
            :param Frame: ftp notebook frame
            :return:
            '''
            upassword = tkinter.Frame(Frame)
            upassword.pack(side=TOP)
            Label(upassword, text="账号：").grid(row=0, column=0, pady=(10, 5))
            self.user = Entry(upassword, width=14)
            self.user.grid(row=0, column=1, columnspan=2, pady=(10, 5))
            Label(upassword, text="密码：").grid(row=0, column=3, pady=(10, 5))
            self.passwd = Entry(upassword, width=14)
            self.passwd.grid(row=0, column=4, columnspan=2, pady=(10, 5))
            Label(upassword, text="端口号：").grid(row=0, column=6, padx=(25, 0), pady=(10, 5))
            self.Fport = Entry(upassword, width=6)
            self.Fport.grid(row=0, column=7, pady=(10, 5))
            self.Fport.insert(END, "2121")

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
            self.httpprotocol = StringVar()
            self.httpprotocol.set("zip")
            R1 = Radiobutton(iszipped, text="压缩", font=("黑体", 12), anchor=W, variable=self.httpprotocol, value="zip")
            R1.grid(row=0, column=0, padx=(0, 40), pady=(10, 5))
            R2 = Radiobutton(iszipped, text="不压缩", font=("黑体", 12), anchor=W, variable=self.httpprotocol, value="nozip")
            R2.grid(row=0, column=1, padx=(0, 0), pady=(10, 5))
            R3 = Radiobutton(iszipped, text="不缓存", font=("黑体", 12), anchor=W, variable=self.httpprotocol, value="nocache")
            R3.grid(row=0, column=2, padx=(40, 0), pady=(10, 5))
            Label(iszipped, text="端口号：").grid(row=0, column=3, padx=(25, 0), pady=(10, 5))
            self.Hport = Entry(iszipped, width=6)
            self.Hport.grid(row=0, column=4, pady=(10, 5))
            self.Hport.insert(END, "80")

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
    def Move(cls, directorys, targetpath, pipe=None):
        '''
        Move folders and files to cache
        :return:
        '''
        share_path = targetpath
        if not os.path.exists(share_path):
            os.makedirs(share_path)
        for directory in directorys:
            if os.path.isdir(directory):
                shutil.copytree(directory, os.path.join(share_path, os.path.basename(directory)))
            else:
                shutil.copy(directory, os.path.join(share_path, os.path.basename(directory)))
        if not pipe is None:
            pipe.send(share_path)
            pipe.close()

    def ftp_drag(self, event):
        try:
            if self.Fuse:
                self.clear_IP()
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
            else:
                showerror("错误", "请稍后操作")
                if hasattr(self, "Fdrag"):
                    self.Fdrag.configure(background="gray")
        except Exception as e:
            self.clear_IP()
            if hasattr(self, "ftp_share_path") and not self.ftp_share_path is None:
                shutil.rmtree(self.ftp_share_path, ignore_errors=True)
                self.ftp_share_path = None
            if hasattr(self, "http_share_path") and not self.http_share_path is None and not self.httpprotocol.get() == "nocache":
                shutil.rmtree(self.http_share_path, ignore_errors=True)
                self.http_share_path = None
            showerror("错误", str(e))

    def ftp_share(self):
        try:
            if hasattr(self, "ftpfileList"):
                directorys = self.ftpfileList.get("0", END)
            else:
                raise Exception("没有路径")
            if not self.ftp_share_path is None:
                shutil.rmtree(self.ftp_share_path, ignore_errors=True)
                self.ftp_share_path = None

            dirname = "".join(random.sample(string.ascii_letters, 6))
            share_path = os.path.join(os.path.expanduser("~"), "Library")
            share_path = os.path.join(share_path, "FileServer")
            share_path = os.path.join(share_path, dirname)
            for dir in directorys:
                if self.ftp_share_path is None and os.path.basename(dir) in share_path:
                    raise Exception("缓存文件不允许分享！！！请检查你的分享文件")
            (con1, con2) = multiprocessing.Pipe()
            move = multiprocessing.Process(target=GUI.Move, args=(directorys, share_path, con1), daemon=True)
            move.start()

            def Share(T: multiprocessing.Process):
                try:
                    self.show_IP("请勿操作，等待中...")
                    self.Fuse = False
                    self.Huse = False
                    T.join(timeout=180)
                    self.Fuse = True
                    self.Huse = True
                    self.clear_IP()
                    if T.is_alive():
                        T.terminate()
                        T.join()
                        T.close()
                        raise Exception("文件太大啦~")
                    share_path = con2.recv()
                    con2.close()
                    self.ftp_share_path = share_path
                    if hasattr(self, "user") and hasattr(self, "passwd"):
                        self.ftpserver.start_server(self.ftp_share_path, self.user.get(), self.passwd.get(), port=int(self.Fport.get()))
                    else:
                        self.ftpserver.start_server(self.ftp_share_path, port=int(self.Fport.get()))

                    def check_server():
                        try:
                            with open(self.ftpserver.stream, "r") as f:
                                pipe = f.read()
                            pattern = re.compile(r"starting FTP server")
                            if not pattern.search(pipe) is None:
                                IP_info, port_info = self.ftpserver.getLocalIP()
                                if port_info == 21:
                                    self.show_IP(f"ftp://{IP_info}")
                                else:
                                    self.show_IP(f"ftp://{IP_info}:{port_info}")
                                return 0
                            raise Exception("启动失败！请尝试更换端口号")
                        except Exception as e:
                            self.clear_IP()
                            if hasattr(self, "ftp_share_path") and not self.ftp_share_path is None:
                                shutil.rmtree(self.ftp_share_path, ignore_errors=True)
                                self.ftp_share_path = None
                            if hasattr(self, "http_share_path") and not self.http_share_path is None and not self.httpprotocol.get() == "nocache":
                                shutil.rmtree(self.http_share_path, ignore_errors=True)
                                self.http_share_path = None
                            showerror("错误", str(e))

                    threading.Thread(target=check_server, daemon=True).start()
                except Exception as e:
                    self.clear_IP()
                    if hasattr(self, "ftp_share_path") and not self.ftp_share_path is None:
                        shutil.rmtree(self.ftp_share_path, ignore_errors=True)
                        self.ftp_share_path = None
                    if hasattr(self, "http_share_path") and not self.http_share_path is None and not self.httpprotocol.get() == "nocache":
                        shutil.rmtree(self.http_share_path, ignore_errors=True)
                        self.http_share_path = None
                    showerror("错误", str(e))

            share = threading.Thread(target=Share, args=(move,), daemon=True)
            share.start()

        except Exception as e:
            self.clear_IP()
            if hasattr(self, "ftp_share_path") and not self.ftp_share_path is None:
                shutil.rmtree(self.ftp_share_path, ignore_errors=True)
                self.ftp_share_path = None
            if hasattr(self, "http_share_path") and not self.http_share_path is None and not self.httpprotocol.get() == "nocache":
                shutil.rmtree(self.http_share_path, ignore_errors=True)
                self.http_share_path = None
            showerror("错误", str(e))

    @classmethod
    def preprocessing(cls, directorys, path, iszip=True):
        '''
        preprocess path
        :param directory:
        :return:
        '''
        perfect_dir = False
        share_path = path
        if not os.path.exists(share_path):
            os.makedirs(share_path)
        if iszip:
            for directory in directorys:
                result = Logic.judge_file_type(directory)
                if result[0] == Logic.PATH:
                    if result[1]:
                        perfect_dir = True
                        shutil.copytree(directory, os.path.join(share_path, os.path.basename(directory)))
                    else:
                        perfect_dir = False
                        Logic.zip_item(directory, os.path.join(share_path,
                                                               os.path.basename(directory).split(r".")[0] + ".zip"))
                elif result[0] == Logic.TEXT:
                    perfect_dir = False
                    Logic.zip_item(directory, os.path.join(share_path,
                                                           os.path.basename(directory).split(r".")[0] + ".zip"))
                elif result[0] == Logic.STREAM:
                    perfect_dir = False
                    shutil.copy(directory, share_path)
                elif result[0] == Logic.APP:
                    dir_name = "".join(random.sample(string.ascii_letters, 6))
                    temp_path = os.path.join(os.path.dirname(directory), dir_name)
                    shutil.copytree(directory, os.path.join(temp_path, os.path.basename(directory)))
                    Logic.zip_item(temp_path, os.path.join(share_path,
                                                           os.path.basename(directory).split(r".")[0] + ".zip"))
                    Logic.delete_dir(temp_path)
        else:
            GUI.Move(directorys, share_path)

    def http_drag(self, event):
        try:
            if self.Huse:
                global preprocessing
                self.clear_IP()
                self.httpserver.stop_server()
                self.ftpserver.stop_server()
                if hasattr(self, "Hdrag"):
                    self.Hdrag.configure(background="gray")
                if not self.http_share_path is None:
                    shutil.rmtree(self.http_share_path, ignore_errors=True)
                    self.http_share_path = None
                file_paths = GUI.get_all_path(event.data)
                self.clear_httpfile()

                dirname = "".join(random.sample(string.ascii_letters, 6))
                share_path = os.path.join(os.path.expanduser("~"), "Library")
                share_path = os.path.join(share_path, "FileServer")
                share_path = os.path.join(share_path, dirname)
                for path in file_paths:
                    self.show_httpfile(path)
                    if os.path.basename(share_path) in path or os.path.basename(path) in share_path:
                        print(share_path, path)
                        raise Exception("缓存文件不允许分享！！！请检查你的分享文件")

                if hasattr(self, "httpfileList") and hasattr(self, "httpprotocol"):
                    if self.httpprotocol.get() == "zip":
                        preprocessing = multiprocessing.Process(target=GUI.preprocessing,
                                                                args=(self.httpfileList.get("0", END), share_path, True), daemon=True)
                    elif self.httpprotocol.get() == "nozip":
                        preprocessing = multiprocessing.Process(target=GUI.preprocessing,
                                                                args=(self.httpfileList.get("0", END), share_path, False),
                                                                daemon=True)
                    else:
                        if len(file_paths)>1:
                            raise Exception("该模式不支持多文件分享！")
                        pattern = re.compile(r"\.")
                        if pattern.search(os.path.basename(file_paths[0])) is None:
                            share_path = file_paths[0]
                        else:
                            share_path = os.path.dirname(file_paths[0])
                        preprocessing = multiprocessing.Process(daemon=True)
                    preprocessing.start()

                def Share(T: multiprocessing.Process):
                    try:
                        self.show_IP("请勿操作，等待中...")
                        self.Huse = False
                        self.Fuse = False
                        T.join(180)
                        self.Huse = True
                        self.Fuse = True
                        self.clear_IP()
                        if T.is_alive():
                            T.terminate()
                            T.join()
                            T.close()
                            raise Exception("文件太大啦~")
                        for dir in file_paths:
                            if self.http_share_path is None and os.path.basename(dir) in share_path and not self.httpprotocol.get() == "nocache":
                                raise Exception("缓存文件不允许分享！！！请检查你的分享文件")
                        self.http_share_path = share_path
                        self.httpserver.start_server(self.http_share_path, port=int(self.Hport.get()))
                        with open(self.httpserver.stream, "r") as f:
                            pipe = f.read()
                        if self.httpprotocol.get() == "nocache":
                            self.http_share_path = None
                        pattern = re.compile(r"Serving HTTP on")
                        if not pattern.search(pipe) is None:
                            IP_info, port_info = self.httpserver.getLocalIP()
                            if port_info == 80:
                                self.show_IP(f"{IP_info}")
                            else:
                                self.show_IP(f"{IP_info}:{port_info}")
                            return 0
                        raise Exception("启动失败, 请尝试更换端口号")
                    except Exception as e:
                        self.clear_IP()
                        if hasattr(self, "ftp_share_path") and not self.ftp_share_path is None:
                            shutil.rmtree(self.ftp_share_path, ignore_errors=True)
                            self.ftp_share_path = None
                        if hasattr(self, "http_share_path") and not self.http_share_path is None and not self.httpprotocol.get() == "nocache":
                            shutil.rmtree(self.http_share_path, ignore_errors=True)
                            self.http_share_path = None
                        showerror("错误", str(e))

                share = threading.Thread(target=Share, args=(preprocessing,), daemon=True)
                share.start()
            else:
                showerror("错误", "请稍后操作")
                if hasattr(self, "Hdrag"):
                    self.Hdrag.configure(background="gray")
        except Exception as e:
            self.clear_IP()
            if hasattr(self, "ftp_share_path") and not self.ftp_share_path is None:
                shutil.rmtree(self.ftp_share_path, ignore_errors=True)
                self.ftp_share_path = None
            if hasattr(self, "http_share_path") and not self.http_share_path is None and not self.httpprotocol.get() == "nocache":
                shutil.rmtree(self.http_share_path, ignore_errors=True)
                self.http_share_path = None
            showerror("错误", str(e))