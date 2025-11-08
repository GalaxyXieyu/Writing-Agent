from bs4 import BeautifulSoup
import json
import re
def html_to_structured_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    def parse_section(element, level):
        section = {"title": "", "content": "", "subsections": []}
        
        # element 本身就是 h 标签
        section["title"] = element.text.strip()
        
        # Process content and subsections
        current = element.next_sibling
        while current:
            if isinstance(current, str):
                current = current.next_sibling
                continue
            if current.name and current.name.startswith('h'):
                # 检查是否是同级或更高级别的标题
                current_level = int(current.name[1])
                if current_level <= level:
                    break
                elif current_level == level + 1:
                    subsection = parse_section(current, current_level)
                    section["subsections"].append(subsection)
            elif current.name == 'p':
                section["content"] += current.text.strip() + "\n"
            current = current.next_sibling
        
        return section
    
    structured_data = []
    # 首先尝试查找 h1 标签，如果没有则查找 h2 标签
    h_tags = soup.find_all('h1')
    if not h_tags:
        h_tags = soup.find_all('h2')
        level = 2
    else:
        level = 1
    
    for h_tag in h_tags:
        structured_data.append(parse_section(h_tag, level))
    
    return json.dumps(structured_data, ensure_ascii=False, indent=2)

def markdown_to_json(markdown_text):
    # 去掉开头的 ```json 和结尾的 ```
    if markdown_text.startswith('```json'):
        markdown_text = markdown_text[7:]
    if markdown_text.endswith('```'):
        markdown_text = markdown_text[:-3]

    lines = markdown_text.strip().split('\n')
    stack = []
    current = {}
    id_counter = 1  # 初始化ID计数器

    for line in lines:
        if line.startswith('#'):
            level = len(re.match(r'#+', line).group(0))
            title = line[level:].strip()
            node = {
                "titleId": id_counter,
                "templateId": 1,
                "parentId": 0 if not stack else stack[-1]["titleId"],
                "titleName": title,
                "showOrder": None,
                "writingRequirement": "",
                "statusCd": "Y",
                "children": []
            }
            id_counter += 1  # 每次创建新节点时增加ID计数器
            while len(stack) >= level:
                stack.pop()
            if stack:
                stack[-1]["children"].append(node)
            else:
                current = node
            stack.append(node)
        elif line.strip():
            stack[-1]["writingRequirement"] = line.strip()

    return json.dumps(current, ensure_ascii=False, indent=4)
# def markdown_to_json(markdown_text):
#     # 去掉开头的 ```json 和结尾的 ```
#     if markdown_text.startswith('```json'):
#         markdown_text = markdown_text[7:]
#     if markdown_text.endswith('```'):
#         markdown_text = markdown_text[:-3]

#     lines = markdown_text.strip().split('\n')
#     stack = []
#     current = {}
#     for line in lines:
#         if line.startswith('#'):
#             level = len(re.match(r'#+', line).group(0))
#             title = line[level:].strip()
#             node = {
#                 "titleName": title,
#                 "writingRequirement": "",
#                 "children": []
#             }
#             while len(stack) >= level:
#                 stack.pop()
#             if stack:
#                 stack[-1]["children"].append(node)
#             else:
#                 current = node
#             stack.append(node)
#         elif line.strip():
#             stack[-1]["writingRequirement"] = line.strip()
#     return json.dumps(current, ensure_ascii=False, indent=4)

def json_to_markdown(json_data, level=1):
    markdown_lines = []
    prefix = '#' * level
    markdown_lines.append(f"{prefix} {json_data['titleName']}")
    if json_data['writingRequirement']:
        markdown_lines.append(json_data['writingRequirement'])
    for child in json_data.get('children', []):
        markdown_lines.append(json_to_markdown(child, level + 1))
    return '\n'.join(markdown_lines)
