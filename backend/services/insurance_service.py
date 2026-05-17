"""
Insurance Service — Business logic for product catalog and basic risk scoring.
"""
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.insurance_product import InsuranceProduct
from models.risk_data import RiskData
from models.enums import ProductCategory
from schemas.insurance import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)

def _calculate_basic_risk_score(db: Session, category: ProductCategory) -> float:
    """
    Tính toán điểm rủi ro cơ bản (thang điểm 1-10) dựa trên dữ liệu lịch sử.
    Đây là phiên bản MVP cho Phase 1. 
    """
    try:
        event_count = db.query(RiskData).filter(RiskData.product_category == category).count()
        base_score = 1.0
        calculated_score = base_score + (event_count / 50.0) * 9.0

        final_score = round(min(calculated_score, 10.0), 1)
        return final_score
    except Exception as e:
        logger.error(f"Lỗi khi tính risk score cho category {category}: {e}")
        return 5.0  


def _attach_risk_score(db: Session, product: InsuranceProduct) -> InsuranceProduct:
    """
    Helper function để gán thêm thuộc tính 'risk_score' vào object SQLAlchemy 
    trước khi parse qua Pydantic schema (vì DB table không có cột này).
    """
    score = _calculate_basic_risk_score(db, product.category)
    setattr(product, "risk_score", score)
    return product


def get_products(db: Session, active_only: bool = True) -> List[InsuranceProduct]:
    """Lấy danh sách tất cả sản phẩm bảo hiểm."""
    query = db.query(InsuranceProduct)
    if active_only:
        query = query.filter(InsuranceProduct.is_active == True)
        
    products = query.order_by(InsuranceProduct.created_at.desc()).all()
    return [_attach_risk_score(db, p) for p in products]


def get_product_by_id(db: Session, product_id: UUID) -> InsuranceProduct:
    """Lấy chi tiết một sản phẩm theo ID."""
    product = db.query(InsuranceProduct).filter(InsuranceProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance product not found",
        )
    
    return _attach_risk_score(db, product)


def create_product(db: Session, product_in: ProductCreate, admin_id: UUID) -> InsuranceProduct:
    """Tạo mới một gói bảo hiểm (Dành cho Admin)."""
    db_product = InsuranceProduct(
        **product_in.model_dump(),
        created_by=admin_id
    )
    
    db.add(db_product)
    try:
        db.commit()
        db.refresh(db_product)
        return _attach_risk_score(db, db_product)
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during product creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create insurance product.",
        )


def update_product(db: Session, product_id: UUID, product_in: ProductUpdate) -> InsuranceProduct:
    """Cập nhật thông tin gói bảo hiểm (Dành cho Admin)."""
    db_product = db.query(InsuranceProduct).filter(InsuranceProduct.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance product not found",
        )

    update_data = product_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_product, field, value)

    try:
        db.commit()
        db.refresh(db_product)
        return _attach_risk_score(db, db_product)
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during product update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update insurance product.",
        )


def update_product_status(db: Session, product_id: UUID, is_active: bool) -> InsuranceProduct:
    """Kích hoạt hoặc Hủy kích hoạt gói bảo hiểm (Dành cho Admin)."""
    db_product = db.query(InsuranceProduct).filter(InsuranceProduct.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance product not found",
        )

    db_product.is_active = is_active
    
    try:
        db.commit()
        db.refresh(db_product)
        return _attach_risk_score(db, db_product)
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during product status update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product status.",
        )