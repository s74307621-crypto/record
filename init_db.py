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
        # جدول کاربران با فیلدهای کامل
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                phone VARCHAR(20),
                address TEXT,
                birth_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول محصولات
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                image_url VARCHAR(500),
                category VARCHAR(100),
                stock INTEGER DEFAULT 0,
                average_rating DECIMAL(3,2) DEFAULT 0,
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
                average_rating DECIMAL(3,2) DEFAULT 0,
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
        
        # جدول آیتم‌های سفارش
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(id),
                course_id INTEGER REFERENCES courses(id),
                quantity INTEGER DEFAULT 1,
                price DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول پیام‌های تماس
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
        
        # جدول امتیازات محصولات
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_ratings (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(product_id, user_id)
            )
        """)
        
        # جدول علاقه‌مندی‌ها
        cur.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, product_id)
            )
        """)
        
        # ایجاد اکانت ادمین
        admin_hash = hashlib.sha256(ADMIN_PASS.encode()).hexdigest()
        cur.execute("""
            INSERT INTO users (username, email, password, is_admin)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, ('admin', ADMIN_EMAIL, admin_hash, True))
        
        # داده‌های نمونه محصولات
        sample_products = [
            ('کتاب آناتومی گری', 'مرجع کامل آناتومی بدن انسان برای دانشجویان پزشکی. این کتاب شامل تصاویر دقیق و توضیحات کامل از تمام سیستم‌های بدن انسان است.', 450000, 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400', 'کتاب', 50),
            ('کتاب فیزیولوژی گایتون', 'کتاب مرجع فیزیولوژی پزشکی. بهترین منبع برای یادگیری فیزیولوژی بدن انسان با توضیحات روشن و کاربردی.', 380000, 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400', 'کتاب', 30),
            ('کتاب پاتولوژی Robbins', 'مرجع بیماری‌شناسی عمومی و تخصصی. جامع‌ترین کتاب پاتولوژی برای دانشجویان پزشکی و متخصصین.', 520000, 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400', 'کتاب', 25),
            ('کتاب فارماکولوژی کاتزونگ', 'داروشناسی بالینی برای پزشکان. راهنمای کامل داروها، عوارض و تداخلات دارویی.', 410000, 'https://images.unsplash.com/photo-1555680202-c84f975971d2?w=400', 'کتاب', 40),
            ('کتاب معاینه فیزیکی', 'راهنمای کامل معاینه بیمار. آموزش گام به گام معاینه سیستم‌های مختلف بدن.', 290000, 'https://images.unsplash.com/photo-1516549655169-df83a0921410?w=400', 'کتاب', 35),
            ('کتاب ایمونولوژی جانز', 'مبانی ایمنی‌شناسی پزشکی. درک عمیق از سیستم ایمنی بدن و بیماری‌های مرتبط.', 360000, 'https://images.unsplash.com/photo-1576091160550-217358c7e618?w=400', 'کتاب', 20),
        ]
        
        for product in sample_products:
            cur.execute("""
                INSERT INTO products (title, description, price, image_url, category, stock)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, product)
        
        # داده‌های نمونه مقالات
        sample_articles = [
            ('۱۰ علامت هشداردهنده سکته قلبی', 'شناخت علائم اولیه سکته قلبی می‌تواند جان شما را نجات دهد.\n\n## علائم هشداردهنده\n\n۱. درد قفسه سینه\n۲. تنگی نفس\n۳. تعریق سرد\n۴. حالت تهوع\n\n## چه باید کرد؟\n\nدر صورت مشاهده این علائم فوراً با اورژانس تماس بگیرید.', 
             'سکته قلبی یکی از علل اصلی مرگ و میر در جهان است.', 
             'https://images.unsplash.com/photo-1576091160550-217358c7e618?w=600', 'دکتر محمدی', 'قلب', 0),
            ('اصول اولیه کمک‌های اولیه', 'یادگیری کمک‌های اولیه مهارتی است که هر فردی باید بداند.\n\n## مراحل اولیه\n\n۱. ارزیابی صحنه\n۲. بررسی هوشیاری\n۳. تماس با اورژانس\n۴. شروع CPR',\n             'کمک‌های اولیه اقداماتی است که قبل از رسیدن نیروهای امدادی انجام می‌شود.',\n             'https://images.unsplash.com/photo-1516549655169-df83a0921410?w=600', 'دکتر احمدی', 'امداد', 0),
            ('تغذیه سالم برای پزشکان', 'پزشکان به دلیل شیفت‌های کاری طولانی نیاز به تغذیه خاصی دارند.\n\n## توصیه‌های غذایی\n\n- مصرف وعده‌های کوچک\n- استفاده از میان‌وعده‌های سالم',\n             'برنامه غذایی مناسب می‌تواند عملکرد پزشکان را بهبود بخشد.',\n             'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=600', 'دکتر کریمی', 'تغذیه', 0),
        ]
        
        for article in sample_articles:
            cur.execute("""
                INSERT INTO articles (title, content, excerpt, image_url, author, category, views)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, article)
        
        conn.commit()
        print("✅ دیتابیس با موفقیت ایجاد شد!")
        print(f"📧 اکانت ادمین: {ADMIN_EMAIL}")
        print(f"🔑 رمز عبور: {ADMIN_PASS}")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_db()
