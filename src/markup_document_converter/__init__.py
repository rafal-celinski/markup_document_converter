from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("markup-document-converter")
except PackageNotFoundError:
    __version__ = "0.0.0"
