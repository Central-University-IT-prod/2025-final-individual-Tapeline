import os

from pydantic import Field, BaseModel


class BackendConfig(BaseModel):
    base_url: str = Field(alias="API_BASE_URL", default="http://localhost:8080")


class S3Config(BaseModel):
    base_url: str = Field(alias="S3_BASE_URL", default="http://localhost:9000")


class Config(BaseModel):
    api: BackendConfig = Field(
        default_factory=lambda: BackendConfig(**os.environ)
    )
    s3: S3Config = Field(
        default_factory=lambda: S3Config(**os.environ)
    )
