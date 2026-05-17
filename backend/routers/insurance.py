"""
Insurance Router — API endpoints cho danh mục sản phẩm bảo hiểm.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Any
from uuid import UUID
from config.database import get_db
from middleware.auth import get_current_user, require_admin
from models.user import User

# Import Schemas và Service
from schemas.insurance import (
    ProductCreate,
    ProductUpdate,
    ProductStatusUpdate,
    ProductResponse,
    ProductListResponse,
)
from services import insurance_service

router = APIRouter(
    prefix="/products",
    tags=["Insurance Catalog"]
)


@router.get("", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
def list_products(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Lấy danh sách các sản phẩm bảo hiểm.
    - USER bình thường: Chỉ lấy được sản phẩm đang active (is_active = True).
    - ADMIN: Có thể truyền query `?include_inactive=true` để xem toàn bộ.
    """
    active_only = True
    if current_user.role == "ADMIN" and include_inactive:
        active_only = False
        
    products = insurance_service.get_products(db=db, active_only=active_only)
    
    return ProductListResponse(
        products=products,
        total=len(products)
    )


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Lấy chi tiết một sản phẩm bảo hiểm kèm theo Basic Risk Score.
    Bất kỳ user nào đã đăng nhập cũng có thể xem.
    """
    return insurance_service.get_product_by_id(db=db, product_id=product_id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    """
    Tạo một gói bảo hiểm mới (Chỉ dành cho ADMIN).
    Dữ liệu form động (parameters_schema) và luật (trigger_conditions) được truyền dưới dạng JSON.
    """
    return insurance_service.create_product(
        db=db, 
        product_in=product_in, 
        admin_id=current_admin.id
    )


@router.put("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id: UUID,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)  
) -> Any:
    """
    Cập nhật thông tin gói bảo hiểm (Chỉ dành cho ADMIN).
    """
    return insurance_service.update_product(db=db, product_id=product_id, product_in=product_in)


@router.patch("/{product_id}/status", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product_status(
    product_id: UUID,
    status_in: ProductStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)  
) -> Any:
    """
    Bật/Tắt trạng thái hoạt động của gói bảo hiểm (Chỉ dành cho ADMIN).
    """
    return insurance_service.update_product_status(
        db=db, 
        product_id=product_id, 
        is_active=status_in.is_active
    )