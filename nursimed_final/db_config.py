# db_config.py - تنظیمات اتصال به PostgreSQL
# لطفاً پسورد دیتابیس خود را در خط زیر وارد کنید

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'nursimed_db',
    'user': 'postgres',
    'password': 'YOUR_PASSWORD_HERE'  # <--- رمز عبور پستگرس خود را اینجا بنویسید
}

# مشخصات اکانت ادمین پیش‌فرض
ADMIN_EMAIL = "a@gmail.com"
ADMIN_PASS = "1234"
