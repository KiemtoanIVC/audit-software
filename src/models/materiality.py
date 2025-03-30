from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

class UserType(Enum):
    BANK = "Ngân hàng"
    INVESTOR = "Nhà đầu tư"
    SHAREHOLDER = "Cổ đông"
    SUPPLIER = "Nhà cung cấp"
    CUSTOMER = "Khách hàng"
    GOVERNMENT = "Cơ quan nhà nước"

class Benchmark(Enum):
    TOTAL_ASSETS = "Tổng tài sản"
    EQUITY = "Vốn chủ sở hữu"
    REVENUE = "Doanh thu"
    PROFIT_BEFORE_TAX = "Lợi nhuận trước thuế"
    TOTAL_EXPENSES = "Tổng chi phí"

class RiskLevel(Enum):
    LOW = "Thấp"
    MEDIUM = "Trung bình"
    HIGH = "Cao"

@dataclass
class MaterialityResult:
    company_name: str
    tax_code: str
    calculation_date: datetime
    users: List[str]
    benchmark_type: str
    benchmark_value: float
    risk_level: str
    percentage: float
    overall_materiality: float
    performance_materiality: float
    threshold: float
    explanation: str 