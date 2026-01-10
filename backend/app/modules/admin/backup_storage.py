from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Protocol


class BackupStorage(Protocol):
    def root(self) -> Path: ...

    def index_path(self) -> Path: ...

    def backup_dir(self, backup_id: str) -> Path: ...

    def ensure_root(self) -> None: ...

    def delete_backup(self, backup_id: str) -> None: ...


@dataclass(frozen=True)
class LocalBackupStorage:
    root_path: Path

    def root(self) -> Path:
        return self.root_path

    def index_path(self) -> Path:
        return self.root_path / "index.json"

    def backup_dir(self, backup_id: str) -> Path:
        return self.root_path / backup_id

    def ensure_root(self) -> None:
        self.root_path.mkdir(parents=True, exist_ok=True)

    def delete_backup(self, backup_id: str) -> None:
        folder = self.backup_dir(backup_id).resolve()
        root = self.root_path.resolve()
        if folder.exists() and folder.is_dir() and folder.parent == root:
            shutil.rmtree(folder)
