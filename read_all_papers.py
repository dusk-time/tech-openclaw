# -*- coding: utf-8 -*-
import os
import PyPDF2

folder = r"C:\Users\28054\Desktop\图\中文文献"
files = [f for f in os.listdir(folder) if f.endswith('.pdf')]

print(f"找到 {len(files)} 个PDF文件\n")
print("=" * 80)

for i, filename in enumerate(sorted(files), 1):
    filepath = os.path.join(folder, filename)
    print(f"\n[{i}] {filename}")
    print("-" * 60)
    try:
        reader = PyPDF2.PdfReader(open(filepath, 'rb'), strict=False)
        # 提取前2页
        for page_num in range(min(2, len(reader.pages))):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text:
                # 提取标题行（通常在前几行）
                lines = text.split('\n')[:20]
                for line in lines:
                    line = line.strip()
                    if line and len(line) < 100:
                        # 查找题目、作者、期刊等信息
                        keywords = ['题目', '标题', '作者', '期刊', '摘要', '关键词', 
                                   '研究', '现状', '趋势', '发展', '地源热泵', 'CiteSpace',
                                   '建筑节能', '热力发电', '储能']
                        if any(kw in line for kw in keywords):
                            print(f"  {line}")
                break  # 只处理第一页的关键信息
    except Exception as e:
        print(f"  读取错误: {e}")
