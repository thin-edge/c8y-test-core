
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("c8y_test_core")
except PackageNotFoundError:
    pass
