# -*- coding: utf-8 -*-
import typing

from fastapi import UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from loguru import logger

from app.api.v1.common.file.model import FileInfo
from app.api.v1.common.file.schema import FileId, FileIdList, FileIn, FileQuery
from app.config.setting import settings
from app.utils.common import get_str_uuid
from app.utils.current_user import current_user
from app.utils.storage import StorageFactory, StorageType


def _get_file_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    image_ext = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"}
    doc_ext = {"doc", "docx", "xls", "xlsx", "ppt", "pptx", "pdf", "txt", "md", "csv"}
    video_ext = {"mp4", "avi", "mov", "wmv", "flv", "mkv"}
    audio_ext = {"mp3", "wav", "flac", "aac", "ogg"}
    archive_ext = {"zip", "rar", "7z", "tar", "gz"}
    if ext in image_ext:
        return "image"
    if ext in doc_ext:
        return "document"
    if ext in video_ext:
        return "video"
    if ext in audio_ext:
        return "audio"
    if ext in archive_ext:
        return "archive"
    return "other"


class FileService:
    @staticmethod
    def _validate_upload(file: UploadFile, content: bytes) -> None:
        max_bytes = settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise ValueError(f"文件大小超过限制（最大 {settings.UPLOAD_MAX_SIZE_MB}MB）")
        ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
        allowed = settings.upload_allowed_ext_list
        if allowed and ext and ext not in allowed:
            raise ValueError(f"不支持的文件类型: {ext}")

    @staticmethod
    async def upload(file: UploadFile, folder: str = "") -> typing.Dict[str, typing.Any]:
        if not file:
            raise FileNotFoundError("请选择上传文件！")
        content = await file.read()
        await file.seek(0)
        FileService._validate_upload(file, content)

        storage_type = settings.UPLOAD_STORAGE_TYPE or StorageType.LOCAL
        storage = StorageFactory.create(storage_type)
        result = await storage.upload(file, folder)

        ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
        uploader_id = None
        uploader_name = None
        try:
            user = await current_user()
            uploader_id = user.get("id")
            uploader_name = user.get("username")
        except Exception:
            pass

        file_id = get_str_uuid()
        file_params = FileIn(
            id=file_id,
            name=result["key"].split("/")[-1],
            file_path=result["key"],
            extend_name=ext,
            original_name=file.filename,
            content_type=file.content_type,
            file_size=str(round(result["size"] / 1024, 2)),
            storage_type=storage_type,
            file_url=result["url"],
            file_hash=result.get("hash"),
            uploader_id=uploader_id,
            uploader_name=uploader_name,
        )
        await FileInfo.create(file_params.model_dump(), to_dict=True)
        return {
            "id": file_id,
            "url": result["url"],
            "name": file.filename,
            "original_name": file.filename,
            "storage_type": storage_type,
            "file_type": _get_file_type(file.filename or ""),
            "size": result["size"],
        }

    @staticmethod
    async def get_file_list(params: FileQuery) -> typing.Dict:
        return await FileInfo.get_list(params)

    @staticmethod
    async def get_statistics() -> dict:
        return await FileInfo.statistics()

    @staticmethod
    async def get_storage_config() -> dict:
        return StorageFactory.get_storage_config()

    @staticmethod
    async def download(file_id: str):
        file_info = await FileInfo.get(file_id, to_dict=True)
        if not file_info:
            return HTMLResponse(content="文件不存在")
        storage_type = file_info.get("storage_type") or StorageType.LOCAL
        storage_key = file_info.get("file_path")
        if storage_type != StorageType.LOCAL and file_info.get("file_url"):
            return RedirectResponse(file_info["file_url"])
        from app.utils.storage import LocalStorage

        storage = StorageFactory.create(storage_type)
        if isinstance(storage, LocalStorage) and storage_key:
            local_path = storage.get_file_path(storage_key)
            if local_path.is_file():
                return FileResponse(path=str(local_path), filename=file_info.get("original_name"))
            import os

            legacy_path = os.path.join(settings.upload_local_dir, file_info.get("name") or "")
            if os.path.isfile(legacy_path):
                return FileResponse(path=legacy_path, filename=file_info.get("original_name"))
        if file_info.get("file_url"):
            return RedirectResponse(file_info["file_url"])
        return HTMLResponse(content="文件不存在")

    @staticmethod
    async def deleted(params: FileId) -> int:
        file_info = await FileInfo.get(params.id, to_dict=True)
        if not file_info:
            raise FileNotFoundError("文件不存在！")
        storage = StorageFactory.create(file_info.get("storage_type") or StorageType.LOCAL)
        storage_key = file_info.get("file_path")
        if storage_key:
            await storage.delete(storage_key)
        return await FileInfo.delete(params.id)

    @staticmethod
    async def batch_deleted(params: FileIdList) -> int:
        count = 0
        for file_id in params.ids:
            try:
                await FileService.deleted(FileId(id=file_id))
                count += 1
            except Exception as exc:
                logger.warning(f"删除文件 {file_id} 失败: {exc}")
        return count

    @staticmethod
    async def get_file_by_id(params: FileId):
        file_info = await FileInfo.get(params.id, to_dict=True)
        if not file_info:
            raise FileNotFoundError("文件不存在！")
        return {
            "id": file_info["id"],
            "url": file_info.get("file_url") or f"/api/file/download/{file_info['id']}",
            "name": file_info.get("original_name"),
            "storage_type": file_info.get("storage_type"),
        }

    @staticmethod
    async def serve_local_file(file_path: str):
        from app.utils.storage import LocalStorage

        storage = StorageFactory.create(StorageType.LOCAL)
        if not isinstance(storage, LocalStorage):
            return HTMLResponse(content="文件不存在", status_code=404)
        local_file = storage.get_file_path(file_path)
        if not local_file.is_file():
            return HTMLResponse(content="文件不存在", status_code=404)
        return FileResponse(path=str(local_file))
