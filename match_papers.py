# -*- coding: utf-8 -*-
import os
import PyPDF2
import sys

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

folder = r"C:\Users\28054\Desktop\图\中文文献"
files = [f for f in os.listdir(folder) if f.endswith('.pdf')]

print(f"找到 {len(files)} 个PDF文件\n")

# 定义论文中需要匹配的引用信息
target_papers = {
    "[2]": "双碳目标下我国能源结构转型思考",
    "[6]": "我国地源热泵技术研究现状与发展趋势", 
    "[10]": "CiteSpace知识图谱的方法论功能",
    "[11]": "我国储能创新研究的热点及未来发展趋势",
    "[17]": "CiteSpace科技文本挖掘及可视化"
}

# 文件名关键词映射
keyword_map = {
    "双碳目标": "[2]",
    "地源热泵": "[6]",
    "CiteSpace知识图谱": "[10]",
    "储能创新": "[11]",
    "CiteSpace科技文本": "[17]",
    "CiteSpace可视化": "[17]"
}

print("=" * 80)
print("查找论文中引用的文献：")
print("=" * 80)

for filename in sorted(files):
    matched_ref = None
    for kw, ref in keyword_map.items():
        if kw in filename:
            matched_ref = ref
            print(f"\n✓ {filename}")
            print(f"  可能对应: {ref}")
            break
    
    if not matched_ref:
        # 尝试提取文件前几行内容
        filepath = os.path.join(folder, filename)
        try:
            reader = PyPDF2.PdfReader(open(filepath, 'rb'), strict=False)
            if len(reader.pages) > 0:
                text = reader.pages[0].extract_text()
                if text:
                    for kw, ref in target_papers.items():
                        if kw in text:
                            print(f"\n✓ {filename}")
                            print(f"  包含内容: {kw}")
                            print(f"  可能对应: {ref}")
                            break
        except:
            pass

print("\n" + "=" * 80)
print("未匹配的文献（需要下载）：")
print("=" * 80)
for ref, title in target_papers.items():
    print(f"  {ref} {title}")
