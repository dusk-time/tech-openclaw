# 工具调用与文献分析经验总结

## 2026-03-01 浅层地热能文献分析任务遇到的问题

### 一、文件读取问题

1. **中文路径编码问题**
   - PowerShell 和 Python 无法直接读取包含中文的路径（如 `C:\Users\28054\Desktop\能源底板 - 中文\data`）
   - 解决方法：先用 PowerShell 复制文件到无中文路径（如 `F:\OpenClawProjects\logistic_fit\`）再读取

2. **文件格式限制**
   - `read` 工具无法直接读取 `.docx` 和 `.pdf` 文件
   - 解决方法：
     - `.docx`: 使用 `python-docx` 库读取
     - `.pdf`: 使用 `PyMuPDF (fitz)` 或 `pypdf` 库读取
     - 或让用户直接粘贴文本内容

3. **路径不存在错误**
   - ENOENT 错误：文件路径确实不存在或编码问题导致找不到
   - 解决方法：先用 `glob.glob()` 或 `os.listdir()` 确认文件存在

### 二、数据理解错误

1. **误解读物内容**
   - 最初把文献数据文件当成发文量统计文件
   - 教训：必须先读取文件内容确认数据格式，不能假设

2. **统计数据错误**
   - 自己读取的文献数量与用户提供的统计数据不符
   - 原因：文件解析逻辑有误或遗漏部分文件
   - 教训：**以用户提供的官方统计数据为准**，自己读取的仅用于主题分析

### 三、编码问题

1. **Python print 中文编码错误**
   - Windows PowerShell 默认 GBK 编码，print 中文会报错
   - 错误示例：`UnicodeEncodeError: 'gbk' codec can't encode character`
   - 解决方法：
     ```python
     # 避免 print 中文，改用文件保存
     with open('output.txt', 'w', encoding='utf-8') as f:
         f.write(text)
     ```

2. **exec 命令输出乱码**
   - PowerShell 执行 Python 脚本输出中文显示为乱码
   - 解决方法：将输出写入文件后用 `read` 读取

### 四、分析错误

1. **照抄参考 PDF**
   - 最初撰写阶段演化分析时照抄了参考 PDF 的内容
   - 被用户指出后重新基于实际文献标题分析
   - 教训：**必须基于实际文献内容分析**，参考资料仅作为格式参考

2. **阶段划分不准确**
   - 最初阶段划分与用户要求不符
   - 用户明确要求：2001-2008、2009-2014、2015-2025 三阶段
   - 教训：**严格按照用户要求的阶段划分**

### 五、模块缺失问题

1. **PyMuPDF 未安装**
   - `ModuleNotFoundError: No module named 'fitz'`
   - 解决方法：使用 `pypdf` 替代，或让用户提供文本内容

2. **python-docx 路径问题**
   - 读取 `.docx` 文件时路径编码导致失败
   - 解决方法：复制到简单路径后读取

### 六、正确的工作流程

1. **数据确认**
   - ✅ 首先确认用户是否有官方统计数据
   - ✅ 以用户提供的数据为准，自己读取的仅用于主题分析

2. **文献分析**
   - ✅ 读取文献标题和关键词
   - ✅ 基于实际标题分析研究主题演变
   - ✅ 不照抄参考资料，独立分析

3. **文本输出**
   - ✅ 避免 print 中文，写入 UTF-8 文件
   - ✅ 用 `read` 工具读取文件内容展示给用户

4. **阶段划分**
   - ✅ 严格按照用户要求的阶段划分
   - ✅ 统计数据使用用户提供的准确数据

### 七、关键统计数据（最终确认）

| 年份 | 中文 | 英文 | CNKI 累计 | WOS 累计 |
|------|------|------|----------|----------|
| 2001-2008 | 37 篇 | 4 篇 | 37 | 4 |
| 2009-2014 | 109 篇 | 44 篇 | 146 | 48 |
| 2015-2025 | 366 篇 | 741 篇 | 505 | 789 |
| **总计** | **505 篇** | **789 篇** | **505** | **789** |

### 八、命令行 (exec) 调用问题

1. **PowerShell 管道符问题**
   - 错误：`dir "path" 2>&1` 在 PowerShell 中语法错误
   - 原因：PowerShell 不支持 `2>&1` 重定向语法（这是 bash 语法）
   - 正确做法：
     ```powershell
     # PowerShell 方式
     dir "path" 2>&1 | Select-Object -First 30
     # 或直接
     Get-ChildItem "path" -ErrorAction SilentlyContinue
     ```

2. **PowerShell 中文路径乱码**
   - 错误：`Get-ChildItem "C:\Users\28054\Desktop\能源底板 - 中文\data"` 显示为 `Դװ-`
   - 原因：PowerShell 控制台编码与路径编码不匹配
   - 解决方法：
     ```python
     # 使用 Python 的 os 模块，避免 PowerShell 路径问题
     import os
     files = os.listdir(r'路径')
     ```

3. **Python 脚本执行超时**
   - 问题：复杂脚本执行时间长，需要多次 poll
   - 解决方法：
     ```python
     # 脚本中避免 plt.show()，改用 plt.close()
     plt.savefig('output.png')
     plt.close()  # 不显示图形窗口
     ```

4. **命令行输出截断**
   - 问题：exec 输出超过一定长度被截断
   - 解决方法：写入文件后 read 读取

5. **bash 与 PowerShell 语法混用**
   - 错误：`cp file1 file2`（bash 语法）在 PowerShell 中无效
   - 正确：`Copy-Item file1 file2`（PowerShell 语法）
   - 错误：`rm file`（bash 语法）
   - 正确：`Remove-Item file` 或 `del file`

6. **Python 单行命令引号问题**
   - 错误：`python -c "import os; os.listdir('path')"` 引号嵌套错误
   - 解决方法：写成脚本文件执行，不用 -c 参数

7. **进程管理**
   - 问题：后台进程需要用 process 工具管理
   - 方法：
     ```
     exec 命令 (yieldMs=10000) → process(action=poll, sessionId=xxx, timeout=30000)
     ```

### 九、输出文件位置

- 最终 3.5 小节：`F:\OpenClawProjects\logistic_fit\stage_35_FINAL.txt`
- 文献分析：`F:\OpenClawProjects\logistic_fit\real_literature_analysis.txt`
- 统计数据：`F:\OpenClawProjects\logistic_fit\corrected_counts.txt`

---

**核心教训**：
1. 先确认数据格式，不要假设
2. 以用户提供的官方数据为准
3. 基于实际文献内容分析，不照抄
4. 避免中文 print，用文件输出
5. 严格按用户要求的阶段划分
6. PowerShell 不用 bash 语法（2>&1, cp, rm 等）
7. 复杂任务写脚本文件，不用 python -c
8. 图形保存用 plt.close() 不显示
