import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import os
import PyPDF2
from fastapi import APIRouter, Depends, Request, HTTPException
from models.file import FilePathRequest, FileAnalysisResponse
from services.files import file_structure_extract, new_file_structure_extract
from utils.logger import mylog
import requests
from urllib.parse import urlparse
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from openai import BaseModel
from sqlalchemy import create_engine, Column, BigInteger, String, Integer, TIMESTAMP, update, null, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random
import string
from datetime import datetime
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import AsyncSessionLocal
from config import get_async_db
from docx import Document
from io import BytesIO
from tenacity import retry, stop_after_attempt, wait_fixed
router = APIRouter()
Base = declarative_base()

"""统一使用全局 get_async_db，避免多处硬编码数据库连接导致环境不一致"""

class AiFileRel(Base):
    __tablename__ = 'ai_file_rel'
    file_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='附件主键')
    busi_id = Column(String(100), comment='业务标识')
    busi_code = Column(String(10), comment='业务类型')
    file_name = Column(String(1000), comment='原文件名称')
    file_page = Column(Integer, comment='页数')
    create_date = Column(TIMESTAMP, comment='上传时间')
    create_no = Column(String(100), comment='上传人')
    create_name = Column(String(100), comment='上传人名称')
    update_date = Column(TIMESTAMP, comment='修改时间')
    update_no = Column(String(100), comment='修改人')
    update_name = Column(String(100), comment='修改人名称')
    status_cd = Column(String(10), comment='状态，0等待解析，1解析完成，-1无效')
    remark = Column(String(255), comment='备注')
    file_url = Column(String(255), comment='文件地址')
    system_name = Column(String(100), comment='系统文件名称')
    data_path = Column(String(255), comment='文件路径')
    title_data = Column(String, comment='文件解析标题数据')

# 使用 config.get_async_db 注入 db

# 设置文件保存的目录
UPLOAD_FOLDER = Path(os.getenv('UPLOAD_FOLDER', './uploads'))
try:
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    UPLOAD_FOLDER = Path('./uploads')
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'docx', 'doc'}

class reFilename(BaseModel):
    file_id: int
    file_name: str = None

class queryFile(BaseModel):
    busiId: str
    pageNum: int = None
    pageSize: int = None

class reAnalysisRequest(BaseModel):
    file_id: int

class deleteFile(BaseModel):
    file_id: int

class queryFile(BaseModel):
    busiId: str
    pageNum: int = None
    pageSize: int = None
    

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_random_string(length: int) -> str:
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(length))

async def get_unique_filename(extension: str) -> str:
    now = datetime.now().strftime("%Y%m%d%H%M")
    random_string = get_random_string(5)
    return f"{now}-{random_string}.{extension}"

@router.post("/analysis")
async def file_analysis(request_data: FilePathRequest, request: Request):
    mylog.info("*"*100)
    mylog.info(f"开始分析文件: {request_data.filePath}")
    mylog.info(f"源IP: {request.client.host}")
    filePath = await fangan_file_download(request_data.filePath)
    analysis_result = await file_structure_extract(filePath)
    if analysis_result is None:
        raise HTTPException(status_code=400, detail="文件分析失败")
    mylog.info("文件解析成功预计返回数据：", analysis_result)
    return analysis_result

async def fangan_file_download(filePath):
    file_name = os.path.basename(filePath)
    file_path = "http://36.133.78.98:9531/dubhe-ai/solution/" + file_name
    if file_path.startswith('http://') or file_path.startswith('https://'):
        response = requests.get(file_path)
        if response.status_code == 200:
            parsed_url = urlparse(file_path)
            file_name = os.path.basename(parsed_url.path)
            tmp_file_path = os.path.join('/data/xieyu/file_download', file_name)
            with open(tmp_file_path, 'wb') as f:
                f.write(response.content)
            return tmp_file_path
        else:
            mylog.error(f"无法下载文件: {file_path}")
            return None


async def count_characters_in_docx(file_stream):
    document = Document(BytesIO(file_stream))
    return sum(len(paragraph.text) for paragraph in document.paragraphs if paragraph.text)

async def count_characters_in_pdf(file_stream):
    reader = PyPDF2.PdfReader(BytesIO(file_stream))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return len(text)

async def count_characters_in_text_like(file_stream):
    try:
        text = file_stream.decode('utf-8', errors='ignore')
    except Exception:
        text = ''
    return len(text)
