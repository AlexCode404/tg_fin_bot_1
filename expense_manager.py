import datetime
import calendar
from sqlalchemy import extract, func
from database import get_session, Expense, Category

def add_expense(user_id, amount, category_name):
    """
    Add a new expense record
    
    Args:
        user_id: Telegram user ID
        amount: Expense amount
        category_name: Category name
        
    Returns:
        True if successful, False if category doesn't exist
    """
    session = get_session()
    
    # Check if category exists
    category = session.query(Category).filter(Category.name == category_name.lower()).first()
    
    if not category:
        session.close()
        return False
    
    # Create new expense
    expense = Expense(
        amount=float(amount),
        user_id=user_id,
        category_id=category.id
    )
    
    session.add(expense)
    session.commit()
    session.close()
    
    return True

def get_categories():
    """
    Get list of all available categories
    
    Returns:
        List of category names
    """
    session = get_session()
    categories = [cat.name for cat in session.query(Category).all()]
    session.close()
    
    return categories

def get_month_expenses(user_id, year=None, month=None):
    """
    Get all expenses for a specific month
    
    Args:
        user_id: Telegram user ID
        year: Year (default: current year)
        month: Month number 1-12 (default: current month)
        
    Returns:
        List of expenses with category information
    """
    if year is None or month is None:
        today = datetime.date.today()
        year = year or today.year
        month = month or today.month
    
    session = get_session()
    
    # Get all expenses for the specified month
    expenses = session.query(
        Expense, Category.name
    ).join(
        Category
    ).filter(
        Expense.user_id == user_id,
        extract('year', Expense.date) == year,
        extract('month', Expense.date) == month
    ).all()
    
    result = []
    for expense, category_name in expenses:
        result.append({
            'id': expense.id,
            'amount': expense.amount,
            'date': expense.date,
            'category': category_name
        })
    
    session.close()
    return result

def get_category_summary(user_id, year=None, month=None):
    """
    Get summary of expenses by category for a specific month
    
    Args:
        user_id: Telegram user ID
        year: Year (default: current year)
        month: Month number 1-12 (default: current month)
        
    Returns:
        Dictionary with category totals and grand total
    """
    if year is None or month is None:
        today = datetime.date.today()
        year = year or today.year
        month = month or today.month
    
    session = get_session()
    
    # Get sum of expenses by category
    category_totals = session.query(
        Category.name,
        func.sum(Expense.amount).label('total')
    ).join(
        Expense
    ).filter(
        Expense.user_id == user_id,
        extract('year', Expense.date) == year,
        extract('month', Expense.date) == month
    ).group_by(
        Category.name
    ).all()
    
    # Get total sum of all expenses
    total_expense = session.query(
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id,
        extract('year', Expense.date) == year,
        extract('month', Expense.date) == month
    ).scalar() or 0
    
    result = {
        'categories': {name: total for name, total in category_totals},
        'total': total_expense,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month]
    }
    
    session.close()
    return result 