import unittest
import os
import sys

# Добавление родительского каталога в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TOKEN, CATEGORIES
from database import Category, Expense, get_session

class TestConfig(unittest.TestCase):
    def test_token_exists(self):
        """Проверка наличия токена"""
        self.assertIsNotNone(TOKEN)
        self.assertNotEqual(TOKEN, "")
    
    def test_categories_exist(self):
        """Проверка наличия категорий"""
        self.assertIsInstance(CATEGORIES, list)
        self.assertGreater(len(CATEGORIES), 0)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Настройка тестового окружения"""
        self.session = get_session()
        
    def tearDown(self):
        """Очистка после тестов"""
        self.session.close()
        
    def test_categories_initialized(self):
        """Проверка инициализации категорий"""
        categories = self.session.query(Category).all()
        self.assertGreater(len(categories), 0)
        
        category_names = [cat.name for cat in categories]
        for expected_category in CATEGORIES:
            self.assertIn(expected_category, category_names)

if __name__ == '__main__':
    unittest.main() 