import zipfile, os, random, string
import shutil


def create_dir(path):
    '''
    create a random name in father path
    :param path: share path
    :return:
    '''
    while True:
        dir_name = "".join(random.sample(string.ascii_letters, 6))
        path = os.path.join(os.path.dirname(path), dir_name)
        if not os.path.exists(path):
            os.mkdir(path)
            return path


def delete_dir(path):
    '''
    delete random dir
    :param path: del path
    :return:
    '''
    shutil.rmtree(path, ignore_errors=True)


def zip_item(dirpath, targetpath):
    '''
    zip file or dir from dirpath to targetpath
    :param dirpath: file path
    :param targetpath: zip file path
    :return: zip is or not success
    '''
    file = os.path.basename(dirpath)
    try:
        with zipfile.ZipFile(targetpath, "a", zipfile.ZIP_DEFLATED) as zip:
            if os.path.isdir(dirpath):
                for path, dirnames, filenames in os.walk(dirpath):
                    for filename in filenames:
                        arcname = os.path.join(path.replace(dirpath, ""), filename)
                        zip.write(os.path.join(path, filename), arcname=arcname)
            else:
                zip.write(dirpath, arcname=file)
        return True
    except Exception as e:
        return False


PATH = 0
TEXT = 1
STREAM = 2
APP = 3


def judge_file_type(path):
    '''
    judge file type
    :param path: judge path
    :return:
    '''
    file_type = ['zip', 'rar', '7z', 'tar', 'doc', 'ppt', 'xls', 'docx', 'pptx', 'xlsx', 'msi', 'dll', 'sql', 'stl',
                 'dmg', 'pkg', 'exe', 'gz', 'command', 'sh']
    path = path.replace("\\", "/")
    if os.path.exists(path):
        if os.path.isdir(path):
            if path.split(r".")[-1] == "app":
                return [APP]
            for _, dirs, files in os.walk(path):
                for file in files:
                    if not file.split(r".")[-1] in file_type:
                        return [PATH, False]
            return [PATH, True]
        else:
            if path.split(r".")[-1] in file_type:
                return [STREAM]
            else:
                return [TEXT]
    else:
        print("文件不存在！！！")
        return [-1]
