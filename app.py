# فایل اصلی برنامه - سرور وب ساده با پایتون
# این فایل رو اجرا کنید تا سایت بالا بیاد

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import psycopg2
from db_config import DB_CONFIG

# اتصال به دیتابیس
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        return conn
    except Exception as e:
        print("خطا در اتصال به دیتابیس:", e)
        return None

# ایجاد جداول دیتابیس
def create_tables():
    conn = get_db_connection()
    if conn is None:
        print("نتوانست به دیتابیس وصل شود!")
        return
    
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول کتاب‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            author VARCHAR(100),
            price DECIMAL(10, 2),
            description TEXT,
            image_url VARCHAR(300),
            category VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول دوره‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            instructor VARCHAR(100),
            price DECIMAL(10, 2),
            description TEXT,
            image_url VARCHAR(300),
            duration VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول پادکست‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS podcasts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            host VARCHAR(100),
            audio_url VARCHAR(300),
            description TEXT,
            duration VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول مقالات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            author VARCHAR(100),
            content TEXT,
            summary VARCHAR(500),
            image_url VARCHAR(300),
            category VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول تماس با ما
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("جداول با موفقیت ساخته شدند!")

# هندلر درخواست‌ها
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # مسیرهای مختلف سایت
        if self.path == '/' or self.path == '/index.html':
            self.path = '/templates/index.html'
        elif self.path == '/articles.html':
            self.path = '/templates/articles.html'
        elif self.path.startswith('/article-'):
            self.path = '/templates/article_detail.html'
        elif self.path == '/store.html':
            self.path = '/templates/store.html'
        elif self.path.startswith('/product-'):
            self.path = '/templates/product_detail.html'
        elif self.path == '/about.html':
            self.path = '/templates/about.html'
        elif self.path == '/contact.html':
            self.path = '/templates/contact.html'
        elif self.path == '/team.html':
            self.path = '/templates/team.html'
        elif self.path == '/login.html':
            self.path = '/templates/login.html'
        elif self.path == '/register.html':
            self.path = '/templates/register.html'
        elif self.path == '/400.html':
            self.path = '/templates/400.html'
        elif self.path == '/500.html':
            self.path = '/templates/500.html'
        elif self.path.startswith('/static/'):
            pass  # فایل‌های استاتیک
        else:
            self.path = '/templates/404.html'
        
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        #处理 POST درخواست‌ها (مثل فرم تماس یا ثبت نام)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # اینجا می‌تونید داده‌ها رو پردازش کنید
        print("داده دریافت شد:", post_data)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        response = "<html><body><h1>دریافت شد!</h1></body></html>"
        self.wfile.write(response.encode('utf-8'))

if __name__ == '__main__':
    # اول جداول رو می‌سازه
    print("در حال ساخت جداول دیتابیس...")
    create_tables()
    
    # بعد سرور رو راه میندازه
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandler)
    print("سرور روی آدرس http://localhost:8000 اجرا شد")
    print("برای توقف سرور Ctrl+C بزنید")
    httpd.serve_forever()
