import requests
from bs4 import BeautifulSoup
import os
import threading
from concurrent.futures import ThreadPoolExecutor


def cjg_crawl(info, index="", download_list=[]):
    header = "https://cjgtu.com"
    url = header + info[0]

    if len(index) > 0:
        rindex = url.rindex("/")
        url = url[0:rindex] + "/" + index + ".html"

    # print("current url ", url)
    try:
        resp = requests.get(url, timeout=120)
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

    except Exception as e:
        print("获取url超时：", e, info)


def download_images(folder, title, url_list):
    if not os.path.exists(folder):
        os.mkdir(folder)

    n = 0

    for url in url_list:
        file_name = title + str(n + 1) + ".jpg"
        print("%s"%(threading.current_thread().name), folder, "-"* 5, url)
        try:
            result = requests.get(url, timeout=120)
            with open(f"{folder}/{file_name}", "wb") as f:
                f.write(result.content)
            n += 1
        except Exception as e:
            t = (folder, url, file_name)
            exception_image_list.append(t)
            print(folder, url, "图片下载异常", e)

    complete_list.append(folder)
    print("——————————————————{} 下载完成——————————————————".format(folder))


def get_all_image_set(pool):
    html_file = open("./target.html", 'r', encoding='utf-8').read()
    bs = BeautifulSoup(html_file, "html.parser")

    info_list = []
    for h2_tag in bs.find_all("h2"):
        # print(h2_tag)
        link = h2_tag.a.get("href")
        title = h2_tag.a.string
        info_list.append((link, title))

    # print(info_list)
    for info in info_list:
        # print(info)
        pool.map(cjg_crawl, [info])


def exception_download(exception_image_list):
    print("———————————— exception download begin ————————————")
    if len(exception_image_list) <= 0:
        return

    for image in exception_image_list:
        try:
            result = requests.get(image[1], timeout=180)
            with open("./%s/%s"%(image[0], image[2]), "wb") as f:
                f.write(result.content)
        except Exception as e:
            print("Exception download 异常信息：", e, image)
    print("———————————— exception download complete ————————————")


if __name__ == '__main__':

    exception_image_list, complete_list = [], []

    with ThreadPoolExecutor(max_workers=15, thread_name_prefix="当前线程_") as pool:
        get_all_image_set(pool)


    # t = ('/luyilu/2020/0725/9127_2.html', '某群美胸比赛无圣光套图[58P]')
    # cjg_crawl(t)

    print("exception_image_list: %s 张未下载完成" % (len(exception_image_list)), exception_image_list)
    print("complete_list: ", complete_list)

    if len(exception_image_list) > 0:
        exception_download(exception_image_list)
    else:
        print("——————————————————下载任务完成——————————————————")
