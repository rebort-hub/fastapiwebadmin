from fastapi import APIRouter, UploadFile, File

from app.utils.response import HttpResponse
from app.schemas.system.file import FileId, FileQuery
from app.services.system.file import FileService

router = APIRouter()


@router.post('/upload', description="文件上传")
async def upload(file: UploadFile = File(...)):
    result = await FileService.upload(file)
    return await HttpResponse.success(result)


@router.post('/list', description="文件列表")
async def file_list(params: FileQuery):
    """获取文件列表"""
    result = await FileService.get_file_list(params)
    return await HttpResponse.success(result)


@router.get('/download/{file_id}', description="文件下载")
async def download(file_id: str):
    result = await FileService.download(file_id)
    return result


@router.get('/getFileById', description="根据id获取文件下载地址")
async def get_file_by_id(params: FileId):
    return await FileService.get_file_by_id(params)


@router.post('/deleted', description="文件删除")
async def deleted(params: FileId):
    data = await FileService.deleted(params)
    return await HttpResponse.success(data)
