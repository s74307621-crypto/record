#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سرور ساده پایتون برای سایت نرسیمد
بدون استفاده از فریم‌ورک - مناسب برای دانشجویان تازه‌کار
"""

import http.server
import socketserver
import json
import urllib.parse
import psycopg2
from db_config import DB_CONFIG
from datetime import datetime

# اتصال به دیتابیس
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# ایجاد جداول دیتابیس
def create_tables():
    conn = get_db_connection()
    if not conn:
        print("Cannot connect to database. Please check db_config.py")
        return
    
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول محصولات (کتاب‌ها)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            image_url VARCHAR(500),
            category VARCHAR(100),
            author VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول مقالات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            excerpt TEXT,
            author VARCHAR(255),
            image_url VARCHAR(500),
            category VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول پادکست‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS podcasts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            audio_url VARCHAR(500),
            duration VARCHAR(50),
            image_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول دوره‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2),
            image_url VARCHAR(500),
            instructor VARCHAR(255),
            duration VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول سبد خرید
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول سفارشات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            user_id INTEGER REFERENCES users(id),
            total_amount DECIMAL(10, 2),
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول تماس با ما
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    
    # اضافه کردن داده‌های نمونه اگر خالی باشد
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('آناتومی گری', 'کامل‌ترین مرجع آناتومی بدن انسان', 450000, '/static/images/product1.jpg', 'کتاب تخصصی', 'هنری گری'),
            ('فیزیولوژی پزشکی گایتون', 'مرجع کامل فیزیولوژی انسانی', 520000, '/static/images/product2.jpg', 'کتاب تخصصی', 'آرتور گایتون'),
            ('داروشناسی کاتزونگ', 'اصول فارماکولوژی بالینی', 380000, '/static/images/product3.jpg', 'کتاب تخصصی', 'برترام کاتزونگ'),
            ('کمک‌های اولیه', 'راهنمای جامع کمک‌های اولیه و امداد', 125000, '/static/images/product4.jpg', 'کتاب عمومی', 'سازمان هلال احمر'),
            ('تغذیه در سلامت', 'اصول تغذیه سالم برای عموم', 95000, '/static/images/product5.jpg', 'کتاب عمومی', 'دکتر احمدی'),
        ]
        for prod in sample_products:
            cursor.execute("""
                INSERT INTO products (title, description, price, image_url, category, author)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, prod)
    
    # اضافه کردن مقالات نمونه
    cursor.execute("SELECT COUNT(*) FROM articles")
    if cursor.fetchone()[0] == 0:
        sample_articles = [
            ('۱۰ نکته طلایی برای سلامت قلب', 'در این مقاله با راهکارهای حفظ سلامت قلب آشنا می‌شوید...', 
             'قلب یکی از مهم‌ترین اندام‌های بدن است...', 'دکتر محمدی', '/static/images/article1.jpg', 'سلامت قلب'),
            ('اصول کمک‌های اولیه در حوادث', 'یاد بگیرید چگونه در مواقع اضطراری جان افراد را نجات دهید...',
             'کمک‌های اولیه مهارتی حیاتی است که هر فردی باید بداند...', 'سازمان هلال احمر', '/static/images/article2.jpg', 'امداد'),
            ('تغذیه سالم در دوران کرونا', 'رژیم غذایی مناسب برای تقویت سیستم ایمنی...',
             'تغذیه نقش مهمی در تقویت سیستم ایمنی بدن دارد...', 'دکتر کریمی', '/static/images/article3.jpg', 'تغذیه'),
            ('ورزش‌های کششی برای کارمندان', 'حرکات ساده‌ای که در پشت میز کار انجام دهید...',
             'نشستن طولانی مدت باعث مشکلات اسکلتی عضلانی می‌شود...', 'مربی ورزشی', '/static/images/article4.jpg', 'ورزش'),
            ('خواب سالم و تاثیر آن بر سلامت', 'چگونه خواب بهتری داشته باشیم؟...',
             'خواب کافی و باکیفیت برای سلامت جسم و روان ضروری است...', 'متخصص خواب', '/static/images/article5.jpg', 'سلامت عمومی'),
        ]
        for art in sample_articles:
            cursor.execute("""
                INSERT INTO articles (title, content, excerpt, author, image_url, category)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, art)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database tables created successfully!")

# هندلر درخواست‌های HTTP
class NursimedHandler(http.server.SimpleHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='/workspace/nursimed_v2', **kwargs)
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # روت‌های مختلف
        if path == '/' or path == '/index.html':
            self.serve_home()
        elif path == '/articles':
            self.serve_articles()
        elif path.startswith('/article/'):
            article_id = path.split('/')[-1]
            self.serve_single_article(article_id)
        elif path == '/shop':
            self.serve_shop()
        elif path.startswith('/product/'):
            product_id = path.split('/')[-1]
            self.serve_single_product(product_id)
        elif path == '/about':
            self.serve_about()
        elif path == '/contact':
            self.serve_contact()
        elif path == '/team':
            self.serve_team()
        elif path == '/login':
            self.serve_login()
        elif path == '/register':
            self.serve_register()
        elif path == '/cart':
            self.serve_cart()
        elif path == '/podcasts':
            self.serve_podcasts()
        elif path == '/courses':
            self.serve_courses()
        elif path == '/api/products':
            self.get_products_api()
        elif path == '/api/articles':
            self.get_articles_api()
        elif path.startswith('/api/product/'):
            product_id = path.split('/')[-1]
            self.get_single_product_api(product_id)
        elif path.startswith('/api/article/'):
            article_id = path.split('/')[-1]
            self.get_single_article_api(article_id)
        elif path.startswith('/api/cart/'):
            session_id = path.split('/')[-1]
            self.get_cart_api(session_id)
        elif path == '/error400':
            self.send_error_page(400, "Bad Request")
        elif path == '/error500':
            self.send_error_page(500, "Internal Server Error")
        else:
            # فایل‌های استاتیک
            if path.endswith('.css') or path.endswith('.js') or path.endswith('.jpg') or path.endswith('.png'):
                super().do_GET()
            else:
                self.send_error_page(404, "Page Not Found")
    
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data) if post_data else {}
        
        if path == '/api/register':
            self.handle_register(data)
        elif path == '/api/login':
            self.handle_login(data)
        elif path == '/api/cart/add':
            self.handle_add_to_cart(data)
        elif path == '/api/cart/remove':
            self.handle_remove_from_cart(data)
        elif path == '/api/cart/update':
            self.handle_update_cart(data)
        elif path == '/api/contact':
            self.handle_contact(data)
        elif path == '/api/checkout':
            self.handle_checkout(data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def serve_home(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نرسیمد | پلتفرم آموزشی پزشکی</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/articles">مقالات</a>
                    <a href="/shop">فروشگاه</a>
                    <a href="/podcasts">پادکست‌ها</a>
                    <a href="/courses">دوره‌ها</a>
                    <a href="/about">درباره ما</a>
                    <a href="/contact">تماس با ما</a>
                </nav>
                <div class="header-actions">
                    <a href="/cart" class="cart-icon">
                        <i class="fas fa-shopping-cart"></i>
                        <span class="cart-count" id="cartCount">0</span>
                    </a>
                    <a href="/login" class="btn btn-outline">ورود</a>
                    <a href="/register" class="btn btn-primary">ثبت نام</a>
                </div>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <h1>به نرسیمد خوش آمدید</h1>
                <p>مرجع تخصصی آموزش‌های پزشکی، کتاب‌ها و پادکست‌های سلامت</p>
                <div class="hero-buttons">
                    <a href="/shop" class="btn btn-primary btn-lg">مشاهده فروشگاه</a>
                    <a href="/articles" class="btn btn-outline btn-lg">مطالعه مقالات</a>
                </div>
            </div>
        </div>
    </section>

    <section class="features">
        <div class="container">
            <h2 class="section-title">ویژگی‌های نرسیمد</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <i class="fas fa-book-medical"></i>
                    <h3>کتاب‌های پزشکی</h3>
                    <p>دسترسی به بهترین منابع و کتاب‌های تخصصی پزشکی</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-podcast"></i>
                    <h3>پادکست‌های سلامت</h3>
                    <p>آموزش‌های صوتی در زمینه‌های مختلف پزشکی</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-chalkboard-teacher"></i>
                    <h3>دوره‌های آموزشی</h3>
                    <p>دوره‌های تخصصی با پشتیبانی هوشمند</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-first-aid"></i>
                    <h3>آموزش امداد</h3>
                    <p>یادگیری کمک‌های اولیه و اقدامات اضطراری</p>
                </div>
            </div>
        </div>
    </section>

    <section class="latest-products">
        <div class="container">
            <h2 class="section-title">جدیدترین محصولات</h2>
            <div class="products-grid" id="homeProducts">
                <!-- محصولات از دیتابیس بارگذاری می‌شوند -->
            </div>
            <div class="text-center">
                <a href="/shop" class="btn btn-primary">مشاهده همه محصولات</a>
            </div>
        </div>
    </section>

    <section class="latest-articles">
        <div class="container">
            <h2 class="section-title">آخرین مقالات</h2>
            <div class="articles-grid" id="homeArticles">
                <!-- مقالات از دیتابیس بارگذاری می‌شوند -->
            </div>
            <div class="text-center">
                <a href="/articles" class="btn btn-primary">مشاهده همه مقالات</a>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>نرسیمد</h3>
                    <p>پلتفرم جامع آموزش پزشکی برای دانشجویان، متخصصان و علاقه‌مندان به سلامت</p>
                </div>
                <div class="footer-section">
                    <h4>دسترسی سریع</h4>
                    <ul>
                        <li><a href="/about">درباره ما</a></li>
                        <li><a href="/contact">تماس با ما</a></li>
                        <li><a href="/team">اعضای تیم</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>محصولات</h4>
                    <ul>
                        <li><a href="/shop">کتاب‌ها</a></li>
                        <li><a href="/podcasts">پادکست‌ها</a></li>
                        <li><a href="/courses">دوره‌ها</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>ارتباط با ما</h4>
                    <p><i class="fas fa-envelope"></i> info@nursimed.ir</p>
                    <p><i class="fas fa-phone"></i> ۰۲۱-۱۲۳۴۵۶۷۸</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© ۱۴۰۳ نرسیمد - تمامی حقوق محفوظ است.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_articles(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مقالات | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/articles">مقالات</a>
                    <a href="/shop">فروشگاه</a>
                    <a href="/podcasts">پادکست‌ها</a>
                    <a href="/courses">دوره‌ها</a>
                    <a href="/about">درباره ما</a>
                    <a href="/contact">تماس با ما</a>
                </nav>
                <div class="header-actions">
                    <a href="/cart" class="cart-icon">
                        <i class="fas fa-shopping-cart"></i>
                        <span class="cart-count" id="cartCount">0</span>
                    </a>
                    <a href="/login" class="btn btn-outline">ورود</a>
                    <a href="/register" class="btn btn-primary">ثبت نام</a>
                </div>
            </div>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1>مقالات پزشکی</h1>
            <p>مطالب آموزشی و تخصصی در زمینه‌های مختلف پزشکی</p>
        </div>
    </section>

    <section class="articles-page">
        <div class="container">
            <div class="articles-grid" id="articlesList">
                <!-- مقالات از دیتابیس بارگذاری می‌شوند -->
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>© ۱۴۰۳ نرسیمد - تمامی حقوق محفوظ است.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_single_article(self, article_id):
        template = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مقاله | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/articles">مقالات</a>
                    <a href="/shop">فروشگاه</a>
                </nav>
                <div class="header-actions">
                    <a href="/cart" class="cart-icon">
                        <i class="fas fa-shopping-cart"></i>
                        <span class="cart-count" id="cartCount">0</span>
                    </a>
                </div>
            </div>
        </div>
    </header>

    <section class="article-detail" data-article-id="{article_id}">
        <div class="container">
            <div class="article-content" id="articleContent">
                <!-- محتوا از دیتابیس بارگذاری می‌شود -->
            </div>
        </div>
    </section>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_shop(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>فروشگاه | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/articles">مقالات</a>
                    <a href="/shop">فروشگاه</a>
                    <a href="/podcasts">پادکست‌ها</a>
                    <a href="/courses">دوره‌ها</a>
                </nav>
                <div class="header-actions">
                    <a href="/cart" class="cart-icon">
                        <i class="fas fa-shopping-cart"></i>
                        <span class="cart-count" id="cartCount">0</span>
                    </a>
                    <a href="/login" class="btn btn-outline">ورود</a>
                </div>
            </div>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1>فروشگاه کتاب‌های پزشکی</h1>
            <p>بهترین منابع و کتاب‌های تخصصی پزشکی</p>
        </div>
    </section>

    <section class="shop-page">
        <div class="container">
            <div class="filters">
                <button class="filter-btn active" data-category="all">همه</button>
                <button class="filter-btn" data-category="کتاب تخصصی">تخصصی</button>
                <button class="filter-btn" data-category="کتاب عمومی">عمومی</button>
            </div>
            <div class="products-grid" id="productsList">
                <!-- محصولات از دیتابیس بارگذاری می‌شوند -->
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>© ۱۴۰۳ نرسیمد - تمامی حقوق محفوظ است.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_single_product(self, product_id):
        template = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>محصول | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/shop">فروشگاه</a>
                </nav>
                <div class="header-actions">
                    <a href="/cart" class="cart-icon">
                        <i class="fas fa-shopping-cart"></i>
                        <span class="cart-count" id="cartCount">0</span>
                    </a>
                </div>
            </div>
        </div>
    </header>

    <section class="product-detail" data-product-id="{product_id}">
        <div class="container">
            <div class="product-detail-content" id="productContent">
                <!-- محتوا از دیتابیس بارگذاری می‌شود -->
            </div>
        </div>
    </section>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_about(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درباره ما | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/about">درباره ما</a>
                    <a href="/contact">تماس با ما</a>
                </nav>
            </div>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1>درباره نرسیمد</h1>
        </div>
    </section>

    <section class="about-page">
        <div class="container">
            <div class="about-content">
                <h2>داستان ما</h2>
                <p>نرسیمد یک پلتفرم آموزشی جامع در حوزه پزشکی است که با هدف ارائه دسترسی آسان به آموزش‌های تخصصی پزشکی برای دانشجویان، متخصصان و عموم مردم علاقه‌مند به سلامت ایجاد شده است.</p>
                
                <h2>ماموریت ما</h2>
                <p>ما معتقدیم که دانش پزشکی باید در دسترس همه باشد. بنابراین تلاش می‌کنیم با ارائه محتوای باکیفیت شامل کتاب‌ها، پادکست‌ها، دوره‌های آموزشی و مقالات تخصصی، به ارتقای سطح دانش پزشکی جامعه کمک کنیم.</p>
                
                <h2>ویژگی‌های منحصر به فرد</h2>
                <ul>
                    <li>دسترسی دائم به دوره‌های آموزشی</li>
                    <li>پشتیبانی هوشمند از یادگیرندگان</li>
                    <li>محتوای تولید شده توسط متخصصان</li>
                    <li>آموزش‌های امداد از راه دور</li>
                    <li>فروشگاه جامع کتاب‌های پزشکی</li>
                </ul>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>© ۱۴۰۳ نرسیمد - تمامی حقوق محفوظ است.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_contact(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تماس با ما | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/contact">تماس با ما</a>
                </nav>
            </div>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1>تماس با ما</h1>
            <p>سوالات و پیشنهادات خود را با ما در میان بگذارید</p>
        </div>
    </section>

    <section class="contact-page">
        <div class="container">
            <div class="contact-form-wrapper">
                <form id="contactForm" class="contact-form">
                    <div class="form-group">
                        <label>نام و نام خانوادگی</label>
                        <input type="text" name="name" required>
                    </div>
                    <div class="form-group">
                        <label>ایمیل</label>
                        <input type="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label>پیام شما</label>
                        <textarea name="message" rows="5" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">ارسال پیام</button>
                </form>
                <div class="contact-info">
                    <h3>اطلاعات تماس</h3>
                    <p><i class="fas fa-envelope"></i> info@nursimed.ir</p>
                    <p><i class="fas fa-phone"></i> ۰۲۱-۱۲۳۴۵۶۷۸</p>
                    <p><i class="fas fa-map-marker-alt"></i> تهران، ایران</p>
                </div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>© ۱۴۰۳ نرسیمد - تمامی حقوق محفوظ است.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_team(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اعضای تیم | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/team">اعضای تیم</a>
                </nav>
            </div>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1>اعضای تیم نرسیمد</h1>
            <p>با تیم متخصص ما آشنا شوید</p>
        </div>
    </section>

    <section class="team-page">
        <div class="container">
            <div class="team-grid">
                <div class="team-member">
                    <div class="member-avatar">
                        <i class="fas fa-user-md"></i>
                    </div>
                    <h3>دکتر محمدی</h3>
                    <p>متخصص داخلی و مدیر علمی</p>
                </div>
                <div class="team-member">
                    <div class="member-avatar">
                        <i class="fas fa-user-graduate"></i>
                    </div>
                    <h3>دکتر احمدی</h3>
                    <p>متخصص تغذیه</p>
                </div>
                <div class="team-member">
                    <div class="member-avatar">
                        <i class="fas fa-user-nurse"></i>
                    </div>
                    <h3>مریم کریمی</h3>
                    <p>پرستار ارشد و مدرس امداد</p>
                </div>
                <div class="team-member">
                    <div class="member-avatar">
                        <i class="fas fa-laptop-code"></i>
                    </div>
                    <h3>علی رضایی</h3>
                    <p>توسعه‌دهنده وب</p>
                </div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>© ۱۴۰۳ نرسیمد - تمامی حقوق محفوظ است.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_login(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="auth-page">
        <div class="auth-container">
            <div class="auth-box">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <h2>ورود به حساب کاربری</h2>
                <form id="loginForm" class="auth-form">
                    <div class="form-group">
                        <label>ایمیل یا نام کاربری</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>رمز عبور</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">ورود</button>
                </form>
                <p class="auth-footer">حساب کاربری ندارید؟ <a href="/register">ثبت نام کنید</a></p>
            </div>
        </div>
    </div>
    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_register(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ثبت نام | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="auth-page">
        <div class="auth-container">
            <div class="auth-box">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <h2>ثبت نام در نرسیمد</h2>
                <form id="registerForm" class="auth-form">
                    <div class="form-group">
                        <label>نام کاربری</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>ایمیل</label>
                        <input type="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label>رمز عبور</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">ثبت نام</button>
                </form>
                <p class="auth-footer">قبلاً ثبت نام کرده‌اید؟ <a href="/login">وارد شوید</a></p>
            </div>
        </div>
    </div>
    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_cart(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سبد خرید | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/shop">فروشگاه</a>
                </nav>
            </div>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1>سبد خرید شما</h1>
        </div>
    </section>

    <section class="cart-page">
        <div class="container">
            <div id="cartContent">
                <!-- محتوای سبد خرید اینجا بارگذاری می‌شود -->
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>© ۱۴۰۳ نرسیمد - تمامی حقوق محفوظ است.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_podcasts(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پادکست‌ها | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/podcasts">پادکست‌ها</a>
                </nav>
            </div>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1>پادکست‌های پزشکی</h1>
            <p>آموزش‌های صوتی در زمینه‌های مختلف سلامت</p>
        </div>
    </section>

    <section class="podcasts-page">
        <div class="container">
            <p style="text-align: center; padding: 50px;">به زودی...</p>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>© ۱۴۰۳ نرسیمد - تمامی حقوق محفوظ است.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def serve_courses(self):
        template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دوره‌ها | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-heartbeat"></i>
                    <span>نرسیمد</span>
                </div>
                <nav class="nav">
                    <a href="/">خانه</a>
                    <a href="/courses">دوره‌ها</a>
                </nav>
            </div>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1>دوره‌های آموزشی پزشکی</h1>
            <p>دوره‌های تخصصی با پشتیبانی هوشمند</p>
        </div>
    </section>

    <section class="courses-page">
        <div class="container">
            <p style="text-align: center; padding: 50px;">به زودی...</p>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>© ۱۴۰۳ نرسیمد - تمامی حقوق محفوظ است.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    def send_error_page(self, code, message):
        template = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خطای {code} | نرسیمد</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
</head>
<body>
    <div class="error-page">
        <div class="error-content">
            <h1>{code}</h1>
            <p>{message}</p>
            <a href="/" class="btn btn-primary">بازگشت به صفحه اصلی</a>
        </div>
    </div>
</body>
</html>"""
        
        self.send_response(code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(template.encode('utf-8'))
    
    # API Methods
    def get_products_api(self):
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, price, image_url, category, author FROM products ORDER BY created_at DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        products = []
        for row in rows:
            products.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'price': float(row[3]),
                'image_url': row[4],
                'category': row[5],
                'author': row[6]
            })
        
        self.send_json({'products': products})
    
    def get_articles_api(self):
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, excerpt, author, image_url, category, created_at FROM articles ORDER BY created_at DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        articles = []
        for row in rows:
            articles.append({
                'id': row[0],
                'title': row[1],
                'excerpt': row[2],
                'author': row[3],
                'image_url': row[4],
                'category': row[5],
                'created_at': str(row[6]) if row[6] else ''
            })
        
        self.send_json({'articles': articles})
    
    def get_single_product_api(self, product_id):
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, price, image_url, category, author FROM products WHERE id = %s", (product_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            product = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'price': float(row[3]),
                'image_url': row[4],
                'category': row[5],
                'author': row[6]
            }
            self.send_json({'product': product})
        else:
            self.send_json({'error': 'Product not found'}, 404)
    
    def get_single_article_api(self, article_id):
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content, excerpt, author, image_url, category, created_at FROM articles WHERE id = %s", (article_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            article = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'excerpt': row[3],
                'author': row[4],
                'image_url': row[5],
                'category': row[6],
                'created_at': str(row[7]) if row[7] else ''
            }
            self.send_json({'article': article})
        else:
            self.send_json({'error': 'Article not found'}, 404)
    
    def handle_register(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            self.send_json({'error': 'تمامی فیلدها الزامی هستند'}, 400)
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s)
            """, (username, email, password))
            conn.commit()
            self.send_json({'success': True, 'message': 'ثبت نام با موفقیت انجام شد'})
        except Exception as e:
            conn.rollback()
            self.send_json({'error': 'نام کاربری یا ایمیل تکراری است'}, 400)
        finally:
            cursor.close()
            conn.close()
    
    def handle_login(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            self.send_json({'error': 'نام کاربری و رمز عبور الزامی هستند'}, 400)
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email FROM users
            WHERE (username = %s OR email = %s) AND password = %s
        """, (username, username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            self.send_json({
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2]
                }
            })
        else:
            self.send_json({'error': 'نام کاربری یا رمز عبور اشتباه است'}, 401)
    
    def handle_add_to_cart(self, data):
        session_id = data.get('session_id', 'default')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            self.send_json({'error': 'محصول مشخص نشده است'}, 400)
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        try:
            # بررسی وجود آیتم در سبد
            cursor.execute("""
                SELECT id, quantity FROM cart_items
                WHERE session_id = %s AND product_id = %s
            """, (session_id, product_id))
            existing = cursor.fetchone()
            
            if existing:
                # افزایش تعداد
                new_quantity = existing[1] + quantity
                cursor.execute("""
                    UPDATE cart_items SET quantity = %s WHERE id = %s
                """, (new_quantity, existing[0]))
            else:
                # افزودن آیتم جدید
                cursor.execute("""
                    INSERT INTO cart_items (session_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """, (session_id, product_id, quantity))
            
            conn.commit()
            self.send_json({'success': True, 'message': 'به سبد خرید اضافه شد'})
        except Exception as e:
            conn.rollback()
            self.send_json({'error': str(e)}, 500)
        finally:
            cursor.close()
            conn.close()
    
    def handle_remove_from_cart(self, data):
        session_id = data.get('session_id', 'default')
        item_id = data.get('item_id')
        
        if not item_id:
            self.send_json({'error': 'آیتم مشخص نشده است'}, 400)
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart_items WHERE id = %s AND session_id = %s", (item_id, session_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        self.send_json({'success': True})
    
    def handle_update_cart(self, data):
        session_id = data.get('session_id', 'default')
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        
        if not all([item_id, quantity]):
            self.send_json({'error': 'اطلاعات ناقص است'}, 400)
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cart_items SET quantity = %s WHERE id = %s AND session_id = %s
        """, (quantity, item_id, session_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        self.send_json({'success': True})
    
    def get_cart_api(self, session_id):
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci.id, ci.quantity, p.id, p.title, p.price, p.image_url
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.session_id = %s
        """, (session_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        items = []
        total = 0
        for row in rows:
            item_total = float(row[4]) * row[1]
            total += item_total
            items.append({
                'id': row[0],
                'quantity': row[1],
                'product': {
                    'id': row[2],
                    'title': row[3],
                    'price': float(row[4]),
                    'image_url': row[5]
                },
                'item_total': item_total
            })
        
        self.send_json({'items': items, 'total': total})
    
    def handle_contact(self, data):
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        
        if not all([name, email, message]):
            self.send_json({'error': 'تمامی فیلدها الزامی هستند'}, 400)
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json({'error': 'Database connection failed'}, 500)
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contacts (name, email, message)
            VALUES (%s, %s, %s)
        """, (name, email, message))
        conn.commit()
        cursor.close()
        conn.close()
        
        self.send_json({'success': True, 'message': 'پیام شما با موفقیت ارسال شد'})
    
    def handle_checkout(self, data):
        session_id = data.get('session_id', 'default')
        # اینجا می‌توانید منطق پرداخت را اضافه کنید
        self.send_json({'success': True, 'message': 'سفارش شما با موفقیت ثبت شد'})
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

# اجرای سرور
if __name__ == '__main__':
    PORT = 8000
    
    print("Creating database tables...")
    create_tables()
    
    print(f"Starting Nursimed server on port {PORT}...")
    with socketserver.TCPServer(("", PORT), NursimedHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()
