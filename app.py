from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import hashlib
import urllib.parse
from db_config import DB_CONFIG, ADMIN_EMAIL, ADMIN_PASS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# مسیر فایل‌های استاتیک و تمپلیت‌ها
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

print(BASE_DIR)
print(TEMPLATES_DIR)
print(os.path.exists(TEMPLATES_DIR))
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

def hash_password(password):
    """هش کردن رمز عبور"""
    return hashlib.sha256(password.encode()).hexdigest()

class NursimedHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # روت‌های مختلف
        if path == '/' or path == '/index.html':
            self.serve_page('home')
        elif path == '/shop':
            self.serve_page('shop')
        elif path.startswith('/product/'):
            product_id = path.split('/')[-1]
            self.serve_product_detail(product_id)
        elif path == '/articles':
            self.serve_page('articles')
        elif path.startswith('/article/'):
            article_id = path.split('/')[-1]
            self.serve_article_detail(article_id)
        elif path == '/about':
            self.serve_page('about')
        elif path == '/contact':
            self.serve_page('contact')
        elif path == '/team':
            self.serve_page('team')
        elif path == '/login':
            self.serve_page('login')
        elif path == '/register':
            self.serve_page('register')
        elif path == '/cart':
            self.serve_page('cart')
        elif path == '/admin':
            self.serve_page('admin')
        elif path == '/error400':
            self.serve_error(400)
        elif path == '/error500':
            self.serve_error(500)
        elif path.startswith('/static/'):
            self.serve_static(path)
        elif path.startswith('/api/'):
            self.handle_api(path)
        else:
            self.serve_error(404)
    
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data) if post_data else {}
        except:
            data = {}
        
        if path == '/api/login':
            self.handle_login(data)
        elif path == '/api/register':
            self.handle_register(data)
        elif path == '/api/cart/add':
            self.handle_add_to_cart(data)
        elif path == '/api/cart/get':
            self.handle_get_cart(data)
        elif path == '/api/cart/update':
            self.handle_update_cart(data)
        elif path == '/api/cart/remove':
            self.handle_remove_from_cart(data)
        elif path == '/api/contact':
            self.handle_contact(data)
        elif path == '/api/admin/products':
            self.handle_admin_products(data)
        elif path == '/api/admin/articles':
            self.handle_admin_articles(data)
        elif path == '/api/product/rate':
            self.handle_product_rate(data)
        elif path == '/api/product/favorite':
            self.handle_product_favorite(data)
        elif path == '/api/user/profile':
            self.handle_user_profile(data)
        elif path == '/api/user/orders':
            self.handle_user_orders(data)
        elif path == '/api/article/rate':
            self.handle_article_rate(data)
        else:
            self.send_json_response({'success': False, 'message': 'API not found'})
    
    def serve_page(self, page_name):
        """سرو کردن صفحات HTML"""
        template_path = os.path.join(TEMPLATES_DIR, f'{page_name}.html')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.serve_error(404)
    
    def serve_product_detail(self, product_id):
        """نمایش جزئیات محصول"""
        conn = get_db_connection()
        if not conn:
            self.serve_error(500)
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cur.fetchone()
        cur.close()
        conn.close()
        
        if product:
            template_path = os.path.join(TEMPLATES_DIR, 'product_detail.html')
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # جایگذاری داده‌های محصول در تمپلیت
                content = content.replace('{{PRODUCT_ID}}', str(product['id']))
                content = content.replace('{{TITLE}}', product['title'])
                content = content.replace('{{DESCRIPTION}}', product['description'] or '')
                content = content.replace('{{PRICE}}', f"{product['price']:,.0f}")
                content = content.replace('{{IMAGE_URL}}', product['image_url'] or 'https://via.placeholder.com/400x300?text=No+Image')
                content = content.replace('{{CATEGORY}}', product['category'] or '')
                content = content.replace('{{STOCK}}', str(product['stock'] or 0))
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
                return
        
        self.serve_error(404)
    
    def serve_article_detail(self, article_id):
        """نمایش جزئیات مقاله"""
        conn = get_db_connection()
        if not conn:
            self.serve_error(500)
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # افزایش بازدید
        cur.execute("UPDATE articles SET views = views + 1 WHERE id = %s", (article_id,))
        conn.commit()
        
        cur.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
        article = cur.fetchone()
        cur.close()
        conn.close()
        
        if article:
            template_path = os.path.join(TEMPLATES_DIR, 'article_detail.html')
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # جایگذاری داده‌های مقاله در تمپلیت
                content = content.replace('{{ARTICLE_ID}}', str(article['id']))
                content = content.replace('{{TITLE}}', article['title'])
                content = content.replace('{{CONTENT}}', article['content'])
                content = content.replace('{{EXCERPT}}', article['excerpt'] or '')
                content = content.replace('{{IMAGE_URL}}', article['image_url'] or 'https://via.placeholder.com/600x400?text=No+Image')
                content = content.replace('{{AUTHOR}}', article['author'] or 'ناشناس')
                content = content.replace('{{CATEGORY}}', article['category'] or '')
                content = content.replace('{{VIEWS}}', str(article['views'] or 0))
                content = content.replace('{{CREATED_AT}}', str(article['created_at'])[:10] if article['created_at'] else '')
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
                return
        
        self.serve_error(404)
    
    def serve_static(self, path):
        """سرو کردن فایل‌های استاتیک"""
        file_path = os.path.join(BASE_DIR, path[1:])  # حذف اسلش اول
        
        if os.path.exists(file_path):
            _, ext = os.path.splitext(file_path)
            content_types = {
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon'
            }
            
            content_type = content_types.get(ext, 'application/octet-stream')
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        else:
            self.serve_error(404)
    
    def handle_api(self, path):
        """هندل کردن درخواست‌های API"""
        if path == '/api/products':
            self.get_products()
        elif path == '/api/articles':
            self.get_articles()
        elif path == '/api/courses':
            self.get_courses()
        elif path == '/api/podcasts':
            self.get_podcasts()
        else:
            self.send_json_response({'success': False, 'message': 'API not found'})
    
    def get_products(self):
        """دریافت لیست محصولات"""
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'Database connection failed'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY created_at DESC")
        products = cur.fetchall()
        cur.close()
        conn.close()
        
        # تبدیل Decimal به float برای JSON
        for p in products:
            p['price'] = float(p['price'])

            if p.get('created_at'):
                 p['created_at'] = p['created_at'].isoformat()

            if p.get('updated_at'):
                p['updated_at'] = p['updated_at'].isoformat()
                # for p in products:
                #     p['price'] = float(p['price'])
        
        self.send_json_response({'success': True, 'data': products})
    
    def get_articles(self):
        """دریافت لیست مقالات"""
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'Database connection failed'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM articles ORDER BY created_at DESC")
        articles = cur.fetchall()
        cur.close()
        conn.close()
        for a in articles:
         if a.get('created_at'):
          a['created_at'] = a['created_at'].isoformat()

         if a.get('updated_at'):
            a['updated_at'] = a['updated_at'].isoformat()
        
        self.send_json_response({'success': True, 'data': articles})
    
    def get_courses(self):
        """دریافت لیست دوره‌ها"""
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'Database connection failed'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM courses ORDER BY created_at DESC")
        courses = cur.fetchall()
        cur.close()
        conn.close()
        
        for c in courses:
            c['price'] = float(c['price'])
        
        self.send_json_response({'success': True, 'data': courses})
    
    def get_podcasts(self):
        """دریافت لیست پادکست‌ها"""
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'Database connection failed'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM podcasts ORDER BY created_at DESC")
        podcasts = cur.fetchall()
        cur.close()
        conn.close()
        
        self.send_json_response({'success': True, 'data': podcasts})
    
    def handle_login(self, data):
        """پردازش ورود کاربر"""
        email = data.get('email', '')
        password = data.get('password', '')
        
        if not email or not password:
            self.send_json_response({'success': False, 'message': 'ایمیل و رمز عبور الزامی است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        password = hash_password(password)
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            self.send_json_response({
                'success': True, 
                'message': 'ورود موفقیت‌آمیز بود',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user['is_admin']
                }
            })
        else:
            self.send_json_response({'success': False, 'message': 'ایمیل یا رمز عبور اشتباه است'})
    
    def handle_register(self, data):
        """پردازش ثبت نام کاربر"""
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')
        
        if not username or not email or not password:
            self.send_json_response({'success': False, 'message': 'تمام فیلدها الزامی است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor()
        password = hash_password(password)
        
        try:
            cur.execute("""
                INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s)
            """, (username, email, password))
            conn.commit()
            self.send_json_response({'success': True, 'message': 'ثبت نام موفقیت‌آمیز بود'})
        except psycopg2.IntegrityError:
            self.send_json_response({'success': False, 'message': 'این ایمیل یا نام کاربری قبلاً استفاده شده است'})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()
    
    def handle_add_to_cart(self, data):
        """افزودن محصول به سبد خرید"""
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not user_id or not product_id:
            self.send_json_response({'success': False, 'message': 'اطلاعات ناقص است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor()
        
        try:
            # بررسی وجود محصول در سبد
            cur.execute("""
                SELECT id, quantity FROM cart_items 
                WHERE user_id = %s AND product_id = %s
            """, (user_id, product_id))
            
            existing = cur.fetchone()
            
            if existing:
                # افزایش تعداد
                new_qty = existing[1] + quantity
                cur.execute("""
                    UPDATE cart_items SET quantity = %s 
                    WHERE user_id = %s AND product_id = %s
                """, (new_qty, user_id, product_id))
            else:
                # افزودن جدید
                cur.execute("""
                    INSERT INTO cart_items (user_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """, (user_id, product_id, quantity))
            
            conn.commit()
            self.send_json_response({'success': True, 'message': 'محصول به سبد خرید اضافه شد'})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()
    
    def handle_get_cart(self, data):
        """دریافت سبد خرید کاربر"""
        user_id = data.get('user_id')
        
        if not user_id:
            self.send_json_response({'success': False, 'message': 'کاربر وارد نشده است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT ci.*, p.title, p.price, p.image_url 
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = %s
        """, (user_id,))
        
        items = cur.fetchall()
        cur.close()
        conn.close()
        
        total = sum(float(item['price']) * item['quantity'] for item in items)
        
        for item in items:
            item['price'] = float(item['price'])
        
        self.send_json_response({'success': True, 'data': items, 'total': total})
    
    def handle_update_cart(self, data):
        """به‌روزرسانی تعداد محصول در سبد"""
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not user_id or not product_id:
            self.send_json_response({'success': False, 'message': 'اطلاعات ناقص است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor()
        
        try:
            if quantity <= 0:
                cur.execute("""
                    DELETE FROM cart_items 
                    WHERE user_id = %s AND product_id = %s
                """, (user_id, product_id))
            else:
                cur.execute("""
                    UPDATE cart_items SET quantity = %s 
                    WHERE user_id = %s AND product_id = %s
                """, (quantity, user_id, product_id))
            
            conn.commit()
            self.send_json_response({'success': True, 'message': 'سبد خرید به‌روزرسانی شد'})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()
    
    def handle_remove_from_cart(self, data):
        """حذف محصول از سبد خرید"""
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        
        if not user_id or not product_id:
            self.send_json_response({'success': False, 'message': 'اطلاعات ناقص است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor()
        
        try:
            cur.execute("""
                DELETE FROM cart_items 
                WHERE user_id = %s AND product_id = %s
            """, (user_id, product_id))
            conn.commit()
            self.send_json_response({'success': True, 'message': 'محصول از سبد حذف شد'})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()
    
    def handle_contact(self, data):
        """پردازش فرم تماس با ما"""
        name = data.get('name', '')
        email = data.get('email', '')
        subject = data.get('subject', '')
        message = data.get('message', '')
        
        if not name or not email or not message:
            self.send_json_response({'success': False, 'message': 'نام، ایمیل و پیام الزامی است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO contact_messages (name, email, subject, message)
                VALUES (%s, %s, %s, %s)
            """, (name, email, subject, message))
            conn.commit()
            self.send_json_response({'success': True, 'message': 'پیام شما با موفقیت ارسال شد'})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()
    
    def handle_admin_products(self, data):
        """مدیریت محصولات توسط ادمین"""
        action = data.get('action')
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if action == 'get_all':
                cur.execute("SELECT * FROM products ORDER BY created_at DESC")
                products = cur.fetchall()
                for p in products:
                    p['price'] = float(p['price'])
                self.send_json_response({'success': True, 'data': products})
            
            elif action == 'add':
                cur.execute("""
                    INSERT INTO products (title, description, price, image_url, category, stock)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (data.get('title'), data.get('description'), data.get('price'), 
                      data.get('image_url'), data.get('category'), data.get('stock')))
                product = cur.fetchone()
                conn.commit()
                product['price'] = float(product['price'])
                self.send_json_response({'success': True, 'data': product})
            
            elif action == 'delete':
                cur.execute("DELETE FROM products WHERE id = %s", (data.get('id'),))
                conn.commit()
                self.send_json_response({'success': True, 'message': 'محصول حذف شد'})
        
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()
    
    def handle_admin_articles(self, data):
        """مدیریت مقالات توسط ادمین"""
        action = data.get('action')
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if action == 'get_all':
                cur.execute("SELECT * FROM articles ORDER BY created_at DESC")
                articles = cur.fetchall()
                self.send_json_response({'success': True, 'data': articles})
            
            elif action == 'add':
                cur.execute("""
                    INSERT INTO articles (title, content, excerpt, image_url, author, category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (data.get('title'), data.get('content'), data.get('excerpt'), 
                      data.get('image_url'), data.get('author'), data.get('category')))
                article = cur.fetchone()
                conn.commit()
                self.send_json_response({'success': True, 'data': article})
            
            elif action == 'delete':
                cur.execute("DELETE FROM articles WHERE id = %s", (data.get('id'),))
                conn.commit()
                self.send_json_response({'success': True, 'message': 'مقاله حذف شد'})
        
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()

    def handle_product_rate(self, data):
        """امتیازدهی به محصول"""
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        rating = data.get('rating', 5)
        
        if not user_id or not product_id:
            self.send_json_response({'success': False, 'message': 'اطلاعات ناقص است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO product_ratings (user_id, product_id, rating)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, product_id) 
                DO UPDATE SET rating = %s
            """, (user_id, product_id, rating, rating))
            conn.commit()
            self.send_json_response({'success': True, 'message': 'امتیاز شما ثبت شد'})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()

    def handle_product_favorite(self, data):
        """افزودن/حذف از علاقه‌مندی‌ها"""
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        action = data.get('action', 'add')
        
        if not user_id or not product_id:
            self.send_json_response({'success': False, 'message': 'اطلاعات ناقص است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor()
        try:
            if action == 'add':
                cur.execute("""
                    INSERT INTO favorites (user_id, product_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (user_id, product_id))
            else:
                cur.execute("DELETE FROM favorites WHERE user_id = %s AND product_id = %s", (user_id, product_id))
            conn.commit()
            self.send_json_response({'success': True, 'message': 'عملیات با موفقیت انجام شد'})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()

    def handle_user_profile(self, data):
        """دریافت/به‌روزرسانی پروفایل کاربر"""
        user_id = data.get('user_id')
        
        if not user_id:
            self.send_json_response({'success': False, 'message': 'کاربر وارد نشده است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            if data.get('action') == 'update':
                cur.execute("""
                    UPDATE users 
                    SET username = %s, phone = %s, address = %s, birth_date = %s
                    WHERE id = %s
                """, (data.get('username'), data.get('phone'), data.get('address'), 
                      data.get('birth_date'), user_id))
                conn.commit()
            
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            
            if user:
                user.pop('password', None)
                self.send_json_response({'success': True, 'data': user})
            else:
                self.send_json_response({'success': False, 'message': 'کاربر یافت نشد'})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()

    def handle_user_orders(self, data):
        """دریافت سفارشات کاربر"""
        user_id = data.get('user_id')
        
        if not user_id:
            self.send_json_response({'success': False, 'message': 'کاربر وارد نشده است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("""
                SELECT o.*, 
                    json_agg(json_build_object('product_id', oi.product_id, 'title', p.title, 'quantity', oi.quantity, 'price', oi.price)) as items
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                LEFT JOIN products p ON oi.product_id = p.id
                WHERE o.user_id = %s
                GROUP BY o.id
                ORDER BY o.created_at DESC
            """, (user_id,))
            orders = cur.fetchall()
            self.send_json_response({'success': True, 'data': orders})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()

    def handle_article_rate(self, data):
        """امتیازدهی به مقاله"""
        user_id = data.get('user_id')
        article_id = data.get('article_id')
        rating = data.get('rating', 5)
        
        if not user_id or not article_id:
            self.send_json_response({'success': False, 'message': 'اطلاعات ناقص است'})
            return
        
        conn = get_db_connection()
        if not conn:
            self.send_json_response({'success': False, 'message': 'خطا در اتصال به دیتابیس'})
            return
        
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO article_ratings (user_id, article_id, rating)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, article_id) 
                DO UPDATE SET rating = %s
            """, (user_id, article_id, rating, rating))
            conn.commit()
            self.send_json_response({'success': True, 'message': 'امتیاز شما ثبت شد'})
        except Exception as e:
            self.send_json_response({'success': False, 'message': f'خطا: {str(e)}'})
        finally:
            cur.close()
            conn.close()

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        self.wfile.write(
            json.dumps(
            data,
            ensure_ascii=False,
            default=str
        ).encode('utf-8')
        ) 
    # def send_json_response(self, data):
    #     """ارسال پاسخ JSON"""
    #     self.send_response(200)
    #     self.send_header('Content-type', 'application/json; charset=utf-8')
    #     self.send_header('Access-Control-Allow-Origin', '*')
    #     self.end_headers()
    #     self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def serve_error(self, code):
        """نمایش صفحه خطا"""
        if code == 400:
            title = "خطای 400 - درخواست نامعتبر"
            message = "درخواست ارسالی شما نامعتبر است."
        elif code == 404:
            title = "خطای 404 - صفحه یافت نشد"
            message = "صفحه‌ای که جستجو می‌کنید وجود ندارد."
        elif code == 500:
            title = "خطای 500 - خطای سرور"
            message = "متأسفانه خطایی در سرور رخ داده است."
        else:
            title = f"خطای {code}"
            message = "خطایی رخ داده است."
        
        error_html = f"""
        <!DOCTYPE html>
        <html lang="fa" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="stylesheet" href="/static/css/style.css">
            <style>
                .error-page {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    text-align: center;
                    color: white;
                }}
                .error-content {{
                    padding: 40px;
                }}
                .error-code {{
                    font-size: 120px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                .error-message {{
                    font-size: 24px;
                    margin-bottom: 30px;
                }}
                .btn-home {{
                    display: inline-block;
                    padding: 15px 30px;
                    background: white;
                    color: #667eea;
                    text-decoration: none;
                    border-radius: 30px;
                    font-weight: bold;
                    transition: transform 0.3s;
                }}
                .btn-home:hover {{
                    transform: scale(1.05);
                }}
            </style>
        </head>
        <body>
            <div class="error-page">
                <div class="error-content">
                    <div class="error-code">{code}</div>
                    <div class="error-message">{message}</div>
                    <a href="/" class="btn-home">بازگشت به صفحه اصلی</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(error_html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """لاگ درخواست‌ها"""
        print(f"[{self.log_date_time_string()}] {args[0]}")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, NursimedHandler)
    print(f"🚀 سرور نرسیمد در حال اجرا روی پورت {port}")
    print(f"📍 آدرس: http://localhost:{port}")
    print(f"📧 اکانت ادمین: {ADMIN_EMAIL}")
    print(f"🔑 رمز عبور: {ADMIN_PASS}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
