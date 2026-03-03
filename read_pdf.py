# -*- coding: utf-8 -*-
import PyPDF2
import sys
import io

pdf_path = sys.argv[1]
reader = PyPDF2.PdfReader(open(pdf_path, 'rb'))
print('页数:', len(reader.pages))
for i, page in enumerate(reader.pages[:5]):
    print(f'\n=== 第{i+1}页 ===')
    text = page.extract_text()
    if text:
        # 使用utf-8编码处理
        print(text[:3000])
    else:
        print('(无法提取文本)')
