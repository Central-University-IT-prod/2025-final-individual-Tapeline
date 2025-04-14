import uuid
from dataclasses import dataclass
import json
from io import BytesIO
from urllib.parse import urlsplit

import minio
from dishka import FromDishka

from prodadvert.application.interfaces.storage import FileStorage
from prodadvert.config import Config


@dataclass
class S3ConnectionParameters:
    bucket_name: str
    endpoint: str
    username: str
    password: str
    is_secure: bool


class S3Storage(FileStorage):
    client: minio.Minio | None

    def __init__(self, config: FromDishka[Config]):
        self.client = None
        self.params = S3ConnectionParameters(
            bucket_name=config.s3.bucket_name,
            endpoint="{host}:{port}".format(
               host=config.s3.host.replace("https://", "").replace("http://", ""),
               port=config.s3.port,
            ),
            username=config.s3.username,
            password=config.s3.password,
            is_secure=config.s3.host.startswith("https")
        )
        self.connect()
        self.create_bucket_if_not_present()

    def create_bucket_if_not_present(self):  # pragma: no cover
        if not self.client.bucket_exists(self.params.bucket_name):
            self.client.make_bucket(self.params.bucket_name)
            self.client.set_bucket_policy(
                self.params.bucket_name,
                json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                            "Resource": f"arn:aws:s3:::{self.params.bucket_name}",
                        },
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{self.params.bucket_name}/*",
                        },
                    ],
                })
            )

    def connect(self):
        self.client = minio.Minio(
            self.params.endpoint,
            access_key=self.params.username,
            secret_key=self.params.password,
            secure=self.params.is_secure
        )

    async def upload_file(
            self, filename: str, content: bytes, content_type: str
    ) -> str:
        if not self.client:  # pragma: no cover
            raise ValueError("Not connected")
        fake_io = BytesIO(content)
        final_name = f"{uuid.uuid4()}{filename}"
        self.client.put_object(
            bucket_name=self.params.bucket_name,
            object_name=final_name,
            data=fake_io,
            length=len(content),
            content_type=content_type
        )
        return await self.get_file_url(final_name)

    async def get_file_url(self, name: str) -> str:
        if not self.client:  # pragma: no cover
            raise ValueError("Not connected")
        signed_url = self.client.get_presigned_url(
            "GET", self.params.bucket_name, name
        )
        url = urlsplit(signed_url)
        return url.path
