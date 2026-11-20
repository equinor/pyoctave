from importlib.metadata import PackageNotFoundError, version as _version

try:
    version = _version("pyoctave")
except PackageNotFoundError:
    version = "0.0.0"
