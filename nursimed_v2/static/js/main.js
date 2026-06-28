// فایل جاوااسکریپت اصلی سایت نرسیمد

// تولید session ID برای سبد خرید
function getSessionId() {
    let sessionId = localStorage.getItem('nursimed_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('nursimed_session_id', sessionId);
    }
    return sessionId;
}

// بارگذاری محصولات در صفحه اصلی
async function loadHomeProducts() {
    const container = document.getElementById('homeProducts');
    if (!container) return;
    
    try {
        const response = await fetch('/api/products');
        const data = await response.json();
        
        if (data.products && data.products.length > 0) {
            container.innerHTML = data.products.slice(0, 4).map(product => `
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-book-medical"></i>
                    </div>
                    <div class="product-info">
                        <h3 class="product-title">${product.title}</h3>
                        <p class="product-price">${formatPrice(product.price)} تومان</p>
                        <a href="/product/${product.id}" class="btn btn-outline btn-block">مشاهده محصول</a>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">محصولی یافت نشد.</p>';
        }
    } catch (error) {
        console.error('Error loading products:', error);
        container.innerHTML = '<p style="text-align: center; grid-column: 1/-1; color: red;">خطا در بارگذاری محصولات</p>';
    }
}

// بارگذاری مقالات در صفحه اصلی
async function loadHomeArticles() {
    const container = document.getElementById('homeArticles');
    if (!container) return;
    
    try {
        const response = await fetch('/api/articles');
        const data = await response.json();
        
        if (data.articles && data.articles.length > 0) {
            container.innerHTML = data.articles.slice(0, 3).map(article => `
                <div class="article-card">
                    <div class="article-image">
                        <i class="fas fa-file-medical-alt"></i>
                    </div>
                    <div class="article-info">
                        <h3 class="article-title">${article.title}</h3>
                        <p class="article-excerpt">${article.excerpt}</p>
                        <div class="article-meta">
                            <span><i class="fas fa-user"></i> ${article.author}</span>
                            <a href="/article/${article.id}" class="btn btn-primary">ادامه مطلب</a>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">مقاله‌ای یافت نشد.</p>';
        }
    } catch (error) {
        console.error('Error loading articles:', error);
        container.innerHTML = '<p style="text-align: center; grid-column: 1/-1; color: red;">خطا در بارگذاری مقالات</p>';
    }
}

// بارگذاری لیست محصولات در صفحه فروشگاه
async function loadProducts(category = 'all') {
    const container = document.getElementById('productsList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/products');
        const data = await response.json();
        
        if (data.products && data.products.length > 0) {
            let filteredProducts = data.products;
            if (category !== 'all') {
                filteredProducts = data.products.filter(p => p.category === category);
            }
            
            if (filteredProducts.length > 0) {
                container.innerHTML = filteredProducts.map(product => `
                    <div class="product-card">
                        <div class="product-image">
                            <i class="fas fa-book-medical"></i>
                        </div>
                        <div class="product-info">
                            <h3 class="product-title">${product.title}</h3>
                            <p class="product-price">${formatPrice(product.price)} تومان</p>
                            <a href="/product/${product.id}" class="btn btn-outline btn-block">مشاهده محصول</a>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">محصولی در این دسته‌بندی یافت نشد.</p>';
            }
        } else {
            container.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">محصولی یافت نشد.</p>';
        }
    } catch (error) {
        console.error('Error loading products:', error);
        container.innerHTML = '<p style="text-align: center; grid-column: 1/-1; color: red;">خطا در بارگذاری محصولات</p>';
    }
}

// بارگذاری لیست مقالات
async function loadArticles() {
    const container = document.getElementById('articlesList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/articles');
        const data = await response.json();
        
        if (data.articles && data.articles.length > 0) {
            container.innerHTML = data.articles.map(article => `
                <div class="article-card">
                    <div class="article-image">
                        <i class="fas fa-file-medical-alt"></i>
                    </div>
                    <div class="article-info">
                        <h3 class="article-title">${article.title}</h3>
                        <p class="article-excerpt">${article.excerpt}</p>
                        <div class="article-meta">
                            <span><i class="fas fa-user"></i> ${article.author}</span>
                            <a href="/article/${article.id}" class="btn btn-primary">ادامه مطلب</a>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">مقاله‌ای یافت نشد.</p>';
        }
    } catch (error) {
        console.error('Error loading articles:', error);
        container.innerHTML = '<p style="text-align: center; grid-column: 1/-1; color: red;">خطا در بارگذاری مقالات</p>';
    }
}

// بارگذاری جزئیات محصول
async function loadProductDetail(productId) {
    const container = document.getElementById('productContent');
    if (!container) return;
    
    try {
        const response = await fetch(`/api/product/${productId}`);
        const data = await response.json();
        
        if (data.product) {
            const product = data.product;
            container.innerHTML = `
                <div class="product-detail-grid">
                    <div class="product-detail-image">
                        <i class="fas fa-book-medical"></i>
                    </div>
                    <div class="product-detail-info">
                        <h1>${product.title}</h1>
                        <p class="product-detail-price">${formatPrice(product.price)} تومان</p>
                        <p class="product-detail-description">${product.description}</p>
                        <p><strong>نویسنده:</strong> ${product.author}</p>
                        <p><strong>دسته‌بندی:</strong> ${product.category}</p>
                        <button class="add-to-cart-btn" onclick="addToCart(${product.id})">
                            <i class="fas fa-shopping-cart"></i>
                            افزودن به سبد خرید
                        </button>
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = '<p style="text-align: center;">محصول یافت نشد.</p>';
        }
    } catch (error) {
        console.error('Error loading product:', error);
        container.innerHTML = '<p style="text-align: center; color: red;">خطا در بارگذاری محصول</p>';
    }
}

// بارگذاری جزئیات مقاله
async function loadArticleDetail(articleId) {
    const container = document.getElementById('articleContent');
    if (!container) return;
    
    try {
        const response = await fetch(`/api/article/${articleId}`);
        const data = await response.json();
        
        if (data.article) {
            const article = data.article;
            container.innerHTML = `
                <div class="article-header">
                    <h1>${article.title}</h1>
                    <div class="article-meta">
                        <span><i class="fas fa-user"></i> ${article.author}</span>
                        <span><i class="fas fa-tag"></i> ${article.category}</span>
                        <span><i class="fas fa-calendar"></i> ${new Date(article.created_at).toLocaleDateString('fa-IR')}</span>
                    </div>
                </div>
                <div class="article-body">
                    <p>${article.content.replace(/\n/g, '<br>')}</p>
                </div>
            `;
        } else {
            container.innerHTML = '<p style="text-align: center;">مقاله یافت نشد.</p>';
        }
    } catch (error) {
        console.error('Error loading article:', error);
        container.innerHTML = '<p style="text-align: center; color: red;">خطا در بارگذاری مقاله</p>';
    }
}

// افزودن به سبد خرید
async function addToCart(productId, quantity = 1) {
    const sessionId = getSessionId();
    
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                product_id: productId,
                quantity: quantity
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('محصول با موفقیت به سبد خرید اضافه شد!');
            updateCartCount();
        } else {
            alert('خطا: ' + data.error);
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        alert('خطا در افزودن به سبد خرید');
    }
}

// به‌روزرسانی تعداد سبد خرید
async function updateCartCount() {
    const sessionId = getSessionId();
    
    try {
        const response = await fetch(`/api/cart/${sessionId}`);
        const data = await response.json();
        
        const countElement = document.getElementById('cartCount');
        if (countElement) {
            countElement.textContent = data.items ? data.items.length : 0;
        }
    } catch (error) {
        console.error('Error updating cart count:', error);
    }
}

// بارگذاری سبد خرید
async function loadCart() {
    const container = document.getElementById('cartContent');
    if (!container) return;
    
    const sessionId = getSessionId();
    
    try {
        const response = await fetch(`/api/cart/${sessionId}`);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = `
                <div class="cart-items">
                    ${data.items.map(item => `
                        <div class="cart-item">
                            <div class="cart-item-image">
                                <i class="fas fa-book-medical"></i>
                            </div>
                            <div class="cart-item-info">
                                <h3>${item.product.title}</h3>
                                <p class="cart-item-price">${formatPrice(item.product.price)} تومان</p>
                            </div>
                            <div class="quantity-control">
                                <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                                <span class="quantity-value">${item.quantity}</span>
                                <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                            </div>
                            <div class="cart-item-total">
                                <strong>${formatPrice(item.item_total)} تومان</strong>
                                <button class="btn btn-outline" style="margin-right: 10px;" onclick="removeFromCart(${item.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                    <div class="cart-total">
                        <div class="total-row">
                            <span>جمع کل:</span>
                            <span>${formatPrice(data.total)} تومان</span>
                        </div>
                        <button class="checkout-btn" onclick="checkout()">
                            <i class="fas fa-credit-card"></i>
                            پرداخت
                        </button>
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="cart-empty">
                    <i class="fas fa-shopping-cart"></i>
                    <h2>سبد خرید شما خالی است</h2>
                    <p>برای مشاهده محصولات به فروشگاه مراجعه کنید</p>
                    <a href="/shop" class="btn btn-primary" style="margin-top: 1rem;">مشاهده فروشگاه</a>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading cart:', error);
        container.innerHTML = '<p style="text-align: center; color: red;">خطا در بارگذاری سبد خرید</p>';
    }
}

// به‌روزرسانی تعداد محصول در سبد
async function updateQuantity(itemId, newQuantity) {
    if (newQuantity < 1) {
        removeFromCart(itemId);
        return;
    }
    
    const sessionId = getSessionId();
    
    try {
        const response = await fetch('/api/cart/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                item_id: itemId,
                quantity: newQuantity
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadCart();
            updateCartCount();
        }
    } catch (error) {
        console.error('Error updating quantity:', error);
    }
}

// حذف از سبد خرید
async function removeFromCart(itemId) {
    const sessionId = getSessionId();
    
    try {
        const response = await fetch('/api/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                item_id: itemId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadCart();
            updateCartCount();
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
    }
}

// پرداخت
async function checkout() {
    const sessionId = getSessionId();
    
    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('سفارش شما با موفقیت ثبت شد!');
            loadCart();
            updateCartCount();
        } else {
            alert('خطا: ' + data.error);
        }
    } catch (error) {
        console.error('Error checking out:', error);
        alert('خطا در ثبت سفارش');
    }
}

// فرمت قیمت
function formatPrice(price) {
    return parseFloat(price).toLocaleString('fa-IR');
}

// ثبت نام
async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            window.location.href = '/login';
        } else {
            alert('خطا: ' + result.error);
        }
    } catch (error) {
        console.error('Error registering:', error);
        alert('خطا در ثبت نام');
    }
}

// ورود
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        username: formData.get('username'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('ورود با موفقیت انجام شد!');
            localStorage.setItem('nursimed_user', JSON.stringify(result.user));
            window.location.href = '/';
        } else {
            alert('خطا: ' + result.error);
        }
    } catch (error) {
        console.error('Error logging in:', error);
        alert('خطا در ورود');
    }
}

// تماس با ما
async function handleContact(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        message: formData.get('message')
    };
    
    try {
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            form.reset();
        } else {
            alert('خطا: ' + result.error);
        }
    } catch (error) {
        console.error('Error sending contact:', error);
        alert('خطا در ارسال پیام');
    }
}

// راه‌اندازی اولیه
document.addEventListener('DOMContentLoaded', function() {
    // بارگذاری محصولات و مقالات در صفحه اصلی
    loadHomeProducts();
    loadHomeArticles();
    
    // بارگذاری لیست محصولات در صفحه فروشگاه
    loadProducts();
    
    // بارگذاری لیست مقالات
    loadArticles();
    
    // بارگذاری جزئیات محصول
    const productDetailSection = document.querySelector('.product-detail');
    if (productDetailSection) {
        const productId = productDetailSection.getAttribute('data-product-id');
        loadProductDetail(productId);
    }
    
    // بارگذاری جزئیات مقاله
    const articleDetailSection = document.querySelector('.article-detail');
    if (articleDetailSection) {
        const articleId = articleDetailSection.getAttribute('data-article-id');
        loadArticleDetail(articleId);
    }
    
    // بارگذاری سبد خرید
    const cartPage = document.querySelector('.cart-page');
    if (cartPage) {
        loadCart();
    }
    
    // به‌روزرسانی تعداد سبد خرید
    updateCartCount();
    
    // فیلتر محصولات
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const category = this.getAttribute('data-category');
            loadProducts(category);
        });
    });
    
    // فرم ثبت نام
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // فرم ورود
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // فرم تماس با ما
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContact);
    }
});
