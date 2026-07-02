# src/core_logic.py
import os
import re


def ensure_history_dir():
    """确保 history 文件夹存在"""
    if not os.path.exists("history"):
        os.makedirs("history")


def generate_markdown_text(tree_widget):
    """【正向转换】将当前 RobustTreeWidget 的结构递归转化为标准的 Markdown 规格文本"""

    def recurse(item, indent=""):
        md_text = ""
        pure_name = item.data(1, 0x0100) or ""  # Qt.ItemDataRole.UserRole 为 0x0100
        desc = item.data(2, 0x0100) or ""
        is_folder = item.data(0, 0x0100) == "folder"

        formatted_name = f"{pure_name}/" if is_folder else pure_name
        comment = f" # 👉 {desc}" if desc else ""

        md_text += f"{indent}- {formatted_name}{comment}\n"

        for i in range(item.childCount()):
            md_text += recurse(item.child(i), indent + "  ")
        return md_text

    tree_content = ""
    for i in range(tree_widget.topLevelItemCount()):
        tree_content += recurse(tree_widget.topLevelItem(i))

    md_template = f"""# Project Architecture Blueprint

> 本文件规定了软件项目的目录、文件结构标准与设计职责。请 Codex 严格以此骨架为准绳进行代码编写、重构或逻辑重排。

## Directory Tree & Responsibilities

```text
{tree_content}```

---
*Generated via BMW Corporate Architecture Builder Component.*
"""
    return md_template


def parse_markdown_to_tree_data(md_content):
    """【反向读取】解析历史 MD 文件，精确提取其中的目录层级、节点类型与长注释说明"""
    # 使用正则表达式提取 ```text ... ``` 包裹的工程架构核心树部分
    match = re.search(r'```text\s*(.*?)\s*```', md_content, re.DOTALL)
    if not match:
        return []

    raw_lines = match.group(1).split('\n')
    tree_nodes = []

    for line in raw_lines:
        if not line.strip():
            continue

        # 根据前导空格计算当前节点的绝对缩进量，从而推导树的深度父子关系
        indent = len(line) - len(line.lstrip())
        content = line.strip().lstrip('- ').strip()

        desc = ""
        # 拆分出我们定义的特殊长注释标记 # 👉
        if " # 👉 " in content:
            content, desc = content.split(" # 👉 ", 1)

        is_folder = content.endswith('/')
        pure_name = content.rstrip('/')

        tree_nodes.append({
            'indent': indent,
            'name': pure_name,
            'desc': desc,
            'type': 'folder' if is_folder else 'file'
        })

    return tree_nodes