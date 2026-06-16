from pydantic import BaseModel


class VideoInfoRequest(BaseModel):
    url: str


class VideoFormat(BaseModel):
    format_id: str
    ext: str
    resolution: str | None = None
    fps: float | None = None
    vcodec: str | None = None
    acodec: str | None = None
    filesize_approx: int | None = None
    label: str
    url: str


class VideoInfoResponse(BaseModel):
    title: str
    thumbnail: str | None = None
    duration: float | None = None
    uploader: str | None = None
    formats: list[VideoFormat]


class DownloadRequest(BaseModel):
    url: str
    format_id: str = "best"


class DownloadTaskResponse(BaseModel):
    task_id: str


class ProgressData(BaseModel):
    status: str  # extracting, downloading, merging, completed, failed
    percent: float = 0
    speed: float | None = None
    eta: float | None = None
    filename: str | None = None
    error: str | None = None


class TaskInfo(BaseModel):
    task_id: str
    url: str
    status: str
    filename: str | None = None
    created_at: float


class CookieRequest(BaseModel):
    cookies: str


class CookieStatus(BaseModel):
    has_cookies: bool
    size_bytes: int
