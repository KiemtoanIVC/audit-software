import xml.etree.ElementTree as ET
from typing import Dict, Any

class FinancialDataProcessor:
    def __init__(self):
        self.company_info = None
        self.key_metrics = None
        self.namespaces = {
            'ns': 'http://kekhaithue.gdt.gov.vn/TKhaiThue'
        }

    def load_xml_data(self, file_path: str) -> bool:
        """Load và xử lý dữ liệu từ file XML"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Lấy thông tin công ty
            self.company_info = self._get_company_info(root)
            
            # Lấy các chỉ tiêu tài chính
            self.key_metrics = self._get_key_metrics(root)
            
            return True
        except Exception as e:
            print(f"Lỗi khi xử lý file XML: {str(e)}")
            return False

    def _get_company_info(self, root: ET.Element) -> Dict[str, str]:
        """Lấy thông tin công ty từ XML"""
        try:
            nnt = root.find('.//ns:NNT', self.namespaces)
            if nnt is None:
                return {}

            # Lấy thông tin cơ bản
            ten_nnt = nnt.find('ns:tenNNT', self.namespaces)
            mst = nnt.find('ns:mst', self.namespaces)
            
            # Lấy kỳ kê khai
            ky_khai = root.find('.//ns:KyKKhaiThue', self.namespaces)
            tu_ngay = ky_khai.find('ns:kyKKhaiTuNgay', self.namespaces) if ky_khai is not None else None
            den_ngay = ky_khai.find('ns:kyKKhaiDenNgay', self.namespaces) if ky_khai is not None else None

            return {
                'name': ten_nnt.text if ten_nnt is not None else "",
                'tax_code': mst.text if mst is not None else "",
                'period_from': tu_ngay.text if tu_ngay is not None else "",
                'period_to': den_ngay.text if den_ngay is not None else ""
            }
        except Exception as e:
            print(f"Lỗi khi lấy thông tin công ty: {str(e)}")
            return {}

    def _get_key_metrics(self, root: ET.Element) -> Dict[str, float]:
        """Lấy các chỉ tiêu tài chính chính từ XML"""
        try:
            # Tìm phần tử CDKT
            cdkt = root.find('.//ns:CDKT_HoatDongLienTuc', self.namespaces)
            if cdkt is None:
                return {}

            so_cuoi_nam = cdkt.find('ns:SoCuoiNam', self.namespaces)
            if so_cuoi_nam is None:
                return {}

            # Lấy các chỉ tiêu từ CĐKT
            total_assets = self._get_number(so_cuoi_nam, 'ct270')  # Tổng tài sản
            equity = self._get_number(so_cuoi_nam, 'ct410')  # Vốn chủ sở hữu

            # Lấy các chỉ tiêu từ KQKD
            kqkd = root.find('.//ns:PL_KQHDSXKD', self.namespaces)
            if kqkd is None:
                return {}

            nam_nay = kqkd.find('ns:NamNay', self.namespaces)
            if nam_nay is None:
                return {}

            revenue = self._get_number(nam_nay, 'ct01')  # Doanh thu
            profit_before_tax = self._get_number(nam_nay, 'ct50')  # Lợi nhuận trước thuế
            
            # Tính tổng chi phí
            total_expenses = (
                self._get_number(nam_nay, 'ct11') +  # Giá vốn hàng bán
                self._get_number(nam_nay, 'ct25') +  # Chi phí bán hàng
                self._get_number(nam_nay, 'ct26')    # Chi phí quản lý
            )

            return {
                'total_assets': total_assets,
                'equity': equity,
                'revenue': revenue,
                'profit_before_tax': profit_before_tax,
                'total_expenses': total_expenses
            }
        except Exception as e:
            print(f"Lỗi khi lấy chỉ tiêu tài chính: {str(e)}")
            return {}

    def _get_number(self, element: ET.Element, code: str) -> float:
        """Chuyển đổi giá trị từ XML sang số"""
        try:
            value = element.find(f'ns:{code}', self.namespaces)
            if value is not None and value.text:
                return float(value.text)
            return 0
        except (ValueError, TypeError):
            return 0

    def get_key_metrics(self) -> Dict[str, float]:
        """Trả về các chỉ tiêu tài chính đã xử lý"""
        return self.key_metrics if self.key_metrics else {} 