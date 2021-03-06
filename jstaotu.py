import requests
import os
import threading
import urllib3
from bs4 import BeautifulSoup

divide_line = "—————————————————— {} ——————————————————"
exception_image_list, complete_list = [], []

def get_all_topics():
    # base_url = "http://www.jstaotu.com/"
    base_url = "http://js.jstaotu.com/nenmo.html"
    # base_url = "http://www.xsmeinv.com/xingshang/meinvpics/kunbang/1.html?nenmo"

    response = requests.get(base_url)
    response.encoding = "gb2312"

    bs = BeautifulSoup(response.text, "html.parser")
    all_titles = bs.find_all("div", class_="interestline")

    print(response.text)


def parse_html():
    link_list = []

    try:
        html_file = open("./target.html", 'r', encoding='utf-8').read()
        bs = BeautifulSoup(html_file, "html.parser")

        all_brands = bs.find_all("div", class_="interestline")

        for brand in all_brands:
            print(brand.b.string)
            brand_all_hrefs = brand.find_all("a")
            for href in brand_all_hrefs:
                # print(href.get("href"), href.string)
                link_list.append(str(href.string))
                link_list.append(str(href.get("href")))
                link_list.append("\n")

            # print(brand_all_hrefs)
            link_list.append("-" * 50)
            link_list.append("\n")
            print("-" * 50)

        # print(type(link_list))
    except Exception as parse_error:
        print("target.html解析错误：", parse_error)


def fetch_all_list_for_special_topic() -> []:
    url = "http://www.gqxzt.com/gaoqingr/qingzxies/xinyanxiaogongzhu/1.html"
    resp = requests.get(url)
    resp.encoding = "gb2312"
    bs = BeautifulSoup(resp.text, "html.parser")

    page_list = []
    page_list.append(url)
    page_a_list = bs.find_all("div", class_="pagelist")[0].find_all("a")
    # print(page_a_list)

    url_prefix = url.rsplit("/", 1)[0]
    for a_tag in page_a_list:
        href = a_tag.get("href")
        if href not in page_list:
            full_url = os.path.join(url_prefix, href)
            page_list.append(full_url)

    print(page_list)
    return page_list


def fetch_all_album_in_page() -> []:
    url = "http://www.gqxzt.com/gaoqingr/qingzxies/xinyanxiaogongzhu/1.html"
    resp = requests.get(url)
    resp.encoding = "gb2312"
    bs = BeautifulSoup(resp.text, "html.parser")

    album_list = bs.select("#list")[0].find_all("li")

    host = urllib3.get_host(url)[0] + "://" + urllib3.get_host(url)[1]
    print(f"host: {host}")

    album_info_list = []
    for album in album_list:
        title = album.a.get("title")
        link = host + album.a.get("href")
        album_info_list.append((title, link))

    print(album_info_list)
    return album_info_list


def fetch_all_image_in_album():
    url = "http://www.gqxzt.com/gaoqingr/qingzxie/20211021/111735.html"
    resp = requests.get(url)
    resp.encoding = "gb2312"
    bs = BeautifulSoup(resp.text, "html.parser")
    all_pages_count = bs.find_all("div", class_="page")[0].find_all("a")

    image_page_list = []
    url_prefix = url.rsplit("/", 1)[0]
    for count in all_pages_count:
        href = count.get("href")
        link = url_prefix + "/" + href
        if link not in image_page_list:
            image_page_list.append(link)

    print(image_page_list)
    print(bs.find_all("img"))


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


if __name__ == '__main__':
    # fetch_all_list_for_special_topic()
    # fetch_all_album_in_page()
    fetch_all_image_in_album()
