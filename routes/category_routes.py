from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import db_dependecies
from models.category import Category
from schemas.category_schema import CategoryCreate, CategoryResponse
from utils.role import get_current_user
from models.users import User

router = APIRouter(tags=["Categories"])


@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents and admins can create categories",
        )
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
