import requests
from bs4 import BeautifulSoup

image_list = []
title = ""

def sheju_crawl(index):
    header = "https://cjgtu.com"
    url = "https://cjgtu.com/luyilu/2020/0702/{}.html".format(index)

    resp = requests.get(url)
    # print(resp.text)
    # print("-" * 50)

    bs = BeautifulSoup(resp.text, "html.parser")
    # print(bs)


    # print(bs.find_all("img"))
    link_list = [header + img.get("src") for img in bs.find_all("img")]
    # print(link_list)
    # print(image_list.append(link_list))

    global image_list
    image_list = image_list + link_list
    # print("image_list: {}".format(image_list))

    if len(bs.find_all("li", attrs={"class": "next-page"})) > 0:
        li_tag = bs.find_all("li", attrs={"class": "next-page"})[0]
        next_page = li_tag.a.get("href")
        print(next_page)

        if len(next_page) > 0:
            page_index = next_page.split(".")[0]
            sheju_crawl(page_index)
    else:
        global title
        title_index = bs.title.string.index("[")
        title = bs.title.string[0:title_index]
        print("最后一页已加载完成")
        download_images(title)


def download_images(title):
    n = 0
    for url in image_list:
        print(n)
        print(url)
        result = requests.get(url)

        with open((title + str(n+1) + ".jpg"), "wb") as f:
            f.write(result.content)
        n += 1

    print("——————————————————下载完成——————————————————")


sheju_crawl("9077")

# print(image_list)
# print(title)