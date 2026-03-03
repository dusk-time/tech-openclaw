# -*- coding: utf-8 -*-
import os

skills_path = r'C:\Users\28054\AppData\Roaming\npm\node_modules\openclaw\skills'

print('=' * 70)
print('OpenClaw Skill 功能列表')
print('=' * 70)

items = os.listdir(skills_path)
skills_info = []

for item in sorted(items):
    item_path = os.path.join(skills_path, item)
    if not os.path.isdir(item_path):
        continue
    
    skill_file = os.path.join(item_path, 'SKILL.md')
    description = '未知功能'
    
    if os.path.exists(skill_file):
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n')[:20]:
                    if 'description' in line.lower() and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            desc = parts[1].strip()
                            desc = desc.strip('"').strip("'").strip('"')
                            if desc and len(desc) < 80:
                                description = desc
                                break
        except:
            description = '读取失败'
    
    skills_info.append((item, description))

for i, (name, desc) in enumerate(skills_info, 1):
    print(f'{i:2}. {name:25} - {desc}')

print()
print('=' * 70)
print(f'总计: {len(skills_info)} 个Skill')
