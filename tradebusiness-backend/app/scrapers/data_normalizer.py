"""
数据标准化器
将不同数据源的原始数据转换为统一格式
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.logger import get_logger

logger = get_logger(__name__)


class DataNormalizer:
    """
    数据标准化器
    将不同数据源的数据映射为统一的标准格式
    """

    # 国家代码映射
    COUNTRY_NAMES = {
        "NG": "Nigeria",
        "KE": "Kenya",
        "ZA": "South Africa",
        "GH": "Ghana",
        "EG": "Egypt",
        "US": "United States",
    }

    @classmethod
    def normalize_company(cls, raw_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        标准化公司数据

        Args:
            raw_data: 原始采集数据
            source: 数据源标识

        Returns:
            标准化后的数据
        """
        normalized = {
            "raw_data": raw_data,
            "data_source": source,
            "source_url": raw_data.get("source_url", raw_data.get("url", "")),
            "confidence_score": cls._calculate_confidence(raw_data, source),
        }

        # 提取公司名称
        normalized["company_name"] = cls._extract_company_name(raw_data)
        normalized["company_name_en"] = cls._extract_company_name_en(raw_data)

        # 提取位置信息
        normalized["country"], normalized["country_code"] = cls._extract_country(raw_data)
        normalized["city"] = cls._extract_city(raw_data)

        # 提取联系信息
        normalized["email"] = cls._extract_email(raw_data)
        normalized["phone"] = cls._extract_phone(raw_data)
        normalized["whatsapp"] = cls._extract_whatsapp(raw_data)
        normalized["website"] = cls._extract_website(raw_data)

        # 提取业务信息
        normalized["business_type"] = cls._extract_business_type(raw_data)
        normalized["description"] = cls._extract_description(raw_data)

        return normalized

    @classmethod
    def _calculate_confidence(cls, raw_data: Dict[str, Any], source: str) -> int:
        """计算数据可信度（0-100）"""
        score = 50  # 基础分

        # 根据数据源调整
        if source == "google":
            score += 20
        elif source == "directory":
            score += 15
        elif source == "specific_site":
            score += 25

        # 有邮箱加分
        if raw_data.get("email"):
            score += 10

        # 有网站加分
        if raw_data.get("website"):
            score += 10

        # 有电话加分
        if raw_data.get("phone"):
            score += 10

        return min(score, 100)

    @classmethod
    def _extract_company_name(cls, data: Dict[str, Any]) -> str:
        """提取公司名称"""
        # 尝试多个字段
        for field in ["company_name", "name", "title", "organization"]:
            if data.get(field):
                name = str(data[field]).strip()
                # 清理名称
                name = re.sub(r"\s+", " ", name)  # 多个空格转单个
                name = name.strip()
                if len(name) > 2:
                    return name

        return "Unknown Company"

    @classmethod
    def _extract_company_name_en(cls, data: Dict[str, Any]) -> Optional[str]:
        """提取英文名称"""
        for field in ["company_name_en", "name_en", "english_name"]:
            if data.get(field):
                return str(data[field]).strip()
        return None

    @classmethod
    def _extract_country(cls, data: Dict[str, Any]) -> tuple[str, str]:
        """提取国家和代码"""
        # 尝试获取国家代码
        country_code = data.get("country_code", "")
        country_name = data.get("country", "")

        # 如果有国家代码，获取国家名
        if country_code:
            return cls.COUNTRY_NAMES.get(country_code, country_name), country_code.upper()

        # 如果有国家名，尝试推断代码
        if country_name:
            # 反向查找
            for code, name in cls.COUNTRY_NAMES.items():
                if name.lower() in country_name.lower() or country_name.lower() in name.lower():
                    return name, code

        # 默认返回
        return "Unknown", "XX"

    @classmethod
    def _extract_city(cls, data: Dict[str, Any]) -> Optional[str]:
        """提取城市"""
        for field in ["city", "address_city", "location_city"]:
            if data.get(field):
                return str(data[field]).strip()
        return None

    @classmethod
    def _extract_email(cls, data: Dict[str, Any]) -> Optional[str]:
        """提取邮箱"""
        email = data.get("email", "")
        if email and "@" in email:
            # 简单的邮箱验证
            email = email.strip().lower()
            if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                return email
        return None

    @classmethod
    def _extract_phone(cls, data: Dict[str, Any]) -> Optional[str]:
        """提取电话"""
        phone = data.get("phone", "")
        if phone:
            # 清理电话号码
            phone = re.sub(r"[^\d+\+]", "", str(phone))
            if len(phone) >= 7:
                return phone
        return None

    @classmethod
    def _extract_whatsapp(cls, data: Dict[str, Any]) -> Optional[str]:
        """提取WhatsApp"""
        whatsapp = data.get("whatsapp", "")
        if whatsapp:
            return re.sub(r"[^\d+\+]", "", str(whatsapp))
        return None

    @classmethod
    def _extract_website(cls, data: Dict[str, Any]) -> Optional[str]:
        """提取网站"""
        website = data.get("website", "")
        if website:
            website = website.strip()
            if not website.startswith("http"):
                website = "https://" + website
            return website
        return None

    @classmethod
    def _extract_business_type(cls, data: Dict[str, Any]) -> Optional[str]:
        """提取业务类型"""
        business_type = data.get("business_type", data.get("type", ""))
        if business_type:
            return str(business_type).strip()
        return None

    @classmethod
    def _extract_description(cls, data: Dict[str, Any]) -> Optional[str]:
        """提取描述"""
        for field in ["description", "about", "notes", "details"]:
            desc = data.get(field)
            if desc:
                desc = str(desc).strip()
                if len(desc) > 10:
                    return desc[:500]  # 限制长度
        return None


