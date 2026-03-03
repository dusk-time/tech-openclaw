# -*- coding: utf-8 -*-
import os
import glob

folder = r'C:\Users\28054\Desktop\图\中文文献'
files = glob.glob(os.path.join(folder, '*.pdf'))

print(f"找到 {len(files)} 个PDF文件:\n")

for i, f in enumerate(sorted(files), 1):
    name = os.path.basename(f)
    # 尝试用不同编码
    try:
        name_gbk = name.encode('latin1').decode('gbk')
    except:
        name_gbk = name
    print(f"{i}. {name_gbk}")
