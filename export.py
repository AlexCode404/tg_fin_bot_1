import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import datetime
import calendar
from expense_manager import get_month_expenses, get_category_summary

def export_to_csv(user_id, year=None, month=None):
    """
    Export expense data to CSV file
    
    Args:
        user_id: Telegram user ID
        year: Year (default: current year)
        month: Month number 1-12 (default: current month)
        
    Returns:
        Path to the created CSV file
    """
    if year is None or month is None:
        today = datetime.date.today()
        year = year or today.year
        month = month or today.month
    
    expenses = get_month_expenses(user_id, year, month)
    
    # Create directory for exports if it doesn't exist
    os.makedirs('exports', exist_ok=True)
    
    filename = f"exports/expenses_{user_id}_{year}_{month}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['date', 'category', 'amount']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for expense in expenses:
            writer.writerow({
                'date': expense['date'],
                'category': expense['category'],
                'amount': expense['amount']
            })
    
    return filename

def export_to_pdf(user_id, year=None, month=None):
    """
    Export expense data to PDF file with summary and chart
    
    Args:
        user_id: Telegram user ID
        year: Year (default: current year)
        month: Month number 1-12 (default: current month)
        
    Returns:
        Path to the created PDF file
    """
    if year is None or month is None:
        today = datetime.date.today()
        year = year or today.year
        month = month or today.month
    
    # Get data
    expenses = get_month_expenses(user_id, year, month)
    summary = get_category_summary(user_id, year, month)
    
    month_name = calendar.month_name[month]
    
    # Create directory for exports if it doesn't exist
    os.makedirs('exports', exist_ok=True)
    
    # Create pie chart for categories
    if summary['categories']:
        plt.figure(figsize=(10, 6))
        plt.pie(
            summary['categories'].values(), 
            labels=summary['categories'].keys(),
            autopct='%1.1f%%'
        )
        plt.title(f'Расходы по категориям за {month_name} {year}')
        chart_filename = f"exports/chart_{user_id}_{year}_{month}.png"
        plt.savefig(chart_filename)
        plt.close()
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Отчет о расходах за {month_name} {year}', 0, 1, 'C')
    pdf.ln(10)
    
    # Add summary
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Сводка расходов по категориям:', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    for category, amount in summary['categories'].items():
        pdf.cell(100, 8, category, 0)
        pdf.cell(0, 8, f"{amount:.2f}", 0, 1)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, 'Общая сумма расходов:')
    pdf.cell(0, 10, f"{summary['total']:.2f}", 0, 1)
    pdf.ln(10)
    
    # Add chart if it exists
    if summary['categories']:
        pdf.image(chart_filename, x=10, y=None, w=180)
        pdf.ln(10)
    
    # Add detailed expenses
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Детализация расходов:', 0, 1)
    pdf.ln(5)
    
    # Add table header
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 10, 'Дата', 1)
    pdf.cell(70, 10, 'Категория', 1)
    pdf.cell(70, 10, 'Сумма', 1)
    pdf.ln()
    
    # Add table rows
    pdf.set_font('Arial', '', 12)
    for expense in expenses:
        pdf.cell(50, 10, expense['date'].strftime('%Y-%m-%d'), 1)
        pdf.cell(70, 10, expense['category'], 1)
        pdf.cell(70, 10, f"{expense['amount']:.2f}", 1)
        pdf.ln()
    
    # Save PDF
    filename = f"exports/expenses_{user_id}_{year}_{month}.pdf"
    pdf.output(filename)
    
    # Remove chart file after using it
    if summary['categories'] and os.path.exists(chart_filename):
        os.remove(chart_filename)
    
    return filename 