class DuplicateDetector:
    """
    重复数据检测器
    检测与已有数据重复的线索
    """

    @staticmethod
    def calculate_similarity(company_a: Dict[str, Any], company_b: Dict[str, Any]) -> int:
        """
        计算两个公司记录的相似度（0-100）

        Args:
            company_a: 公司A数据
            company_b: 公司B数据

        Returns:
            相似度分数
        """
        score = 0

        # 1. 公司名称相似度（权重50%）
        name_a = company_a.get("company_name", "").lower()
        name_b = company_b.get("company_name", "").lower()
        if name_a and name_b:
            if name_a == name_b:
                score += 50
            elif name_a in name_b or name_b in name_a:
                score += 30

        # 2. 邮箱相似度（权重30%）
        email_a = company_a.get("email", "").lower()
        email_b = company_b.get("email", "").lower()
        if email_a and email_b:
            if email_a == email_b:
                score += 30
            elif email_a in email_b or email_b in email_a:
                score += 15

        # 3. 网站相似度（权重20%）
        web_a = company_a.get("website", "").lower()
        web_b = company_b.get("website", "").lower()
        if web_a and web_b:
            if web_a == web_b:
                score += 20
            elif web_a in web_b or web_b in web_a:
                score += 10

        # 4. 电话相似度（权重10%）
        phone_a = company_a.get("phone", "")
        phone_b = company_b.get("phone", "")
        if phone_a and phone_b:
            if phone_a.replace("+", "") == phone_b.replace("+", ""):
                score += 10
            elif phone_a in phone_b or phone_b in phone_a:
                score += 5

        return score

    @staticmethod
    def is_duplicate(
        normalized_data: Dict[str, Any], existing_leads: List[Dict[str, Any]], threshold: int = 70
    ) -> Optional[str]:
        """
        检查是否重复

        Args:
            normalized_data: 标准化后的数据
            existing_leads: 已存在的线索列表
            threshold: 相似度阈值

        Returns:
            如果重复，返回重复记录ID；否则返回None
        """
        for lead in existing_leads:
            similarity = DuplicateDetector.calculate_similarity(normalized_data, lead)
            if similarity >= threshold:
                return lead.get("id")

        return None
