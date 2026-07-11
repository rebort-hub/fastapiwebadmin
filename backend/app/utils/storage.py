# -*- coding: utf-8 -*-
"""统一存储服务"""

import asyncio
import hashlib
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO
from pathlib import Path
import aiofiles
from fastapi import UploadFile
from loguru import logger

from app.config.setting import settings


class StorageType:
    LOCAL = "local"
    ALIYUN_OSS = "aliyun_oss"
    TENCENT_COS = "tencent_cos"
    QINIU = "qiniu"
    MINIO = "minio"

    LABELS = {
        LOCAL: "本地存储",
        ALIYUN_OSS: "阿里云 OSS",
        TENCENT_COS: "腾讯云 COS",
        QINIU: "七牛云",
        MINIO: "MinIO",
    }


class BaseStorage(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile, path: str = "") -> dict:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def get_url(self, key: str, expires: int = 3600) -> str:
        pass

    @staticmethod
    def generate_key(filename: str, path: str = "") -> str:
        ext = Path(filename or "file").suffix.lower()
        date_path = datetime.now().strftime("%Y/%m/%d")
        unique_id = uuid.uuid4().hex[:16]
        key = f"{date_path}/{unique_id}{ext}"
        if path:
            key = f"{path.strip('/')}/{key}"
        return key

    @staticmethod
    def get_file_hash(content: bytes) -> str:
        return hashlib.md5(content).hexdigest()


class LocalStorage(BaseStorage):
    def __init__(self, base_path: str, url_prefix: str = "/api/files"):
        self.base_path = Path(base_path)
        self.url_prefix = url_prefix.rstrip("/")
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload(self, file: UploadFile, path: str = "") -> dict:
        key = self.generate_key(file.filename or "file", path)
        file_path = self.base_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        content = await file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        return {
            "url": f"{self.url_prefix}/{key}",
            "key": key,
            "size": len(content),
            "hash": self.get_file_hash(content),
        }

    async def delete(self, key: str) -> bool:
        try:
            file_path = self.base_path / key
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as exc:
            logger.error(f"删除本地文件失败: {exc}")
            return False

    async def get_url(self, key: str, expires: int = 3600) -> str:
        return f"{self.url_prefix}/{key}"

    def get_file_path(self, key: str) -> Path:
        return self.base_path / key


class AliyunOSSStorage(BaseStorage):
    def __init__(self, access_key: str, secret_key: str, bucket: str, endpoint: str, domain: str = ""):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket
        self.endpoint = endpoint
        self.domain = domain
        self._bucket = None

    def _get_bucket(self):
        if self._bucket is None:
            import oss2

            auth = oss2.Auth(self.access_key, self.secret_key)
            self._bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
        return self._bucket

    async def upload(self, file: UploadFile, path: str = "") -> dict:
        key = self.generate_key(file.filename or "file", path)
        content = await file.read()
        bucket = self._get_bucket()
        await asyncio.to_thread(bucket.put_object, key, content)
        return {
            "url": await self.get_url(key),
            "key": key,
            "size": len(content),
            "hash": self.get_file_hash(content),
        }

    async def delete(self, key: str) -> bool:
        try:
            bucket = self._get_bucket()
            await asyncio.to_thread(bucket.delete_object, key)
            return True
        except Exception as exc:
            logger.error(f"删除阿里云 OSS 文件失败: {exc}")
            return False

    async def get_url(self, key: str, expires: int = 3600) -> str:
        if self.domain:
            return f"https://{self.domain}/{key}"
        return f"https://{self.bucket_name}.{self.endpoint}/{key}"


class TencentCOSStorage(BaseStorage):
    def __init__(self, secret_id: str, secret_key: str, bucket: str, region: str, domain: str = ""):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.bucket = bucket
        self.region = region
        self.domain = domain
        self._client = None

    def _get_client(self):
        if self._client is None:
            from qcloud_cos import CosConfig, CosS3Client

            config = CosConfig(Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key)
            self._client = CosS3Client(config)
        return self._client

    async def upload(self, file: UploadFile, path: str = "") -> dict:
        key = self.generate_key(file.filename or "file", path)
        content = await file.read()
        client = self._get_client()
        await asyncio.to_thread(client.put_object, Bucket=self.bucket, Body=content, Key=key)
        return {
            "url": await self.get_url(key),
            "key": key,
            "size": len(content),
            "hash": self.get_file_hash(content),
        }

    async def delete(self, key: str) -> bool:
        try:
            client = self._get_client()
            await asyncio.to_thread(client.delete_object, Bucket=self.bucket, Key=key)
            return True
        except Exception as exc:
            logger.error(f"删除腾讯云 COS 文件失败: {exc}")
            return False

    async def get_url(self, key: str, expires: int = 3600) -> str:
        if self.domain:
            return f"https://{self.domain}/{key}"
        return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{key}"


