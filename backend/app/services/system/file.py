import os
import typing
import uuid
from fastapi import UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from loguru import logger
from config import config
from app.models.system_models import FileInfo
from app.schemas.system.file import FileIn, FileId, FileQuery
import aiofiles

from app.utils.common import get_str_uuid


class FileService:
    """文件"""

    @staticmethod
    async def upload(file: UploadFile) -> typing.Dict[str, str]:
        """文件上传"""
        if not file:
            raise FileNotFoundError('请选择上传文件！')
        file_dir = config.TEST_FILES_DIR
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        extend_file = file.filename.split(".")
        extend_name = extend_file[-1] if len(extend_file) > 1 else None

        file_name = f'{str(uuid.uuid4()).replace("-", "").upper()}'
        if extend_name:
            file_name = f"{file_name}.{extend_name}"
        abs_file_path = os.path.join(file_dir, file_name)
        contents = await file.read()
        file_size = str(round(len(contents) / 1024, 2))  # 转换为字符串
        async with aiofiles.open(abs_file_path, "wb") as f:
            await f.write(contents)
        file_params = FileIn(id=get_str_uuid(),
                             name=file_name,
                             file_path=abs_file_path,
                             extend_name=extend_name,
                             original_name=file.filename,
                             file_size=file_size,
                             content_type=file.content_type)

        file_info = await FileInfo.create(file_params.dict(), to_dict=True)
        logger.info(f'文件保存--> {abs_file_path}')
        file_id = file_info['id']
        data = {
            'id': file_id,
            'url': f'/file/download/{file_id}',
            'name': file.filename,
            'original_name': file.filename,
        }
        return data

    @staticmethod
    async def get_file_list(params: FileQuery) -> typing.Dict:
        """获取文件列表"""
        from sqlalchemy import select
        from app.models.system_models import FileInfo
        from app.utils.context import FastApiRequest
        
        # 构建查询
        q = [FileInfo.enabled_flag == 1]
        if params.name:
            q.append(FileInfo.original_name.like(f'%{params.name}%'))
        
        stmt = select(FileInfo).where(*q).order_by(FileInfo.creation_date.desc())
        
        # 直接传入分页参数，避免从 request 中获取
        from app.models.base import Base
        from app.db.sqlalchemy import async_session
        from math import ceil
        
        async with async_session() as session:
            # 获取总数
            count_stmt = Base.count_query(stmt)
            result = await session.execute(count_stmt)
            total = result.scalar()
            
            # 获取分页数据
            page = params.page
            page_size = min(params.pageSize, 1000)
            paginated_stmt = Base.paginate_query(stmt, page=page, page_size=page_size)
            result = await session.execute(paginated_stmt)
            rows = result.scalars().all()
            rows = Base.unwrap_scalars(rows)
            
            total_page = int(ceil(float(total) / page_size))
            
            return {
                'rowTotal': total,
                'pageSize': page_size,
                'page': page,
                'pageTotal': total_page,
                'rows': rows,
            }

    @staticmethod
    async def download(file_id: str) -> typing.Union[FileResponse, HTMLResponse]:
        file_info = await FileInfo.get(file_id)
        if not file_info:
            logger.error(f'{file_id} 文件不存在！')
            return HTMLResponse(content="文件不存在")
        file_dir = os.path.join(config.TEST_FILES_DIR, file_info.name)
        if not os.path.isfile(file_dir):
            logger.error(f'{file_info.name}文件不存在！')
            return HTMLResponse(content="文件不存在")

        return FileResponse(path=file_dir, filename=file_info.original_name)

    @staticmethod
    async def deleted(params: FileId) -> int:
        """删除文件"""
        # 先获取文件信息
        file_info = await FileInfo.get(params.id)
        if not file_info:
            logger.error(f'文件 {params.id} 不存在！')
            raise FileNotFoundError('文件不存在！')
        
        # 删除物理文件
        file_path = os.path.join(config.TEST_FILES_DIR, file_info.name)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                logger.info(f'物理文件已删除: {file_path}')
            except Exception as e:
                logger.error(f'删除物理文件失败: {file_path}, 错误: {e}')
        else:
            logger.warning(f'物理文件不存在: {file_path}')
        
        # 删除数据库记录
        result = await FileInfo.delete(params.id)
        logger.info(f'数据库记录已删除: {params.id}')
        return result

    @staticmethod
    async def get_file_by_id(params: FileId):
        file_info = await FileInfo.get(params.id)
        if not file_info:
            logger.error('文件不存在！')
            raise FileNotFoundError('文件不存在！')
        file_dir = os.path.join(config.TEST_FILES_DIR, file_info.file_name)
        if not os.path.isfile(file_dir):
            logger.error('文件不存在！')
            raise FileNotFoundError('文件不存在！')

        data = {
            'id': file_info.id,
            'url': f'/file/download/{file_info.file_name}',
            'name': file_info.original_name,
        }
        return data
