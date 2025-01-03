import os
import time
import requests
import json
# import mysql.connector
import concurrent.futures
import pandas as pd

def split_dict(original_set, chunk_size):
    num_chunks = (len(original_set) + chunk_size - 1) // chunk_size
    split_sets = {}
    original_list = list(original_set)
    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(original_set))
        split_sets[f'bvid_{i + 1}'] = set(original_list[start:end])
    return split_sets

def download_subtitle_json(bvid: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': f'https://www.bilibili.com/video/{bvid}/?p=1',
        'Origin': 'https://www.bilibili.com',
        'Connection': 'keep-alive',
        'Cookie': "your_cookie_here",
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    resp = requests.get(f'https://www.bilibili.com/video/{bvid}/', headers=headers)
    text = resp.text
    aid = text[text.find('"aid"') + 6:]
    aid = aid[:aid.find(',')]
    cid_back = requests.get(f"http://api.bilibili.com/x/player/pagelist?bvid={bvid}", headers=headers)
    print(cid_back.status_code)
    # if cid_back.status_code != 200:
    #     print('Failed to get playlist')
    #     return

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
            print('Failed to get subtitle link')
            continue
        return wbi_resp.json()['data']["subtitle"]
        # subtitle_links = wbi_resp.json()['data']["subtitle"]['subtitles']
        # if subtitle_links:
        #     subtitle_url = "https:" + subtitle_links[0]['subtitle_url']
        #     subtitle_resp = requests.get(subtitle_url, headers=headers)
        #
        #     subtitle_dir = "subtitle"
        #     os.makedirs(subtitle_dir, exist_ok=True)
        #     subtitle_file = os.path.join(subtitle_dir, f"{bvid}.json")
        #     print(subtitle_file)
        #     with open(subtitle_file, 'w', encoding='utf-8') as f:
        #         f.write(subtitle_resp.text)

def fetch_bvids_from_db(db_config):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT bvid FROM Videos WHERE upload_date >= '2020-01-01'"
    cursor.execute(query)
    bvid_dict = {row[0] for row in cursor.fetchall()}
    cursor.close()
    connection.close()
    return bvid_dict

def fetch_bvid_through_pd(db_config):
    con = mysql.connector.connect(**db_config)
    df = pd.read_sql(sql='select bvid from videos', con=con)
    return df['bvid']



def batch_processing(bvid_dict):
    for bvid in bvid_dict:
        print(f"Processing video BVID: {bvid}")
        download_subtitle_json(bvid)
        print("Processing successful!")

db_config = {
    'user': 'root',
    'password': 'fcx240719',
    'host': 'localhost',
    'database': 'SNM_learning'
}

# bvid_dict = fetch_bvids_from_db(db_config)

# print(len(bvid_dict))

# bvid_list = list(bvid_dict)

# print(len(bvid_list))

# print(bvid_list[0:3])


#test = {'BV1hW4y1v7M7' , 'BV1s3411z7kW', 'BV17C411b7cc'}

#batch_processing(test)


# chunk_size = 1000
# split_bvids = split_dict(bvid_dict, chunk_size)

# split_bvids_list = [bvid_set for bvid_set in split_bvids.values()]

# print(len(split_bvids))

# for index, bvid_set in enumerate(split_bvids_list, start=1):
#     bvid_list = list(bvid_set)
#     first_three = bvid_list[:3]
#     last_three = bvid_list[-3:]
#     print(f"Chunk {index} size: {len(bvid_set)}")
#     print(f"First three elements: {first_three}")
#     print(f"Last three elements: {last_three}")


# def get_processed_bvids(subtitle_dir):
#     uids = []
#     for filename in os.listdir(subtitle_dir):
#         if filename.endswith('.json'):
#             bvid = filename[:-5]
#             uids.append(bvid)
#     return uids

# # Example usage
# subtitle_dir = '/Users/fuchenxu/Desktop/作业/社交网络挖掘/subtitle'
# processed_uids = get_processed_bvids(subtitle_dir)
# print(f"Processed UIDs: {len(processed_uids)}")

