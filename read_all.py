# -*- coding: utf-8 -*-
import os
import PyPDF2

folder = r"C:\Users\28054\Desktop\图\中文文献"
files = [f for f in os.listdir(folder) if f.endswith('.pdf')]

for filename in files:
    filepath = os.path.join(folder, filename)
    print(f"\n{'='*60}")
    print(f"文件: {filename}")
    print('='*60)
    try:
        reader = PyPDF2.PdfReader(open(filepath, 'rb'), strict=False)
        print(f'页数: {len(reader.pages)}')
        # 提取前3页
        for i, page in enumerate(reader.pages[:3]):
            text = page.extract_text()
            if text:
                print(f'\n--- 第{i+1}页 ---')
                lines = text.split('\n')[:50]  # 每页最多50行
                for line in lines:
                    if line.strip():
                        print(line)
    except Exception as e:
        print(f'读取错误: {e}')
