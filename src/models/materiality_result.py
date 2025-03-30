from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import os

@dataclass
class MaterialityResult:
    company_name: str
    tax_code: str
    calculation_date: datetime
    users: list
    benchmark_type: str
    benchmark_value: float
    audit_year: str
    risk_level: str
    percentage: float
    overall_materiality: float
    performance_materiality: float
    threshold: float
    explanation: str

class MaterialityResultManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path / 'results' / 'materiality'
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_result(self, result: MaterialityResult) -> Path:
        """Lưu kết quả tính toán MTY"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"MTY_{result.company_name}_{timestamp}.json"
        file_path = self.base_path / file_name

        # Chuyển đổi datetime thành string để có thể serialize
        result_dict = result.__dict__
        result_dict['calculation_date'] = result.calculation_date.isoformat()

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)

        return file_path 