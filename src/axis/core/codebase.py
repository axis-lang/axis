from typing import Optional, Self
from protobase import Record
from pathlib import Path
import semver

CODEBASES = [
    Path.cwd() / "src",# Strategy: Workspace
    Path.home() / ".axis" / "src", # Strategy: Local cache
]

class Version(Record, frozen=True):
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    @classmethod
    def from_str(cls, ver: str) -> Self:
        parsed = semver.Version.parse(ver)
        return cls(
            major=parsed.major,
            minor=parsed.minor,
            patch=parsed.patch,
            prerelease=parsed.prerelease,
            build=parsed.build,
        )


class SeedPackage(Record, frozen=True):
    name: str
    version: Optional[Version] = None
    # url: Optional[str] = None

seed_packages: set[str] = set()

