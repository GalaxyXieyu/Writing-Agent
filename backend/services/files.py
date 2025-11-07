import asyncio
import subprocess
from docx import Document
from PyPDF2 import PdfReader
from utils.logger import mylog
import os 
import traceback
from ai.agents.planner import planner

async def docx_to_pdf(docx_path, pdf_path):
    try:
        # 使用libreoffice将docx文件转换为pdf文件
        subprocess.run(['libreoffice', '--convert-to', 'pdf', '--outdir', os.path.dirname(pdf_path), docx_path])
        mylog.info(f"PDF文件路径: {pdf_path}")
        return pdf_path
    except subprocess.CalledProcessError as e:
        mylog.error(f"DOCX转PDF失败: {e}")
        return None

async def structure_extract(context):
    try:
        # 构建查询字符串以提取文章结构
        #query = f"请帮我制定该文章{context}的总标题、一级标题、一级标题要求、二级标题、二级标题要求"
        #return planner.invoke(query)
        # 使用线程池执行CPU密集型操作
        loop = asyncio.get_event_loop()
        query = f"请帮我制定该文章{context}的总标题、一级标题、一级标题要求、二级标题、二级标题要求"
        # 将 planner.invoke 放在线程池中执行
        response = await loop.run_in_executor(None, lambda: planner.invoke(query))
        return response
    except:
        mylog.info(traceback.format_exc())
        response = {"error": True, "code": 200, "message": "Failed to fetch"}
        return response


async def file_structure_extract(file_path):
    try:
        if not os.path.isfile(file_path):
            mylog.error(f"文件不存在: {file_path}")
            return None

        file_extension = os.path.splitext(file_path)[1].lower()[1:]
        if file_extension == 'pdf':
            # 处理PDF文件
            pdf = PdfReader(file_path)
            num_pages = len(pdf.pages)
            content = [pdf.pages[i].extract_text() for i in range(num_pages)]
            total_characters = sum(len(page) for page in content)
            plan = await structure_extract(content)
            data = {
                'code': 200,
                'type': 'success',
                'pages': num_pages,
                'content': content,
                'fileWords': total_characters,
                'data': plan
            }
            mylog.info(f"PDF文件处理成功: {file_path}, 页数: {num_pages}, 字符总数: {total_characters}")
        elif file_extension == 'docx':
            # 处理DOCX文件
            doc = Document(file_path)
            pdf_path = os.path.splitext(file_path)[0] + '.pdf'
            pdf_path = docx_to_pdf(file_path, pdf_path)
            pdf = PdfReader(pdf_path)
            total_pages = len(pdf.pages)
            full_text = []
            total_words = 0
            for para in doc.paragraphs:
                text = para.text
                full_text.append(text)
                total_words += len(text.split())
            full_text = '\n'.join(full_text)
            plan = await structure_extract(full_text)
            data = {
                'code': 200,
                'type': 'success',
                'pages': total_pages,
                'content': full_text,
                'fileWords': total_words,
                'data': plan
            }
            mylog.info(f"DOCX文件处理成功: {file_path}, 页数: {total_pages}, 单词总数: {total_words}")
        else:
            mylog.error(f"不支持的文件类型: {file_extension}")
            return None

        return data
    except Exception as e:
        error_msg = f"文件解析失败: {str(e)}"
        mylog.error(error_msg)
        mylog.error(traceback.format_exc())
        return None


async def new_file_structure_extract(file_path):
    try:
        if not os.path.isfile(file_path):
            mylog.error(f"文件不存在: {file_path}")
            return None
        file_extension = os.path.splitext(file_path)[1].lower()[1:]
        # 使用线程池处理文件IO操作
        loop = asyncio.get_event_loop()
        if file_extension == 'pdf':
            # 在线程池中执行PDF处理
            def process_pdf():
                pdf = PdfReader(file_path)
                num_pages = len(pdf.pages)
                content = [pdf.pages[i].extract_text() for i in range(num_pages)]
                total_characters = sum(len(page) for page in content)
                return num_pages, content, total_characters
            num_pages, content, total_characters = await loop.run_in_executor(None, process_pdf)
            plan = await structure_extract(content)
            data = {
                'code': 200,
                'type': 'success',
                'pages': num_pages,
                'content': content,
                'fileWords': total_characters,
                'data': plan
            }
            mylog.info(f"PDF文件处理成功: {file_path}, 页数: {num_pages}, 字符总数: {total_characters}")
        elif file_extension == 'docx':
            # 在线程池中执行DOCX处理
            def process_docx():
                full_text = []
                doc = Document(file_path)
                for para in doc.paragraphs:
                    full_text.append(para.text)
                return '\n'.join(full_text)
            
            full_text = await loop.run_in_executor(None, process_docx)
            pdf_path = os.path.splitext(file_path)[0] + '.pdf'
            pdf_path = await docx_to_pdf(file_path, pdf_path)
            pdf = PdfReader(pdf_path)
            total_pages = len(pdf.pages)
            mylog.info(f"DOCX文件处理成功: {full_text}, 页数: {total_pages}")
            plan = await structure_extract(full_text)
            data = {
                'code': 200,
                'type': 'success',
                'pages': total_pages,
                'content': full_text,
                'data': plan
            }
            
        else:
            mylog.error(f"不支持的文件类型: {file_extension}")
            return None

        return data
    except Exception as e:
        error_msg = f"文件解析失败: {str(e)}"
        mylog.error(error_msg)
        mylog.error(traceback.format_exc())
        return None