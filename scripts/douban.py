
import json
import os
import csv
import argparse
import json
import os
from retrying import retry
import requests




image_save_folder = 'static/images/douban/'

# 如果是 CSV 文件使用下面这一行
csv_movie_path = 'data/douban/movie.csv'
csv_book_path = 'data/douban/book.csv'

DOUBAN_API_HOST = os.getenv("DOUBAN_API_HOST", "frodo.douban.com")
DOUBAN_API_KEY = os.getenv("DOUBAN_API_KEY", "0ac44ae016490db2204ce0a042db2916")

movie_status = {
    # "mark": "想看",
    # "doing": "在看",
    "done": "看过",
}
book_status = {
    # "mark": "想读",
    # "doing": "在读",
    "done": "读过",
}
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

headers = {
    "host": DOUBAN_API_HOST,
    "authorization": f"Bearer {AUTH_TOKEN}" if AUTH_TOKEN else "",
    "user-agent": "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.16(0x18001023) NetType/WIFI Language/zh_CN",
    "referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html",
}


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def fetch_subjects(user, type_, status):
    offset = 0
    page = 0
    url = f"https://{DOUBAN_API_HOST}/api/v2/user/{user}/interests"
    total = 0
    results = []
    while True:
        params = {
            "type": type_,
            "count": 50,
            "status": status,
            "start": offset,
            "apiKey": DOUBAN_API_KEY,
        }
        response = requests.get(url, headers=headers, params=params)

        if response.ok:
            response = response.json()
            interests = response.get("interests")
            if len(interests) == 0:
                break
            results.extend(interests)
            print(f"total = {total}")
            print(f"size = {len(results)}")
            page += 1
            offset = page * 50
    return results

def downloadImgs(image_url,id):
    # 确保文件夹路径存在
    os.makedirs(image_save_folder, exist_ok=True)
    if image_url.startswith("https://") and "dou.img.lithub.cc" in image_url:
        headers = {
            'Host': 'dou.img.lithub.cc',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    else:
        headers = {
            'referer': 'https://movie.douban.com/'
        }
    file_name = "{id}.jpg".format(id = id)
    save_path = os.path.join(image_save_folder, file_name)
    if os.path.exists(save_path):
        print(f'id = {id},文件已存在 {file_name}')
    else:
        print('文件不存在')
        with open(save_path, 'wb') as file:
            response = requests.get(image_url, headers=headers, timeout=300)
            if response.status_code == 200:
                file.write(response.content)
                print(f'id = {id},图片已保存为 {file_name}')
            else :
                if response.status_code == 403:
                    print("403 error!")





def insert_movie():
    results = []
    for i in movie_status.keys():
        results.extend(fetch_subjects(douban_name, "movie", i))
    # 确保文件的父目录存在
    os.makedirs(os.path.dirname(csv_movie_path), exist_ok=True)

    # 检查文件是否存在
    if not os.path.exists(csv_movie_path):
        # 文件不存在时，创建文件
        open(csv_movie_path, 'w').close()  # 创建一个空文件
        print("File created.")
    with open(csv_movie_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["d", "title", "intro", "poster", "pubdate", "url", "rating", "genres", "star", "comment", "tags",
             "star_time", "card"])

        # Iterate over each JSON object in the array
        for item in results:
            # 下载图片文件
            downloadImgs(item["subject"]["pic"]["large"],item["id"])
            writer.writerow([
                item["id"],
                item["subject"]["title"],
                item["comment"],
                item["subject"]["pic"]["large"],
                item["subject"]["pubdate"][0] if item["subject"]["pubdate"] else "",
                item["subject"]["url"],
                item["subject"]["rating"]["value"] if "rating" in item["subject"] and item["subject"]["rating"] else "",
                ",".join(item["subject"]["genres"]),
                item["subject"]["rating"]["star_count"] if "rating" in item["subject"] and item["subject"][
                    "rating"] else "",
                item["comment"],
                "",  # Assuming tags are empty
                item["create_time"],
                item["subject"]["card_subtitle"]
            ])

#             获取所有豆瓣标记的图书
def insert_books():
    results = []
    for i in book_status.keys():
        results.extend(fetch_subjects(douban_name, "book", i))
    # 确保文件的父目录存在
    os.makedirs(os.path.dirname(csv_book_path), exist_ok=True)

    # 检查文件是否存在
    if not os.path.exists(csv_book_path):
        # 文件不存在时，创建文件
        open(csv_book_path, 'w').close()  # 创建一个空文件
        print("File created.")
    with open(csv_book_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["d", "title", "intro", "poster", "pubdate", "url", "rating", "press", "star", "comment", "tags",
             "star_time", "author"])

        # Iterate over each JSON object in the array
        for item in results:
            # 下载图片文件
            downloadImgs(item["subject"]["pic"]["large"], item["id"])
            writer.writerow([
                item["id"],
                item["subject"]["title"],
                item["comment"],
                item["subject"]["pic"]["large"],
                item["subject"]["pubdate"][0] if item["subject"]["pubdate"] else "",
                item["subject"]["url"],
                item["subject"]["rating"]["value"] if "rating" in item["subject"] and item["subject"]["rating"] else "",
                ",".join(item["subject"]["press"]),
                item["subject"]["rating"]["star_count"] if "rating" in item["subject"] and item["subject"][
                    "rating"] else "",
                item["comment"],
                "",  # Assuming tags are empty
                item["create_time"],
                item.get("author","")
            ])




if __name__ == "__main__":

    # douban_name = "137124245"
    douban_name = "73961556"
    insert_movie()
    insert_books()
    # else:
    #     insert_book()


