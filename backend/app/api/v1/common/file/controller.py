from fastapi import File, Query, UploadFile

from app.api.v1.common.file.schema import FileId, FileIdList, FileQuery
from app.api.v1.common.file.service import FileService
from app.corelibs.custom_router import APIRouter
from app.utils.response import HttpResponse

FileRouter = APIRouter(prefix="/file", tags=["文件管理"])
FileAccessRouter = APIRouter(tags=["文件访问"])


@FileRouter.post("/upload", description="文件上传")
async def upload(file: UploadFile = File(...), folder: str = Query(default="")):
    try:
        result = await FileService.upload(file, folder)
        return await HttpResponse.success(result)
    except ValueError as exc:
        return await HttpResponse.fail(msg=str(exc))


@FileRouter.post("/list", description="文件列表")
async def file_list(params: FileQuery):
    result = await FileService.get_file_list(params)
    return await HttpResponse.success(result)


@FileRouter.get("/statistics", description="文件统计")
async def file_statistics():
    result = await FileService.get_statistics()
    return await HttpResponse.success(result)


@FileRouter.get("/storage-config", description="存储配置")
async def storage_config():
    result = await FileService.get_storage_config()
    return await HttpResponse.success(result)


@FileRouter.get("/download/{file_id}", description="文件下载")
async def download(file_id: str):
    return await FileService.download(file_id)


@FileRouter.get("/getFileById", description="根据id获取文件下载地址")
async def get_file_by_id(params: FileId):
    data = await FileService.get_file_by_id(params)
    return await HttpResponse.success(data)


@FileRouter.post("/deleted", description="文件删除")
async def deleted(params: FileId):
    data = await FileService.deleted(params)
    return await HttpResponse.success(data)


@FileRouter.post("/deleteList", description="批量删除文件")
async def delete_list(params: FileIdList):
    data = await FileService.batch_deleted(params)
    return await HttpResponse.success({"count": data})


@FileAccessRouter.get("/files/{file_path:path}", description="本地存储文件访问")
async def access_local_file(file_path: str):
    return await FileService.serve_local_file(file_path)