# 文件大小限制 10000个字符
MAX_FILE_SIZE = 10000  
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    createNo: str = Form(...),
    createName: str = Form(...),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="未找到上传文件，请重新上传")

        # 读取上传内容
        file_stream = await file.read()
        filename = file.filename
        if not allowed_file(filename):
            raise HTTPException(status_code=415, detail="不支持的文件类型")

        # 推断扩展名（小写）
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        # 仅统计长度用于日志，不做拦截
        try:
            if extension == 'docx':
                _ = await count_characters_in_docx(file_stream)
            elif extension == 'pdf':
                _ = await count_characters_in_pdf(file_stream)
            elif extension in ('txt', 'md'):
                _ = await count_characters_in_text_like(file_stream)
        except Exception:
            pass

        # 生成唯一文件名并写入磁盘
        unique_filename = await get_unique_filename(extension or 'bin')
        file_location = str((UPLOAD_FOLDER / unique_filename).resolve())
        with open(file_location, "wb") as file_object:
            file_object.write(file_stream)
            file_object.flush()
            os.fsync(file_object.fileno())

        file_size = os.path.getsize(file_location)
        mylog.info(f"写入后的文件大小: {file_size} 字节, 路径: {file_location}")
        if file_size == 0:
            raise HTTPException(status_code=500, detail="文件写入失败，文件大小为0")

        # 入库记录 & 启动异步解析
        new_file_info = await insert_file_data(db, filename.rsplit('.', 1)[0], unique_filename,
                                               file_location, createNo, createNo, createName)
        asyncio.create_task(background_parse(new_file_info.file_id, file_location))

        # 规范化时间字段
        if isinstance(new_file_info.create_date, str):
            new_file_info.create_date = datetime.fromisoformat(new_file_info.create_date.replace('Z', '+00:00'))
        new_file_info.create_date = new_file_info.create_date.strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "file_id": new_file_info.file_id,
            "file_name": new_file_info.file_name,
            "create_date": new_file_info.create_date,
        }
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 200, "message": "文件上传成功", "type": "success", "data": data
        }))
    except HTTPException:
        # 直接抛出 HTTPException 让 FastAPI 处理状态码
        raise
    except Exception as e:
        mylog.error(f"文件上传发生异常: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content=jsonable_encoder({
            "code": 500, "message": "文件上传失败，请重试", "type": "error"
        }))

async def parse_file(db: AsyncSession, file_id: Integer, file_location: str):
    try:
        mylog.info(f"[文件解析] 步骤1: 开始解析文件 file_id={file_id}, 路径={file_location}")
        data = await new_file_structure_extract(file_location)
        mylog.info(f"[文件解析] 步骤2: 文件内容提取完成 file_id={file_id}, 页数={data.get('pages', 'N/A')}")
        
        # 直接检查 data['data'] 是否存在并且不为空
        plan = data.get('data', {}).get('data', {})
        if 'titleName' in plan and 'writingRequirement' in plan:
            mylog.info(f"[文件解析] 步骤3: 结构解析成功 file_id={file_id}, 标题={plan.get('titleName', '')}")
            await file_analysis_success(db, file_id, data['pages'], 1, json.dumps(plan, ensure_ascii=False))
            mylog.info(f"[文件解析] 完成: 文件解析成功 file_id={file_id}")
        else:
            mylog.warning(f"[文件解析] 步骤3: 结构解析失败，缺少必要字段 file_id={file_id}")
            await file_analysis_failed(db, file_id, 2, json.dumps(plan, ensure_ascii=False))
    except Exception as e:
        mylog.error(f"[文件解析] 异常: file_id={file_id}, 错误={str(e)}")
        await file_analysis_failed(db, file_id, 2, json.dumps({"error": str(e)}, ensure_ascii=False))

async def background_parse(file_id: Integer, file_location: str):
    mylog.info(f"[文件解析] 启动后台解析任务 file_id={file_id}")
    if not os.path.exists(file_location):
        mylog.error(f"[文件解析] 文件不存在: {file_location}")
        raise FileNotFoundError(f"文件不存在: {file_location}")
    async with AsyncSessionLocal() as db:
        await parse_file(db, file_id, file_location)

@router.post("/reAnalysis")
async def re_analysis(request_data: reAnalysisRequest, request: Request, db: AsyncSession = Depends(get_async_db)):
    mylog.info(f"开始分析文件: {request_data.file_id}")
    stmt = select(AiFileRel).filter(AiFileRel.file_id == request_data.file_id)
    result = await db.execute(stmt)
    file_data = result.scalar_one_or_none()
    
    if file_data:
        asyncio.create_task(background_parse(request_data.file_id, file_data.file_url))
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": "开始重新解析文件，请稍后", "type": "success"})
        )
    raise HTTPException(status_code=404, detail="File not found")

