from botocore.client import BaseClient
from botocore.exceptions import ClientError
from dependencies import base_logger, get_s3_client, settings
from fastapi import Depends, UploadFile


class S3Repo:
    def __init__(self, client: BaseClient = Depends(get_s3_client)):
        self.client = client

    async def insert(self, file: UploadFile):
        try:
            await self.client.upload_fileobj(file.file, "ums", file.filename)
        except ClientError as e:
            base_logger.error(f"Client exception during s3 insertion: {e}")
            raise e
        except Exception as e:
            base_logger.error(f"Unknown exception during s3 insertion: {e}")
            raise e

    async def create_presigned_url(self, bucket_name: str, object_name: str):
        try:
            if bucket_name and object_name:
                url = await self.client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": object_name},
                    ExpiresIn=settings.PRESIGNED_URL_EXPIRATION_SECONDS,
                )
            else:
                return None
        except ClientError as e:
            base_logger.error(f"Client exception during s3 insertion: {e}")
            raise e
        except Exception as e:
            base_logger.error(f"Unknown exception during s3 insertion: {e}")
            raise e
        return url
