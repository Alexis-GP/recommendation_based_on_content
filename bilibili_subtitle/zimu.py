"""下载哔哩哔哩 字幕
"""
import math
import os
import time
import requests
import json
 
 
 
def download_subtitle_json(bvid: str):
    """
    下载字幕
    """
    sub_dir = f'./{bvid}'
    if not os.path.isdir(sub_dir):
        os.mkdir(f'./{bvid}')
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
    resp = requests.get(f'https://www.bilibili.com/video/{bvid}/', headers=headers)
    text = resp.text
    aid = text[text.find('"aid"') + 6:]
    aid = aid[:aid.find(',')]
    cid_back = requests.get("http://api.bilibili.com/x/player/pagelist?bvid={}".format(bvid), headers=headers)
    if cid_back.status_code != 200:
        print('获取 playlist 失败')
 
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
        if wbi_resp.status_code != 200:
            print('获取 字幕链接 失败')
        subtitle_links = wbi_resp.json()['data']["subtitle"]['subtitles']
        if subtitle_links:
            # 默认下载第一个字幕
            subtitle_url = "https:" + subtitle_links[0]['subtitle_url']
            subtitle_resp = requests.get(subtitle_url, headers=headers)
            open(os.path.join(sub_dir, title), 'w', encoding='utf-8').write(subtitle_resp.text)
 
 
if __name__ == '__main__':
    BVID = 'BV1sHx9eUEVY'
    download_subtitle_json(BVID)
