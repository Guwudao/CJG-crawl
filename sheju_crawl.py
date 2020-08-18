import requests
import os
import threading
import urllib3
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.common import exceptions
urllib3.disable_warnings()


def cjg_crawl(info, index="", download_list=[]):
    header = "https://cjgtu.com"
    url = header + info[0]

    if len(index) > 0:
        rindex = url.rindex("/")
        url = url[0:rindex] + "/" + index + ".html"

    # print("current url ", url)
    try:
        resp = requests.get(url, timeout=120, verify=False)
        bs = BeautifulSoup(resp.text, "html.parser")
        # print(bs.find_all("img"))
        link_list = [header + img.get("src") for img in bs.find_all("img")]
        # print(link_list)

        temp_list = download_list + link_list

        li_tag_set = bs.find_all("li", attrs={"class": "next-page"})
        if len(li_tag_set) > 0:
            li_tag = li_tag_set[0]
            next_page = li_tag.a.get("href")
            # print(next_page)

            if len(next_page) > 0:
                page_index = next_page.split(".")[0]
                cjg_crawl(info, page_index, temp_list)
        else:
            origin_title_string = bs.title.string
            if "[" in origin_title_string:
                title_index = origin_title_string.index("[")
                title = bs.title.string[0:title_index]
            else:
                title = origin_title_string

            image_list = []

            for link in temp_list:
                suffix = link.split(".")[-1]
                if suffix != "gif":
                    image_list.append(link)

            print("{} 最后一页数据已加载完成".format(info[1]))
            download_images(info[1], title, image_list)

    except Exception as crawl_error:
        print("获取url超时：", crawl_error, info)


def download_images(folder, title, url_list):
    if not os.path.exists(folder):
        os.mkdir(folder)

    n = 0
    for url in url_list:
        file_name = title + str(n + 1) + ".jpg"
        print("%s" % threading.current_thread().name, folder, "-" * 5, url)

        try:
            result = requests.get(url, timeout=120, verify=False)
            with open(f"{folder}/{file_name}", "wb") as image_f:
                image_f.write(result.content)
            n += 1
        except Exception as download_error:
            t = (folder, url, file_name)
            exception_image_list.append(t)
            print(folder, url, "图片下载异常", download_error)

    complete_list.append(folder)
    print(divide_line.format(folder + "下载完成"))


def get_all_image_set(pool):
    info_list = []
    try:
        html_file = open("./target.html", 'r', encoding='utf-8').read()
        bs = BeautifulSoup(html_file, "html.parser")

        for h2_tag in bs.find_all("h2"):
            link = h2_tag.a.get("href")
            title = h2_tag.a.string
            info_list.append((link, title))
    except Exception as parse_error:
        print("target.html解析错误：", parse_error)
    else:
        # print(info_list)
        if len(info_list) > 0:
            for info in info_list:
                # print(info)
                pool.map(cjg_crawl, [info])
        else:
            print(divide_line.format("无下载内容，请检查target.html"))
            return


def exception_download(exception_list):
    print(divide_line.format("Exception download begin"))
    if len(exception_list) <= 0:
        return

    for image in exception_list:
        try:
            result = requests.get(image[1], timeout=180, verify=False)
            with open("./%s/%s" % (image[0], image[2]), "wb") as exception_f:
                exception_f.write(result.content)
        except Exception as exception_error:
            print("Exception download 异常信息：", exception_error, image)
    print(divide_line.format("Exception download complete"))


def auto_search(msg):
    try:
        driver = webdriver.Chrome()
        driver.get("https://cjgtu.com/index.php?s=sou")
        driver.find_element_by_class_name("form-control").send_keys(msg)
        driver.find_element_by_class_name("btn").click()
        driver.find_element_by_class_name("focus")
        content = driver.page_source
        # print(content)

        with open("target.html", "w") as f:
            f.write(content)

        print(divide_line.format("搜索内容加载完毕"))
    except exceptions.NoSuchElementException as e:
        print("无搜索结果，请手动往target.htm导入搜索结果html", e)
    except exceptions.WebDriverException as e:
        print("浏览器驱动错误，请手动往target.html导入搜索结果html。", e)
    except Exception as e:
        print("错误：", e)
    finally:
        driver.quit()


def result_handle():
    if len(complete_list) <= 0:
        print(divide_line.format("下载异常，请检查target.html文件内容"))
        exit(1)
    else:
        print("complete_list: ", complete_list, len(complete_list))

    if len(exception_image_list) > 0:
        print("exception_image_list: %s 张未下载完成" % (len(exception_image_list)), exception_image_list)
        exception_download(exception_image_list)
    else:
        print(divide_line.format("下载任务完成"))


def download_choose():
    download_type = input("是否手动下载下载模式[y/n]: ")

    if download_type == "y":
        print("请确保target.html已更新")
        with ThreadPoolExecutor(max_workers=15, thread_name_prefix="当前线程_") as thread_pool:
            print(divide_line.format("开始下载"))
            get_all_image_set(thread_pool)

    elif download_type == "n":
        message = input("请输入搜索内容：")
        threads = int(input("请输入线程数："))
        auto_search(message)

        with ThreadPoolExecutor(max_workers=threads, thread_name_prefix="当前线程_") as thread_pool:
            print(divide_line.format("开始下载"))
            get_all_image_set(thread_pool)
    else:
        print("输入有误，请重新输入！")
        download_choose()

if __name__ == '__main__':

    exception_image_list, complete_list = [], []
    divide_line = "———————————— {} ————————————"

    download_choose()
    result_handle()

    # debug mode
    # t = ('/luyilu/2020/0627/9062.html', '极品福利姬酒Joanna狼&猫无圣光套图[62P]')
    # cjg_crawl(t)
