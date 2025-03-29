from enum import Enum
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import json

class FormStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class FormStage(Enum):
    PLANNING = "PLANNING"
    EXECUTION = "EXECUTION" 
    REPORTING = "REPORTING"

class AuditForm:
    def __init__(self):
        self.id: str = ""
        self.code: str = ""  # A110, A120,...
        self.name: str = ""
        self.stage: FormStage = FormStage.PLANNING
        self.status: FormStatus = FormStatus.NOT_STARTED
        self.data: dict = {}
        self.attachments: List[str] = []
        self.created_by: str = ""
        self.updated_by: str = ""
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()

    def save(self, job_path: Path):
        """Lưu form vào thư mục job"""
        form_path = job_path / "MauBieu" / f"{self.code}.json"
        with open(form_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
