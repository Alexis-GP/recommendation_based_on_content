import os
import time
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from get_data_from_db import split_bvid as bvid
import pandas as pd
import random

def download_subtitle_json(bvid: str):
    # 设置重试机制
    retry_strategy = Retry(
        total=5,  # 总共重试次数
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1  # 重试间隔时间的倍数
    )
    # proxy = get_proxy().get("proxy")
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("http://", adapter)
    http.mount("https://", adapter)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': f'https://www.bilibili.com/video/{bvid}/?p=1',
        'Origin': 'https://www.bilibili.com',
        'Connection': 'keep-alive',
        'Cookie': "buvid3=1F3F8087-761A-EC94-C010-FA288D019B9C38260infoc; b_nut=1714035538; CURRENT_FNVAL=4048; _uuid=1881063E9-C7AE-510510-3AFA-62396E8D9161041788infoc; buvid4=0A4F598F-3856-1F11-A702-13112BA30B9F42694-024042508-F5Nx4SbwUx%2FD%2BBclYSrKRw%3D%3D; rpdid=|(u~J~mmJkRR0J'u~uR|JllRJ; header_theme_version=CLOSE; enable_web_push=DISABLE; SESSDATA=195cc5e7%2C1744218386%2C77dbe%2Aa2CjDHBcmM8NsGCR_6jxU6pPJqSe_dDUdj3TRi4p7YyZnpXV9P2RHU7rk2RLEZkQKu79ESVjk0c1hPLVpVeFlXLXNmRXlRc0NlemZBd0JPaDNIOVJUV18tUzhWV0JyLTU4eVFNeG5LQU1YbTVBWm1wVFJ6TDFoYS1yU3o2WW03TVlidjFRUDExM1pnIIEC; bili_jct=50994d5b7fe7f9d69f33e88c63518ed3; DedeUserID=3461568392071967; DedeUserID__ckMd5=51715bd0eda8f7c8; home_feed_column=5; browser_resolution=1512-823; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjkyNDYzNjksImlhdCI6MTcyODk4NzEwOSwicGx0IjotMX0.2QnW-BgBVxxkGxlksbHlhs9x1HcD6tZkPV5naCN6Atc; bili_ticket_expires=1729246309; fingerprint=abc34a2fceacc2408071067414337a4b; buvid_fp_plain=undefined; bp_t_offset_3461568392071967=989106461185409024; buvid_fp=0b7d370de02e5af3ad085821c7e726ed; b_lsid=8810AC119_192985FDF7F; sid=7mb07x00",
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }

    try:
        resp = requests.get(f'https://www.bilibili.com/video/{bvid}/', headers=headers)
        resp.raise_for_status()  # 检查请求是否成功
        text = resp.text
        aid = text[text.find('"aid"') + 6:]
        aid = aid[:aid.find(',')]
        
        cid_back = requests.get(f"http://api.bilibili.com/x/player/pagelist?bvid={bvid}", headers=headers)
        cid_back.raise_for_status()  # 检查请求是否成功

        cid_json = json.loads(cid_back.content)
        for item in cid_json['data']:
            cid = item['cid']
            title = item['part'] + '.json'

            params = {
                'aid': aid,
                'cid': cid,
                'isGaiaAvoided': 'false',
                'web_location': '1315873',
                'w_rid': '364cdf378b75ef6a0cee77484ce29dbb',
                'wts': int(time.time()),
            }

            wbi_resp = requests.get('https://api.bilibili.com/x/player/wbi/v2', params=params, headers=headers)
            # wbi_resp = requests.get('https://api.bilibili.com/x/player/wbi/v2', params=params, headers=headers)
            wbi_resp.raise_for_status()  # 检查请求是否成功

            # print(wbi_resp.json())
            
            # Create the videos_info directory if it doesn't exist
            videos_info_dir = "videos_info"
            os.makedirs(videos_info_dir, exist_ok=True)
            video_info_file = os.path.join(videos_info_dir, f"{bvid}.json")

            with open(video_info_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps(wbi_resp.json()))
                print(f"Video info for {bvid} has been written to {video_info_file}")

            # 检查 'subtitle' 键是否存在
            subtitle_data = wbi_resp.json().get('data', {}).get('subtitle', {})
            if 'subtitles' in subtitle_data and subtitle_data['subtitles']:
                subtitle_url = "https:" + subtitle_data['subtitles'][0]['subtitle_url']
                subtitle_resp = http.get(subtitle_url, headers=headers)
                subtitle_resp.raise_for_status()  # 检查请求是否成功

                subtitle_dir = "subtitle"
                os.makedirs(subtitle_dir, exist_ok=True)
                subtitle_file = os.path.join(subtitle_dir, f"{bvid}.json")
                print(subtitle_file + "\n")
                with open(subtitle_file, 'w', encoding='utf-8') as f:
                    f.write(subtitle_resp.text)
            else:
                print(f"视频 {bvid} 没有字幕信息\n")

    except requests.exceptions.RequestException as e:
        print(f"请求过程中发生错误: {e}")
    except KeyError as e:
        print(f"KeyError: {e} - 无法找到 {bvid} 的字幕信息")
    except Exception as e:
        print(f"处理 {bvid} 时发生其他错误: {e}")

def processed_uid(subtitle_dir='subtitle'):
    list_1 = os.listdir(subtitle_dir)
    uid_list = [item.replace('.json', '') for item in list_1]
    print(len(uid_list))
    return uid_list

def batch_processing(bvid_dict, processed_uid):
    for bvid in bvid_dict:
        if bvid in processed_uid:
            continue  # 跳过当前已处理的BVID
        
        print(f"Processing video BVID: {bvid}")
        download_subtitle_json(bvid)
        # time.sleep(3)

# Randomly select BVIDs from bvid_1 to bvid_40 and process them
# print(bvid)

# for i in range(1, 41):
#     bvid_key = f'bvid_{i}'
#     print(bvid_key)

#     print(len(bvid.get(bvid_key)))
#     if bvid.get(bvid_key):
#         # Randomly select a few BVIDs from the list
#         selected_bvids = random.sample(bvid.get(bvid_key), min(3, len(bvid.get(bvid_key))))  # Adjust the number 3 as needed
#         for bviid in selected_bvids:
#             print(f"Randomly selected BVID: {bviid}")
#             download_subtitle_json(bviid)



# print(bvid.get('bvid_1'))

# batch_processing(bvid.get('bvid_1'))



processed_uid = processed_uid()

# 新增的循环，处理 bvid_1 到 bvid_10
for i in range(25, 41):
    bvid_key = f'bvid_{i}'
    print(f"Processing video BVID_list: {bvid_key} -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    batch_processing(bvid.get(bvid_key), processed_uid)
    time.sleep(random.uniform(2, 5))


# batch_processing(bvid.get('bvid_40'))
# 
# download_subtitle_json('BV11TBqY7EFa')


