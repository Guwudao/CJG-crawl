import requests
from bs4 import BeautifulSoup
import os


def sheju_crawl(info, index, download_list):
    header = "https://cjgtu.com"
    url = header + info[0]  # https://cjgtu.com/luyilu/2019/0723/7372.html

    if len(index) > 0:
        rindex = url.rindex("/")
        url = url[0:rindex] + "/" + index + ".html"

    print("current url ", url)
    resp = requests.get(url)
    # print(resp.text)
    # print("-" * 50)

    bs = BeautifulSoup(resp.text, "html.parser")
    # print(bs)
    # print(bs.find_all("img"))
    link_list = [header + img.get("src") for img in bs.find_all("img")]
    # print(link_list)

    temp_list = download_list + link_list

    li_tag_set = bs.find_all("li", attrs={"class": "next-page"})
    if len(li_tag_set) > 0:
        li_tag = li_tag_set[0]
        next_page = li_tag.a.get("href")
        print(next_page)

        if len(next_page) > 0:
            page_index = next_page.split(".")[0]
            sheju_crawl(info, page_index, temp_list)
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

        print("最后一页数据已加载完成")
        download_images(info[1], title, image_list)


def download_images(folder, title, url_list):
    if not os.path.exists(folder):
        os.mkdir(folder)

    n = 0
    for url in url_list:
        print(url)
        try:
            result = requests.get(url)
            file_name = title + str(n+1) + ".jpg"
            with open(f"{folder}/{file_name}", "wb") as f:
                f.write(result.content)
            n += 1
        except Exception as e:
            print("图片下载异常", e)

    print("——————————————————下载完成——————————————————")


def get_all_image_set():
    html_file = open("./target.html", 'r', encoding='utf-8').read()
    bs = BeautifulSoup(html_file, "html.parser")
    # print(bs)

    info_list = []
    for h2_tag in bs.find_all("h2"):
        # print(h2_tag)
        link = h2_tag.a.get("href")
        title = h2_tag.a.string
        # print("-" * 50)
        info_list.append((link, title))

    # print(info_list)
    for info in info_list:
        print(info)
        sheju_crawl(info, "", [])


get_all_image_set()
# sheju_crawl("9082", [])