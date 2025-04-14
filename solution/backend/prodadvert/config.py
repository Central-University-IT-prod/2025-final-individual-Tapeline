import os

from pydantic import Field, BaseModel


class PostgresConfig(BaseModel):
    host: str = Field(alias="DB_HOST", default="localhost")
    port: int = Field(alias="DB_PORT", default=5432)
    username: str = Field(alias="DB_USER", default="pguser")
    password: str = Field(alias="DB_PASS", default="pgpass")
    database: str = Field(alias="DB_NAME", default="prodadvert_db")


class MinioConfig(BaseModel):
    host: str = Field(alias="S3_HOST", default="http://REDACTED")
    port: int = Field(alias="S3_PORT", default=9000)
    username: str = Field(alias="S3_USER", default="minio_user")
    password: str = Field(alias="S3_PASS", default="minio_pass")
    bucket_name: str = "files"


class ModeConfig(BaseModel):
    debug_mode: bool = Field(alias="DEBUG", default=True)


class Config(BaseModel):
    postgres: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig(**os.environ)
    )
    s3: MinioConfig = Field(
        default_factory=lambda: MinioConfig(**os.environ)
    )
    mode: ModeConfig = Field(
        default_factory=lambda: ModeConfig(**os.environ)
    )
