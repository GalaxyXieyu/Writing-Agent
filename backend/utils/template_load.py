from bs4 import BeautifulSoup
import json
import re
def html_to_structured_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    def parse_section(element, level=1):
        section = {"title": "", "content": "", "subsections": []}
        
        # Find the first h{level} tag
        title_tag = element.find(f'h{level}')
        if title_tag:
            section["title"] = title_tag.text.strip()
            
            # Process content and subsections
            current = title_tag.next_sibling
            while current and current.name != f'h{level}':
                if current.name == f'h{level+1}':
                    subsection = parse_section(current, level+1)
                    section["subsections"].append(subsection)
                    # Skip to the end of this subsection
                    while current.next_sibling and current.next_sibling.name != f'h{level}' and current.next_sibling.name != f'h{level+1}':
                        current = current.next_sibling
                elif current.name == 'p':
                    section["content"] += current.text.strip() + "\n"
                current = current.next_sibling
        
        return section
    
    structured_data = []
    for h1 in soup.find_all('h1'):
        structured_data.append(parse_section(h1))
    
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
