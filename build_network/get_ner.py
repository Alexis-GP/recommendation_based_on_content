import pandas as pd
import numpy as np
import sqlite3
import ast
from tqdm import tqdm
from datetime import datetime

from build_network import io
from build_network import config as cfg
import hanlp


ner = hanlp.load(hanlp.pretrained.ner.MSRA_NER_ELECTRA_SMALL_ZH)
print('ner loaded')

con = sqlite3.connect(cfg.FILE['subtitle_cut'])
bvids = con.execute(f'select bvid from video_filter where {cfg.vid_filter['rule1']}').fetchall()
bvids = [i[0] for i in bvids if i[0] not in ('BV11L411J7hp',)]
# bvids[:10]



print(len(bvids))
# print(bvids[445:448])

subtitle_df = io.NerLoader(ner)
n, k = 0, 0
for bvid in tqdm(bvids[431:]):
    try:
        # test_list.append(bvid)
        subtitle_df.do_ner(id_=bvid,)
        # print(bvid)
    except Exception as e:
        print(e, datetime.now())
    else:
        n += 1
    # print(subtitle_df, test_list)

    if n == 20:
        subtitle_df.save_sql3(name='subtitle_cut_ner')
        # print(subtitle_df)
        subtitle_df.dump_()
        n = 0
        k += 1

    # if k == 6:
    #     k = 0
    #     print(datetime.datetime.now(), '120 items done')
    #
# subtitle_df.do_ner_2()