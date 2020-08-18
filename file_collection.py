import os
import shutil

def file_rename(file_list, dir):
    for file in file_list:
        global n
        n += 1
        old_name = path + "/" + dir + "/" + file
        print(old_name)

        new_name = path + "/" + dir + "/" + str(n) + ".jpg"
        print(new_name)

        print("-" * 50)
        os.rename(old_name, new_name)

def file_traversal(dir_name, path):

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    dir_list = os.listdir(path)


    for dir in dir_list:
        if os.path.isdir(dir) and "." not in dir:
            # print(dir)
            file_list = os.listdir(dir)

            # file_rename(file_list, dir)

            for file in file_list:
                old = path + "/" + dir + "/" + file
                new = path + "/" + dir_name
                print(old, new)
                shutil.move(old, new)



if __name__ == '__main__':

    dir_name = input("文件夹名称：")
    path = os.getcwd()

    n = 0
    file_traversal(dir_name, path)