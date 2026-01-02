import itertools
from typing import Annotated, Any, Iterable, Optional, Union

from pydantic import BaseModel, BeforeValidator

from .error import ErrorMessage


class MagnetErrorURI(BaseModel):
    magnet: str
    error: ErrorMessage


class MagnetErrorFile(BaseModel):
    file: str
    error: ErrorMessage


class MagnetUploadURI(BaseModel):
    magnet: str
    name: str
    id: int
    hash: str
    size: int
    ready: bool


class MagnetUploadFile(BaseModel):
    file: str
    name: str
    id: int
    hash: str
    size: int
    ready: bool


class MagnetInstantURI(BaseModel):
    magnet: str
    hash: str
    instant: bool


class MagnetLinkEntryNormal(BaseModel):
    path: str
    fname: str
    size: int


class MagnetLinkEntry(BaseModel):
    n: str
    e: Optional[list["MagnetLinkEntry"]] = None
    s: Optional[int] = None

    @classmethod
    def parse(cls, v: dict[str, Any]):
        if "e" not in v:
            return MagnetLinkEntry(**v)
        v["e"] = [cls.parse(f) for f in v["e"]]
        return MagnetLinkEntry(**v)

    def walk(self, path: str) -> Iterable[MagnetLinkEntryNormal]:
        if self.e is not None:
            for entry in self.e:
                yield from entry.walk(path + self.n + "/")
        else:
            yield MagnetLinkEntryNormal(path=path, fname=self.n, size=self.s or 0)


class MagnetLink(BaseModel):
    @staticmethod
    def parse_files(x: list[Any]):
        return list(itertools.chain(*(MagnetLinkEntry.parse(f).walk("") for f in x)))

    link: str
    filename: str
    size: int
    files: Annotated[list[MagnetLinkEntryNormal], BeforeValidator(parse_files)]


class MagnetStatus(BaseModel):
    id: int
    filename: str
    size: int
    hash: str
    status: str
    statusCode: int
    downloaded: Optional[int] = None
    uploaded: Optional[int] = None
    seeders: Optional[int] = None
    downloadSpeed: Optional[int] = None
    uploadSpeed: Optional[int] = None
    uploadDate: int
    completionDate: int
    type: str
    notified: bool
    version: int


class MagnetFileEntryNormal(BaseModel):
    path: str
    fname: str
    size: int
    link: str


class MagnetFileEntry(BaseModel):
    n: str
    e: Optional[list["MagnetFileEntry"]] = None
    s: Optional[int] = None
    l: Optional[str] = None

    @classmethod
    def parse(cls, v: dict[str, Any]):
        if "e" not in v:
            return MagnetFileEntry(**v)
        v["e"] = [cls.parse(f) for f in v["e"]]
        return MagnetFileEntry(**v)

    def walk(self, path: str) -> Iterable[MagnetFileEntryNormal]:
        if self.e is not None:
            for entry in self.e:
                yield from entry.walk(path + self.n + "/")
        else:
            assert self.l
            yield MagnetFileEntryNormal(path=path, fname=self.n, size=self.s or 0, link=self.l)


class MagnetFiles(BaseModel):
    @staticmethod
    def parse_files(x: list[Any]):
        return list(itertools.chain(*(MagnetFileEntry.parse(f).walk("") for f in x)))

    id: int
    files: Annotated[list[MagnetFileEntryNormal], BeforeValidator(parse_files)]


class MagnetUploadFiles(BaseModel):
    files: list[Union[MagnetUploadFile, MagnetErrorFile]]


class MagnetUploadURIs(BaseModel):
    magnets: list[Union[MagnetUploadURI, MagnetErrorURI]]


class MagnetInstants(BaseModel):
    magnets: list[Union[MagnetInstantURI, MagnetErrorURI]]


class MagnetStatusesList(BaseModel):
    magnets: list[MagnetStatus]


class MagnetStatusesDict(BaseModel):
    magnets: dict[str, MagnetStatus]


class MagnetStatusesOne(BaseModel):
    magnets: MagnetStatus


class MagnetFilesList(BaseModel):
    magnets: list[MagnetFiles]


class MagnetFilesDict(BaseModel):
    magnets: dict[str, MagnetFiles]


class MagnetFilesOne(BaseModel):
    magnets: MagnetFiles


MagnetStatusUnion = MagnetStatusesDict | MagnetStatusesList | MagnetStatusesOne
MagnetFilesUnion = MagnetFilesDict | MagnetFilesList | MagnetFilesOne
