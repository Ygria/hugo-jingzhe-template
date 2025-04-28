import json
import os
import sys
from retrying import retry
import requests
import ffmpeg

image_save_folder = 'static/images/douban/'

json_movie_path = 'data/douban/movie.json'
json_book_path = 'data/douban/book.json'

DOUBAN_API_HOST = os.getenv("DOUBAN_API_HOST", "frodo.douban.com")
DOUBAN_API_KEY = os.getenv("DOUBAN_API_KEY", "0ac44ae016490db2204ce0a042db2916")

movie_status = {
    "mark": "想看",
    "doing": "在看",
    "done": "看过",
}
book_status = {
    "mark": "想读",
    "doing": "在读",
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


def download_and_convert_image(image_url, id):
    # 确保文件夹路径存在
    os.makedirs(image_save_folder, exist_ok=True)
    
    # 原始下载的图片路径
    file_name = f"{id}.jpg"
    save_path = os.path.join(image_save_folder, file_name)

    # 转换为AVIF的保存路径
    avif_file_name = f"{id}.avif"
    avif_save_path = os.path.join(image_save_folder, avif_file_name)
    
    headers = {
        'referer': 'https://movie.douban.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    
    if os.path.exists(avif_save_path):
        print(f'id = {id}, AVIF 文件已存在 {avif_file_name}')
        return
    
    print('文件不存在，正在下载...')
    try:
        response = requests.get(image_url, headers=headers, timeout=300)
        response.raise_for_status()  # 检查响应是否成功，如果不是200，则会抛出异常
    except requests.exceptions.RequestException as err:
        print(f"下载失败: {err}")
        return

    with open(save_path, 'wb') as file:
        file.write(response.content)
        print(f'下载完成: {file_name}')

    # 使用 ffmpeg 将图片转换为 avif 格式
    try:
        stream = ffmpeg.input(save_path)
        stream = ffmpeg.output(stream, avif_save_path, vcodec='libavif')
        ffmpeg.run(stream)
        print(f'图片已转换为 AVIF 格式: {avif_file_name}')
    except ffmpeg.Error as e:
        print(f'转换失败: {e}')
    finally:
        # 删除临时的 JPG 文件（如果需要的话）
        if os.path.exists(save_path):
            os.remove(save_path)
            print(f'删除临时文件: {file_name}')


def insert_movie():
    results = []
    for i in movie_status.keys():
        results.extend(fetch_subjects(douban_name, "movie", i))
    # 确保文件的父目录存在
    os.makedirs(os.path.dirname(json_movie_path), exist_ok=True)

    # 检查文件是否存在
    if not os.path.exists(json_movie_path):
        # 文件不存在时，创建文件
        open(json_movie_path, 'w').close()  # 创建一个空文件
        print("File created.")
    json_data = []
    for item in results:
        # 下载并转换图片文件
        download_and_convert_image(item["subject"]["pic"]["large"], item["id"])
        # 准备要追加的数据
        new_data = {"subject_id": item["id"], "name": item["subject"]["title"],
                    "poster": item["subject"]["pic"]["large"], "card_subtitle": item["subject"]["card_subtitle"],
                    "pubdate": item["subject"]["pubdate"][0] if item["subject"]["pubdate"] else "",
                    "douban_score": item["subject"]["rating"]["value"] if "rating" in item["subject"] and
                                                                          item["subject"][
                                                                              "rating"] else "",
                    "comment": item["comment"], "create_time": item["create_time"],
                    "genres": ",".join(item["subject"]["genres"]),
                    "year": item["subject"]["year"],
                    "status": item["status"],
                    "my_rating": item["rating"]
                    }
        json_data.append(new_data)

    with open(json_movie_path, mode='w', newline='', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)


def insert_books():
    results = []
    for i in book_status.keys():
        results.extend(fetch_subjects(douban_name, "book", i))
    # 确保文件的父目录存在
    os.makedirs(os.path.dirname(json_book_path), exist_ok=True)

    # 检查文件是否存在
    if not os.path.exists(json_book_path):
        # 文件不存在时，创建文件
        open(json_book_path, 'w').close()  # 创建一个空文件
        print("File created.")
    json_data = []
    for item in results:
        # 下载并转换图片文件
        download_and_convert_image(item["subject"]["pic"]["large"], item["id"])
        # 准备要追加的数据
        new_data = {"subject_id": item["id"], "name": item["subject"]["title"],
                    "poster": item["subject"]["pic"]["large"], "card_subtitle": item["subject"]["card_subtitle"],
                    "pubdate": item["subject"]["pubdate"][0] if item["subject"]["pubdate"] else "",
                    "douban_score": item["subject"]["rating"]["value"] if "rating" in item["subject"] and
                                                                          item["subject"][
                                                                              "rating"] else "",
                    "comment": item["comment"], "create_time": item["create_time"],
                    "status": item["status"],
                    "my_rating": item["rating"],
                    "author": item.get("author", ""),
                    "book_subtitle": item.get("subject", {}).get("book_subtitle", ""),
                    "press": item["subject"]["press"],
                    "link_url": item["subject"]["url"],
                    "link_uri": item["subject"]["uri"],
                    "intro": item["subject"]["intro"]
                    }
        json_data.append(new_data)
    with open(json_book_path, mode='w', newline='', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":

    douban_name = os.getenv('DOUBAN_NAME')
    if not douban_name:
        print('Douban name is not set')
        sys.exit(1)
    else:
        print(f"DOUBAN_NAME = {douban_name}")    
    insert_movie()
    insert_books()
