from dataclasses import dataclass

from .files import InputVirtualFile, OutputVirtualFile


@dataclass
class ArgsWithPaths:
    input: str
    output: str
    size: str = ""
    version: int = 2
    outdir: str = ""


@dataclass
class ArgsWithFiles(ArgsWithPaths):
    input: InputVirtualFile
    output: OutputVirtualFile
