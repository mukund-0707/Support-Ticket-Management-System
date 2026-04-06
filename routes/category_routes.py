from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import db_dependecies
from models.category import Category
from schemas.category_schema import CategoryCreate, CategoryResponse
from utils.role import get_current_user
from models.users import User
from decorators.ticket_decorators import require_roles

router = APIRouter(tags=["Categories"])


@router.post("/categories", response_model=CategoryResponse)
@require_roles(["admin"])
def create_category(
    category: CategoryCreate,
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    if db.query(Category).filter(Category.name == category.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists",
        )
    new_category = Category(name=category.name, description=category.description)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category
