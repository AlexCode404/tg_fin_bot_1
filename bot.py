#!/usr/bin/env python
# coding: utf-8

import logging
import datetime
import calendar
import re
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import os

from config import TOKEN, CATEGORIES
from expense_manager import add_expense, get_categories, get_category_summary
from export import export_to_csv, export_to_pdf

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Command handlers
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(
        f'Привет, {user.first_name}!\n\n'
        'Я бот для учета расходов. Вот мои команды:\n\n'
        '/add <сумма> <категория> - добавить расход\n'
        '/stats [месяц] - сводка расходов за месяц\n'
        '/categories - список доступных категорий\n'
        '/export [месяц] - выгрузка транзакций в CSV/PDF'
    )

def add_cmd(update: Update, context: CallbackContext) -> None:
    """Add a new expense."""
    user_id = update.effective_user.id
    
    # Check if arguments are provided
    if not context.args or len(context.args) < 2:
        update.message.reply_text(
            'Пожалуйста, укажите сумму и категорию.\n'
            'Пример: /add 100 food'
        )
        return
    
    # Parse amount and category
    try:
        amount = float(context.args[0])
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        update.message.reply_text('Пожалуйста, укажите корректную сумму.')
        return
    
    category = context.args[1].lower()
    
    # Add expense to database
    success = add_expense(user_id, amount, category)
    
    if success:
        update.message.reply_text(
            f'✅ Расход добавлен: {amount} в категории "{category}"'
        )
    else:
        categories = get_categories()
        update.message.reply_text(
            f'❌ Категория "{category}" не найдена.\n'
            f'Доступные категории: {", ".join(categories)}'
        )

def stats_cmd(update: Update, context: CallbackContext) -> None:
    """Show statistics for a month."""
    user_id = update.effective_user.id
    
    # Parse month argument if provided
    year, month = parse_month_arg(context.args)
    
    # Get expense summary
    summary = get_category_summary(user_id, year, month)
    
    if not summary['categories']:
        update.message.reply_text(
            f'❌ Нет расходов за {summary["month_name"]} {summary["year"]}.'
        )
        return
    
    # Prepare response message
    response = f'📊 *Расходы за {summary["month_name"]} {summary["year"]}*\n\n'
    
    for category, amount in summary['categories'].items():
        percent = (amount / summary['total']) * 100
        response += f'*{category}*: {amount:.2f} ({percent:.1f}%)\n'
    
    response += f'\n*Общая сумма*: {summary["total"]:.2f}'
    
    update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

def categories_cmd(update: Update, context: CallbackContext) -> None:
    """Show available categories."""
    categories = get_categories()
    
    update.message.reply_text(
        '📋 *Доступные категории*:\n\n' + 
        '\n'.join([f'• {category}' for category in categories]),
        parse_mode=ParseMode.MARKDOWN
    )

def export_cmd(update: Update, context: CallbackContext) -> None:
    """Export expenses to CSV/PDF."""
    user_id = update.effective_user.id
    
    # Parse month argument if provided
    year, month = parse_month_arg(context.args)
    
    # Check if format is specified
    format_type = 'both'
    if context.args and context.args[-1].lower() in ['csv', 'pdf']:
        format_type = context.args[-1].lower()
    
    update.message.reply_text('📤 Подготовка отчета, пожалуйста подождите...')
    
    try:
        if format_type in ['both', 'csv']:
            csv_path = export_to_csv(user_id, year, month)
            with open(csv_path, 'rb') as file:
                update.message.reply_document(
                    document=file,
                    filename=f'expenses_{year}_{month}.csv',
                    caption=f'📊 Расходы за {calendar.month_name[month]} {year} (CSV)'
                )
        
        if format_type in ['both', 'pdf']:
            pdf_path = export_to_pdf(user_id, year, month)
            with open(pdf_path, 'rb') as file:
                update.message.reply_document(
                    document=file,
                    filename=f'expenses_{year}_{month}.pdf',
                    caption=f'📊 Расходы за {calendar.month_name[month]} {year} (PDF)'
                )
    except Exception as e:
        logger.error(f"Export error: {e}")
        update.message.reply_text(f'❌ Ошибка при создании отчета: {str(e)}')

def help_cmd(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        '🔍 *Справка по командам*\n\n'
        '/add <сумма> <категория> - добавить расход\n'
        'Пример: `/add 100 food`\n\n'
        '/stats [месяц] - сводка расходов за месяц\n'
        'Пример: `/stats 2023-05` или просто `/stats`\n\n'
        '/categories - список доступных категорий\n\n'
        '/export [месяц] [формат] - выгрузка транзакций\n'
        'Пример: `/export 2023-05 pdf` или `/export csv`\n'
        'Форматы: csv, pdf (по умолчанию - оба)',
        parse_mode=ParseMode.MARKDOWN
    )

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors caused by updates."""
    logger.error(f'Update {update} caused error: {context.error}')
    
    if update and update.effective_message:
        update.effective_message.reply_text(
            '❌ Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.'
        )

# Helper functions
def parse_month_arg(args):
    """Parse month argument in format YYYY-MM or return current month."""
    today = datetime.date.today()
    year = today.year
    month = today.month
    
    if args:
        # Try to parse first argument as YYYY-MM
        match = re.match(r'^(\d{4})-(\d{1,2})$', args[0])
        if match:
            try:
                year = int(match.group(1))
                month = int(match.group(2))
                if month < 1 or month > 12:
                    month = today.month
            except ValueError:
                pass
    
    return year, month

def main() -> None:
    """Start the bot."""
    # Create the Updater with bot token
    updater = Updater(TOKEN)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_cmd))
    dispatcher.add_handler(CommandHandler("add", add_cmd))
    dispatcher.add_handler(CommandHandler("stats", stats_cmd))
    dispatcher.add_handler(CommandHandler("categories", categories_cmd))
    dispatcher.add_handler(CommandHandler("export", export_cmd))
    
    # Register error handler
    dispatcher.add_error_handler(error_handler)
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until the user presses Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main() 