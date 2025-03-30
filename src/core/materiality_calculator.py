from typing import List, Optional
from ..models.materiality import UserType, Benchmark, RiskLevel
from enum import Enum

class UserType(Enum):
    SHAREHOLDER = "Cổ đông, nhà đầu tư"
    BANK = "Ngân hàng, tổ chức tín dụng"
    GOVERNMENT = "Cơ quan nhà nước"
    MANAGEMENT = "Ban điều hành"
    OTHER = "Đối tượng khác"

class Benchmark(Enum):
    TOTAL_ASSETS = "Tổng tài sản"
    EQUITY = "Vốn chủ sở hữu"
    REVENUE = "Doanh thu"
    PROFIT_BEFORE_TAX = "Lợi nhuận trước thuế"
    TOTAL_EXPENSES = "Tổng chi phí"

class AuditYear(Enum):
    FIRST_YEAR = "Năm đầu tiên"
    SUBSEQUENT_YEAR = "Năm tiếp theo"

class RiskLevel(Enum):
    LOW = "Thấp"
    MEDIUM = "Trung bình"
    HIGH = "Cao"

class MaterialityCalculator:
    def __init__(self):
        self.selected_users = []
        self.selected_benchmark = None
        self.benchmark_value = 0
        self.benchmark_percentage = 0
        self.audit_year = None
        self.risk_level = None
        self.overall_materiality = 0
        self.performance_materiality = 0
        self.threshold = 0

    def set_users(self, users):
        self.selected_users = users

    def set_benchmark(self, benchmark, value):
        self.selected_benchmark = benchmark
        self.benchmark_value = value

    def set_audit_parameters(self, year, risk):
        self.audit_year = year
        self.risk_level = risk

    def get_suggested_percentage(self):
        """Tính tỷ lệ % đề xuất dựa trên tiêu chí và mức độ rủi ro"""
        if not self.selected_benchmark or not self.risk_level:
            return None

        base_percentages = {
            Benchmark.TOTAL_ASSETS: 1.0,
            Benchmark.EQUITY: 2.0,
            Benchmark.REVENUE: 0.5,
            Benchmark.PROFIT_BEFORE_TAX: 5.0,
            Benchmark.TOTAL_EXPENSES: 0.5
        }

        risk_factors = {
            RiskLevel.LOW: 1.2,
            RiskLevel.MEDIUM: 1.0,
            RiskLevel.HIGH: 0.8
        }

        base = base_percentages.get(self.selected_benchmark, 1.0)
        factor = risk_factors.get(self.risk_level, 1.0)
        
        return round(base * factor, 2)

    def calculate_materiality(self, custom_percentage=None):
        """Tính toán các mức trọng yếu"""
        if custom_percentage is not None:
            self.benchmark_percentage = custom_percentage
        else:
            self.benchmark_percentage = self.get_suggested_percentage()

        # Tính MTY tổng thể
        self.overall_materiality = self.benchmark_value * (self.benchmark_percentage / 100)
        
        # Tính MTY thực hiện (75% MTY tổng thể)
        self.performance_materiality = self.overall_materiality * 0.75
        
        # Tính ngưỡng sai sót không đáng kể (5% MTY tổng thể)
        self.threshold = self.overall_materiality * 0.05

    def get_explanation(self):
        """Tạo giải thích cho kết quả tính toán"""
        if not self.overall_materiality:
            return "Chưa tính toán mức trọng yếu"

        explanation = f"""
1. Xác định mức trọng yếu tổng thể:
- Tiêu chí được chọn: {self.selected_benchmark.value}
- Giá trị: {self.benchmark_value:,.0f} VND
- Tỷ lệ áp dụng: {self.benchmark_percentage}%
- Mức trọng yếu tổng thể: {self.overall_materiality:,.0f} VND

2. Xác định mức trọng yếu thực hiện:
- 75% mức trọng yếu tổng thể
- Giá trị: {self.performance_materiality:,.0f} VND

3. Ngưỡng sai sót không đáng kể:
- 5% mức trọng yếu tổng thể
- Giá trị: {self.threshold:,.0f} VND
"""
        return explanation 