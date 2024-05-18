from time import sleep
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json

# 常量
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
MAOYAN_BASE_URL = 'https://m.maoyan.com/mmdb/comments/movie/{id}.json?_v_=yes&offset={offset}'
DOUBAN_BASE_URL = 'https://movie.douban.com/subject/{id}/comments?start={start_idx}&limit=20&status=P&sort=new_score'

def get_maoyan_comments(movie_id, offset=0):
    url = MAOYAN_BASE_URL.format(id=movie_id, offset=offset)
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        return pd.DataFrame(), False

    try:
        ans = response.json()
    except ValueError:
        print("解析JSON失败")
        return pd.DataFrame(), False

    if ans.get("total", 0) == 0:
        return pd.DataFrame(), False

    cmts = ans.get("cmts", [])
    data = [{'用户名': cmt.get('nickName', '未知'),
            '评分': cmt.get('score', '无评分'),
            '评论内容': cmt.get('content', ''),
            "地区": cmt.get('cityName', '未知'),
            "时间": cmt.get('startTime', '未知')} for cmt in cmts]
    return pd.DataFrame(data), True


def get_douban_comments(movie_id, start_idx=0, cookies=None):
    url = DOUBAN_BASE_URL.format(id=movie_id, start_idx=start_idx)
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser')
    comments = soup.find_all(class_='comment')

    data = []
    for comment in comments:
        username = comment.find(class_='comment-info').find('a').text.strip()
        publish_time = comment.find(class_='comment-info').find(
            'span', class_='comment-time').text.strip() if comment.find(
                class_='comment-time') else "未知"
        loca = comment.find(class_='comment-info').find(
            'span', class_='comment-location').text.strip() if comment.find(
                class_='comment-location') else "未知"
        rating = comment.find(class_='comment-info').find(
            'span', class_='rating').get('title') if comment.find(
                class_='rating') else "无评分"
        content = comment.find(class_='short').text.strip()
        rating_map = {
            '力荐': 5,
            '推荐': 4,
            '还行': 3,
            '较差': 2,
            '很差': 1,
            '无评分': 0
        }
        rating = rating_map.get(rating, 0)
        data.append({
            '用户名': username,
            '评分': rating,
            '评论内容': content,
            "地区": loca,
            "时间": publish_time
        })

    return pd.DataFrame(data), len(data) != 0

def save_comments_to_excel(data, start_index, end_index, platform,save_dir,movie_id):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    filename = os.path.join(save_dir, f"{platform}_{movie_id}_第{start_index}条到第{end_index}条评论.xlsx")
    data.to_excel(filename, index=False)
    print(f"已保存评论至 {filename}")


def get_all_comments(movie_id,
                     platform='maoyan',
                     cookies=None,
                     start_idx=0,
                     batch_size=10,
                     step=20,
                     save_dir='tmp'):
    has_next = True
    all_data = []
    batch_count = 0

    while has_next:
        if platform == 'maoyan':
            print(f"正在爬取第{start_idx}条到第{start_idx + step}条评论...")
            comments, has_next = get_maoyan_comments(movie_id, start_idx)
        elif platform == 'douban':
            print(f"正在爬取第{start_idx + 1}条至第{start_idx + 20}条评论...")
            comments, has_next = get_douban_comments(movie_id, start_idx,
                                                     cookies)


        all_data.append(comments)
        start_idx += step

        if len(all_data) >= batch_size or not has_next:
            combined_data = pd.concat(all_data, ignore_index=True)
            save_comments_to_excel(combined_data,
                                   start_idx - len(all_data) * step,
                                   start_idx,
                                   platform,
                                   save_dir=save_dir,
                                   movie_id=movie_id)
            all_data.clear()
            batch_count += 1

        print("爬取完成, 为避免被视为恶意脚本, 休息0.1秒")
        sleep(0.1)
        print("休息完毕，开始下一轮爬取...")