class QiniuStorage(BaseStorage):
    def __init__(self, access_key: str, secret_key: str, bucket: str, domain: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.domain = domain
        self._auth = None

    def _get_auth(self):
        if self._auth is None:
            from qiniu import Auth

            self._auth = Auth(self.access_key, self.secret_key)
        return self._auth

    async def upload(self, file: UploadFile, path: str = "") -> dict:
        from qiniu import put_data

        key = self.generate_key(file.filename or "file", path)
        content = await file.read()
        auth = self._get_auth()
        token = auth.upload_token(self.bucket, key)
        _, info = await asyncio.to_thread(put_data, token, key, content)
        if info.status_code != 200:
            raise RuntimeError(f"七牛云上传失败: {info.error}")
        return {
            "url": await self.get_url(key),
            "key": key,
            "size": len(content),
            "hash": self.get_file_hash(content),
        }

    async def delete(self, key: str) -> bool:
        try:
            from qiniu import BucketManager

            auth = self._get_auth()
            bucket_manager = BucketManager(auth)
            _, info = await asyncio.to_thread(bucket_manager.delete, self.bucket, key)
            return info.status_code == 200
        except Exception as exc:
            logger.error(f"删除七牛云文件失败: {exc}")
            return False

    async def get_url(self, key: str, expires: int = 3600) -> str:
        return f"https://{self.domain}/{key}"


class MinIOStorage(BaseStorage):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str, secure: bool = False):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.secure = secure
        self._client = None

    def _get_client(self):
        if self._client is None:
            from minio import Minio

            self._client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
            )
            if not self._client.bucket_exists(self.bucket):
                self._client.make_bucket(self.bucket)
        return self._client

    async def upload(self, file: UploadFile, path: str = "") -> dict:
        key = self.generate_key(file.filename or "file", path)
        content = await file.read()
        client = self._get_client()
        await asyncio.to_thread(client.put_object, self.bucket, key, BytesIO(content), len(content))
        return {
            "url": await self.get_url(key),
            "key": key,
            "size": len(content),
            "hash": self.get_file_hash(content),
        }

    async def delete(self, key: str) -> bool:
        try:
            client = self._get_client()
            await asyncio.to_thread(client.remove_object, self.bucket, key)
            return True
        except Exception as exc:
            logger.error(f"删除 MinIO 文件失败: {exc}")
            return False

    async def get_url(self, key: str, expires: int = 3600) -> str:
        protocol = "https" if self.secure else "http"
        return f"{protocol}://{self.endpoint}/{self.bucket}/{key}"


class StorageFactory:
    @staticmethod
    def create(storage_type: str | None = None) -> BaseStorage:
        storage_type = (storage_type or settings.UPLOAD_STORAGE_TYPE or StorageType.LOCAL).lower()
        if storage_type == StorageType.ALIYUN_OSS:
            return AliyunOSSStorage(
                access_key=settings.ALIYUN_OSS_ACCESS_KEY,
                secret_key=settings.ALIYUN_OSS_SECRET_KEY,
                bucket=settings.ALIYUN_OSS_BUCKET,
                endpoint=settings.ALIYUN_OSS_ENDPOINT,
                domain=settings.ALIYUN_OSS_DOMAIN,
            )
        if storage_type == StorageType.TENCENT_COS:
            return TencentCOSStorage(
                secret_id=settings.TENCENT_COS_SECRET_ID,
                secret_key=settings.TENCENT_COS_SECRET_KEY,
                bucket=settings.TENCENT_COS_BUCKET,
                region=settings.TENCENT_COS_REGION,
                domain=settings.TENCENT_COS_DOMAIN,
            )
        if storage_type == StorageType.QINIU:
            return QiniuStorage(
                access_key=settings.QINIU_ACCESS_KEY,
                secret_key=settings.QINIU_SECRET_KEY,
                bucket=settings.QINIU_BUCKET,
                domain=settings.QINIU_DOMAIN,
            )
        if storage_type == StorageType.MINIO:
            return MinIOStorage(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                bucket=settings.MINIO_BUCKET,
                secure=settings.MINIO_SECURE,
            )
        return LocalStorage(settings.upload_local_dir, settings.UPLOAD_URL_PREFIX)

    @staticmethod
    def get_storage_config() -> dict:
        storage_type = settings.UPLOAD_STORAGE_TYPE or StorageType.LOCAL
        return {
            "storage_type": storage_type,
            "storage_label": StorageType.LABELS.get(storage_type, storage_type),
            "max_size": settings.UPLOAD_MAX_SIZE_MB,
            "allowed_extensions": settings.upload_allowed_ext_list,
            "providers": [
                {"value": key, "label": label}
                for key, label in StorageType.LABELS.items()
            ],
        }
