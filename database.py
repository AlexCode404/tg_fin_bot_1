from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from config import DATABASE_URI, CATEGORIES

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    
    expenses = relationship("Expense", back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name}>"

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, default=datetime.date.today, nullable=False)
    user_id = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    category = relationship("Category", back_populates="expenses")
    
    def __repr__(self):
        return f"<Expense {self.amount} in {self.category.name} on {self.date}>"

def init_db():
    """Initialize the database, create tables and populate categories"""
    Base.metadata.create_all(engine)
    
    # Add categories if they don't exist
    session = Session()
    existing_categories = {cat.name for cat in session.query(Category).all()}
    
    for category_name in CATEGORIES:
        if category_name not in existing_categories:
            session.add(Category(name=category_name))
    
    session.commit()
    session.close()

def get_session():
    """Get a new database session"""
    return Session()

# Initialize database when module is imported
init_db() 