async def insert_file_data(db: AsyncSession, filename, unique_filename, file_path, busiId, createNo, createName):
    new_file_info = AiFileRel(
        busi_id=busiId,
        busi_code='S',
        file_name=filename,
        create_date=datetime.now(),
        create_no=createNo,
        create_name=createName,
        status_cd='0',
        file_url=file_path,
        system_name=unique_filename
    )
    db.add(new_file_info)
    await db.commit()
    await db.refresh(new_file_info)
    return new_file_info

async def file_analysis_success(db: AsyncSession, file_id, filePage, statusCd, titleData):
    stmt = update(AiFileRel).where(
        AiFileRel.file_id == file_id
    ).values(
        file_page=filePage,
        status_cd=statusCd,
        title_data=titleData
    )
    await db.execute(stmt)
    await db.commit()

async def file_analysis_failed(db: AsyncSession, file_id, statusCd,titleData):
    stmt = update(AiFileRel).where(
        AiFileRel.file_id == file_id
    ).values(status_cd=statusCd,title_data=titleData)
    await db.execute(stmt)
    await db.commit()

@router.post("/reFilename")
async def re_filename(re_filename: reFilename, db: AsyncSession = Depends(get_async_db)):
    stmt = update(AiFileRel).where(
        AiFileRel.file_id == re_filename.file_id
    ).values(
        file_name=re_filename.file_name,
        update_date=datetime.now()
    )
    await db.execute(stmt)
    await db.commit()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {"code": 200, "message": "文件重命名成功", "type": "success"})
    )

# 重试装饰器配置
# stop=stop_after_attempt(3) 表示最多重试3次
# wait=wait_fixed(2) 表示每次重试之间等待1秒
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def execute_query_with_retry(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        mylog.error(f"查询失败，将重试: {str(e)}")
        raise  # 重新抛出异常以触发重试

@router.post("/queryFileList")
async def query_file_list(query_file: queryFile, db: AsyncSession = Depends(get_async_db)):
    try:
        stmt = select(AiFileRel).filter(
            (AiFileRel.busi_id == query_file.busiId)
            & (AiFileRel.busi_code == "S")
        ).order_by(AiFileRel.create_date.desc())
        
        result = await db.execute(stmt)
        total_count = len(await execute_query_with_retry(db, stmt))
        
        # 分页
        stmt1 = stmt.offset((query_file.pageNum - 1) * query_file.pageSize).limit(query_file.pageSize)
        results = await execute_query_with_retry(db, stmt1)
        
        # 格式化日期
        for result in results:
            if isinstance(result.create_date, str):
                result.create_date = datetime.fromisoformat(result.create_date.replace('Z', '+00:00'))
            result.create_date = result.create_date.strftime("%Y-%m-%d %H:%M:%S")
            
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": "文件列表查询成功", "type": "success", 
                 "data": {"fileCount": total_count, "fileList": results}})
        )
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return JSONResponse(
            status_code=500, 
            content=jsonable_encoder({"code": 500, "message": str(e), "type": "error"})
        )

@router.post("/selectTemplateTitle")
async def select_template_title(re_filename: reFilename, db: AsyncSession = Depends(get_async_db)):
    stmt = select(AiFileRel).filter(AiFileRel.file_id == re_filename.file_id)
    result = await db.execute(stmt)
    files = result.scalars().all()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {"code": 200, "message": null, "type": "success", "data": files})
    )

@router.post("/fileDelete")
async def file_delete(delete_File: deleteFile, db: AsyncSession = Depends(get_async_db)):
    kwargs = {
        'busi_code': 'O',
    }
    # 删除文件信息
    stmt = update(AiFileRel).where(
        (AiFileRel.file_id == delete_File.file_id)
    ).values(**kwargs)
    await db.execute(stmt)
    # 提交事务
    await db.commit()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {"code": 200, "message": f"文件删除成功", "type": "success"})
    )

async def select_file_by_title(db: AsyncSession,fileName: str, userId: str):
    # 只返回解析完成的文件（status_cd = '1'），过滤掉正在解析中或解析失败的文件
    stmt = select(AiFileRel).filter(
        (AiFileRel.busi_id == userId) & (AiFileRel.busi_code == "S") & (AiFileRel.status_cd == "1")
    ).order_by(AiFileRel.create_date.desc())
    
    if fileName:
        stmt = stmt.filter(AiFileRel.file_name.like(f'%{fileName}%'))
    
    result = await db.execute(stmt)
    return result.scalars().all()