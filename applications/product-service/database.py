import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import ARRAY

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./products.db")

# Handle sqlite vs postgres
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=False)
    description = Column(Text)
    scent_profile = Column(Text)  # JSON string for sqlite compat
    top_notes = Column(Text)
    heart_notes = Column(Text)
    base_notes = Column(Text)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    category = Column(String(50))
    size_ml = Column(Integer)
    in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer, default=0)
    rating = Column(Float)
    review_count = Column(Integer, default=0)
    image_url = Column(String(500))
    is_new = Column(Boolean, default=False)
    is_bestseller = Column(Boolean, default=False)
    gender = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "description": self.description,
            "scent_profile": json.loads(self.scent_profile) if self.scent_profile else [],
            "top_notes": json.loads(self.top_notes) if self.top_notes else [],
            "heart_notes": json.loads(self.heart_notes) if self.heart_notes else [],
            "base_notes": json.loads(self.base_notes) if self.base_notes else [],
            "price": self.price,
            "original_price": self.original_price,
            "category": self.category,
            "size_ml": self.size_ml,
            "in_stock": self.in_stock,
            "stock_quantity": self.stock_quantity,
            "rating": self.rating,
            "review_count": self.review_count,
            "image_url": self.image_url,
            "is_new": self.is_new,
            "is_bestseller": self.is_bestseller,
            "gender": self.gender,
        }


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
