import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DB_CONFIG, ADMIN_EMAIL, ADMIN_PASS
import hashlib
import os

def get_db_connection():
    """اتصال به دیتابیس"""
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
        print(f"خطا در اتصال به دیتابیس: {e}")
        return None

def init_db():
    """ایجاد جداول و داده‌های اولیه"""
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    try:
        # جدول کاربران
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول محصولات (کتاب‌ها)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                image_url VARCHAR(500),
                category VARCHAR(100),
                stock INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول مقالات
        cur.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                excerpt VARCHAR(500),
                image_url VARCHAR(500),
                author VARCHAR(100),
                category VARCHAR(100),
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول دوره‌ها
        cur.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                image_url VARCHAR(500),
                instructor VARCHAR(100),
                duration VARCHAR(50),
                level VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول پادکست‌ها
        cur.execute("""
            CREATE TABLE IF NOT EXISTS podcasts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                audio_url VARCHAR(500),
                duration VARCHAR(50),
                host VARCHAR(100),
                episode_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول سبد خرید
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                quantity INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, product_id)
            )
        """)
        
        # جدول سفارشات
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                total_amount DECIMAL(10, 2),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول پیام‌های تماس با ما
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(255),
                subject VARCHAR(255),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ایجاد اکانت ادمین
        admin_hash = hashlib.sha256(ADMIN_PASS.encode()).hexdigest()
        cur.execute("""
            INSERT INTO users (username, email, password, is_admin)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, ('admin', ADMIN_EMAIL, admin_hash, True))
        
        # اضافه کردن داده‌های نمونه محصولات
        sample_products = [
            ('کتاب آناتومی گری', 'مرجع کامل آناتومی بدن انسان برای دانشجویان پزشکی', 450000, 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400', 'کتاب', 50),
            ('کتاب فیزیولوژی گایتون', 'کتاب مرجع فیزیولوژی پزشکی', 380000, 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400', 'کتاب', 30),
            ('کتاب پاتولوژی Robbins', 'مرجع بیماری‌شناسی عمومی و تخصصی', 520000, 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400', 'کتاب', 25),
            ('کتاب فارماکولوژی کاتزونگ', 'داروشناسی بالینی برای پزشکان', 410000, 'https://images.unsplash.com/photo-1555680202-c84f975971d2?w=400', 'کتاب', 40),
            ('کتاب معاینه فیزیکی', 'راهنمای کامل معاینه بیمار', 290000, 'https://images.unsplash.com/photo-1516549655169-df83a0921410?w=400', 'کتاب', 35),
            ('کتاب ایمونولوژی جانز', 'مبانی ایمنی‌شناسی پزشکی', 360000, 'https://images.unsplash.com/photo-1576091160550-217358c7e618?w=400', 'کتاب', 20),
        ]
        
        for product in sample_products:
            cur.execute("""
                INSERT INTO products (title, description, price, image_url, category, stock)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, product)
        
        # اضافه کردن داده‌های نمونه مقالات
        sample_articles = [
            ('۱۰ علامت هشداردهنده سکته قلبی', 'شناخت علائم اولیه سکته قلبی می‌تواند جان شما را نجات دهد. در این مقاله به بررسی مهم‌ترین نشانه‌ها می‌پردازیم...', 
             'سکته قلبی یکی از علل اصلی مرگ و میر در جهان است. شناخت علائم آن بسیار حیاتی است.', 
             'https://images.unsplash.com/photo-1576091160550-217358c7e618?w=600', 'دکتر محمدی', 'قلب', 0),
            ('اصول اولیه کمک‌های اولیه', 'یادگیری کمک‌های اولیه مهارتی است که هر فردی باید بداند. در این مقاله اصول پایه را آموزش می‌دهیم...',
             'کمک‌های اولیه اقداماتی است که قبل از رسیدن نیروهای امدادی انجام می‌شود.',
             'https://images.unsplash.com/photo-1516549655169-df83a0921410?w=600', 'دکتر احمدی', 'امداد', 0),
            ('تغذیه سالم برای پزشکان', 'پزشکان به دلیل شیفت‌های کاری طولانی نیاز به تغذیه خاصی دارند...',
             'برنامه غذایی مناسب می‌تواند عملکرد پزشکان را بهبود بخشد.',
             'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=600', 'دکتر کریمی', 'تغذیه', 0),
            ('روش‌های جدید درمان دیابت', 'تحقیقات اخیر روش‌های نوینی را برای کنترل دیابت معرفی کرده‌اند...',
             'دیابت نوع ۲ یکی از شایع‌ترین بیماری‌های مزمن است.',
             'https://images.unsplash.com/photo-1579684385180-1ea98f792a57?w=600', 'دکتر رضایی', 'غدد', 0),
            ('اهمیت خواب در سلامت روان', 'خواب کافی تأثیر مستقیمی بر سلامت روان و عملکرد مغز دارد...',
             'کمبود خواب می‌تواند منجر به مشکلات جدی سلامتی شود.',
             'https://images.unsplash.com/photo-1541781777631-fa9531908442?w=600', 'دکتر حسینی', 'روان', 0),
        ]
        
        for article in sample_articles:
            cur.execute("""
                INSERT INTO articles (title, content, excerpt, image_url, author, category, views)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, article)
        
        # اضافه کردن دوره‌های نمونه
        sample_courses = [
            ('دوره ACLS پیشرفته', 'دوره احیای قلبی عروقی پیشرفته برای پزشکان و پرستاران', 1500000, 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400', 'دکتر محمدی', '۱۶ ساعت', 'پیشرفته'),
            ('دوره تفسیر نوار قلب', 'آموزش کامل خواندن و تفسیر ECG', 850000, 'https://images.unsplash.com/photo-1576091160550-217358c7e618?w=400', 'دکتر احمدی', '۸ ساعت', 'متوسط'),
            ('دوره کمک‌های اولیه', 'آموزش اصول اولیه امداد و نجات', 450000, 'https://images.unsplash.com/photo-1516549655169-df83a0921410?w=400', 'دکتر کریمی', '۴ ساعت', 'مقدماتی'),
        ]
        
        for course in sample_courses:
            cur.execute("""
                INSERT INTO courses (title, description, price, image_url, instructor, duration, level)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, course)
        
        # اضافه کردن پادکست‌های نمونه
        sample_podcasts = [
            ('پادکست سلامت قلب', 'بحث درباره آخرین یافته‌های بیماری‌های قلبی', 'https://example.com/podcast1.mp3', '۴۵ دقیقه', 'دکتر محمدی', 1),
            ('پادکست روانشناسی پزشکی', 'بررسی جنبه‌های روانی مراقبت از بیماران', 'https://example.com/podcast2.mp3', '۳۰ دقیقه', 'دکتر حسینی', 2),
            ('پادکست تغذیه بالینی', 'نکات تغذیه‌ای برای بیماران خاص', 'https://example.com/podcast3.mp3', '۳۵ دقیقه', 'دکتر رضایی', 3),
        ]
        
        for podcast in sample_podcasts:
            cur.execute("""
                INSERT INTO podcasts (title, description, audio_url, duration, host, episode_number)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, podcast)
        
        conn.commit()
        print("✅ دیتابیس با موفقیت ایجاد شد و داده‌های نمونه اضافه شدند!")
        print(f"📧 اکانت ادمین: {ADMIN_EMAIL}")
        print(f"🔑 رمز عبور: {ADMIN_PASS}")
        
    except Exception as e:
        print(f"❌ خطا در ایجاد دیتابیس: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_db()
