// Nursimed - کدهای جاوااسکریپت اصلی

// متغیرهای سراسری
let currentUser = null;
let cartCount = 0;

// اجرای کدها پس از لود شدن صفحه
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

// مقداردهی اولیه برنامه
function initApp() {
    loadUserFromStorage();
    updateCartCount();
    setupEventListeners();
    
    // بارگذاری داده‌ها بر اساس صفحه فعلی
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index.html') {
        loadHomeData();
    } else if (path === '/shop') {
        loadProducts();
    } else if (path === '/articles') {
        loadArticles();
    } else if (path.startsWith('/product/')) {
        loadProductDetail();
    } else if (path.startsWith('/article/')) {
        loadArticleDetail();
    } else if (path === '/cart') {
        loadCart();
    } else if (path === '/admin') {
        loadAdminPanel();
    }
}

// تنظیم رویدادها
function setupEventListeners() {
    // فرم ورود
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // فرم ثبت نام
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // فرم تماس با ما
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContact);
    }
    
    // دکمه افزودن به سبد
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', handleAddToCart);
    });
    
    // کلیک روی آیکون سبد خرید
    const cartIcon = document.querySelector('.cart-icon-wrapper');
    if (cartIcon) {
        cartIcon.addEventListener('click', () => {
            window.location.href = '/cart';
        });
    }
}

// ========== توابع API ==========

async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, message: 'خطا در ارتباط با سرور' };
    }
}

// ========== مدیریت کاربر ==========

function loadUserFromStorage() {
    const userStr = localStorage.getItem('nursimed_user');
    if (userStr) {
        currentUser = JSON.parse(userStr);
        updateAuthButtons();
    }
}

function saveUser(user) {
    currentUser = user;
    localStorage.setItem('nursimed_user', JSON.stringify(user));
    updateAuthButtons();
}

function logout() {
    currentUser = null;
    localStorage.removeItem('nursimed_user');
    updateAuthButtons();
    showToast('خروج موفقیت‌آمیز بود', 'success');
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

function updateAuthButtons() {
    const authContainer = document.querySelector('.auth-buttons');
    if (!authContainer) return;
    
    if (currentUser) {
        authContainer.innerHTML = `
            <span style="color: var(--primary); font-weight: 600; padding: 10px;">
                👤 ${currentUser.username}
            </span>
            ${currentUser.is_admin ? `<a href="/admin" class="btn btn-outline">پنل ادمین</a>` : ''}
            <button onclick="logout()" class="btn btn-outline">خروج</button>
        `;
    } else {
        authContainer.innerHTML = `
            <a href="/login" class="btn btn-outline">ورود</a>
            <a href="/register" class="btn btn-primary">ثبت نام</a>
        `;
    }
}

// ========== ورود و ثبت نام ==========

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const result = await apiRequest('/api/login', 'POST', { email, password });
    
    if (result.success) {
        saveUser(result.user);
        showToast(result.message, 'success');
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
    } else {
        showToast(result.message, 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const result = await apiRequest('/api/register', 'POST', { username, email, password });
    
    if (result.success) {
        showToast(result.message, 'success');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
    } else {
        showToast(result.message, 'error');
    }
}

// ========== سبد خرید ==========

function updateCartCount() {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        const count = localStorage.getItem('nursimed_cart_count') || 0;
        cartCount = parseInt(count);
        badge.textContent = cartCount;
        badge.style.display = cartCount > 0 ? 'flex' : 'none';
    }
}

async function handleAddToCart(e) {
    e.preventDefault();
    
    if (!currentUser) {
        showToast('برای افزودن به سبد خرید، ابتدا وارد شوید', 'warning');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
        return;
    }
    
    const productId = this.dataset.productId;
    
    const result = await apiRequest('/api/cart/add', 'POST', {
        user_id: currentUser.id,
        product_id: productId,
        quantity: 1
    });
    
    if (result.success) {
        cartCount++;
        localStorage.setItem('nursimed_cart_count', cartCount);
        updateCartCount();
        showToast(result.message, 'success');
        
        // انیمیشن آیکون سبد
        const cartIcon = document.querySelector('.cart-icon-wrapper');
        if (cartIcon) {
            cartIcon.style.transform = 'scale(1.2)';
            setTimeout(() => {
                cartIcon.style.transform = 'scale(1)';
            }, 300);
        }
    } else {
        showToast(result.message, 'error');
    }
}

async function loadCart() {
    if (!currentUser) {
        document.querySelector('.cart-container').innerHTML = `
            <div class="empty-cart">
                <div class="empty-cart-icon">🛒</div>
                <p class="empty-cart-text">برای مشاهده سبد خرید باید وارد شوید</p>
                <a href="/login" class="btn btn-primary">ورود به حساب</a>
            </div>
        `;
        return;
    }
    
    const result = await apiRequest('/api/cart/get', 'POST', { user_id: currentUser.id });
    
    if (result.success && result.data.length > 0) {
        renderCartItems(result.data, result.total);
    } else {
        document.querySelector('.cart-container').innerHTML = `
            <div class="empty-cart">
                <div class="empty-cart-icon">🛒</div>
                <p class="empty-cart-text">سبد خرید شما خالی است</p>
                <a href="/shop" class="btn btn-primary">مشاهده فروشگاه</a>
            </div>
        `;
    }
}

function renderCartItems(items, total) {
    const container = document.querySelector('.cart-container');
    if (!container) return;
    
    let html = `
        <h1 class="cart-title">🛒 سبد خرید</h1>
        <div class="cart-items">
    `;
    
    items.forEach(item => {
        const itemTotal = item.price * item.quantity;
        html += `
            <div class="cart-item" data-product-id="${item.product_id}">
                <img src="${item.image_url}" alt="${item.title}" class="cart-item-image">
                <div class="cart-item-info">
                    <h3 class="cart-item-title">${item.title}</h3>
                    <p class="cart-item-price">${item.price.toLocaleString()} تومان</p>
                </div>
                <div class="cart-item-quantity">
                    <button class="qty-btn" onclick="updateCartItem(${item.product_id}, ${item.quantity - 1})">−</button>
                    <span class="qty-value">${item.quantity}</span>
                    <button class="qty-btn" onclick="updateCartItem(${item.product_id}, ${item.quantity + 1})">+</button>
                </div>
                <div class="cart-item-total">${itemTotal.toLocaleString()} تومان</div>
                <button class="cart-item-remove" onclick="removeCartItem(${item.product_id})">🗑️</button>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="cart-summary">
            <div class="summary-row">
                <span class="summary-label">تعداد محصولات:</span>
                <span class="summary-value">${items.reduce((sum, item) => sum + item.quantity, 0)} عدد</span>
            </div>
            <div class="summary-row summary-total">
                <span class="summary-label">مبلغ قابل پرداخت:</span>
                <span class="summary-value">${total.toLocaleString()} تومان</span>
            </div>
            <button class="btn btn-success form-btn" style="margin-top: 20px;" onclick="handleCheckout()">
                💳 پرداخت آنلاین
            </button>
        </div>
    `;
    
    container.innerHTML = html;
}

async function updateCartItem(productId, newQuantity) {
    if (!currentUser) return;
    
    const result = await apiRequest('/api/cart/update', 'POST', {
        user_id: currentUser.id,
        product_id: productId,
        quantity: newQuantity
    });
    
    if (result.success) {
        if (newQuantity <= 0) {
            cartCount--;
            localStorage.setItem('nursimed_cart_count', cartCount);
            updateCartCount();
        }
        loadCart();
        showToast('سبد خرید به‌روزرسانی شد', 'success');
    }
}

async function removeCartItem(productId) {
    if (!currentUser) return;
    
    const result = await apiRequest('/api/cart/remove', 'POST', {
        user_id: currentUser.id,
        product_id: productId
    });
    
    if (result.success) {
        cartCount--;
        localStorage.setItem('nursimed_cart_count', cartCount);
        updateCartCount();
        loadCart();
        showToast(result.message, 'success');
    }
}

function handleCheckout() {
    showToast('در حال انتقال به درگاه پرداخت...', 'success');
    setTimeout(() => {
        alert('پرداخت با موفقیت انجام شد! (نمایشی)');
    }, 2000);
}

// ========== بارگذاری محصولات ==========

async function loadProducts() {
    const result = await apiRequest('/api/products');
    
    if (result.success) {
        renderProducts(result.data);
    } else {
        showToast('خطا در بارگذاری محصولات', 'error');
    }
}

function renderProducts(products) {
    const grid = document.querySelector('.products-grid');
    if (!grid) return;
    
    if (products.length === 0) {
        grid.innerHTML = '<p style="text-align: center; color: var(--gray);">محصولی یافت نشد</p>';
        return;
    }
    
    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <div class="product-image-wrapper">
                <img src="${product.image_url}" alt="${product.title}" class="product-image">
                <span class="product-badge">جدید</span>
            </div>
            <div class="product-info">
                <span class="product-category">${product.category}</span>
                <h3 class="product-title">${product.title}</h3>
                <p class="product-desc">${product.description}</p>
                <div class="product-footer">
                    <span class="product-price"><span>قیمت:</span>${product.price.toLocaleString()} تومان</span>
                    <button class="btn btn-primary btn-add-cart add-to-cart-btn" data-product-id="${product.id}">
                        🛒 افزودن
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    // اضافه کردن رویداد به دکمه‌های جدید
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', handleAddToCart);
    });
}

// ========== بارگذاری مقالات ==========

async function loadArticles() {
    const result = await apiRequest('/api/articles');
    
    if (result.success) {
        renderArticles(result.data);
    } else {
        showToast('خطا در بارگذاری مقالات', 'error');
    }
}

function renderArticles(articles) {
    const grid = document.querySelector('.articles-grid');
    if (!grid) return;
    
    if (articles.length === 0) {
        grid.innerHTML = '<p style="text-align: center; color: var(--gray);">مقاله‌ای یافت نشد</p>';
        return;
    }
    
    grid.innerHTML = articles.map(article => {
        const authorInitials = article.author ? article.author.charAt(0) : '?';
        return `
            <div class="article-card">
                <img src="${article.image_url}" alt="${article.title}" class="article-image">
                <div class="article-content">
                    <div class="article-meta">
                        <span class="article-meta-item">📅 ${new Date(article.created_at).toLocaleDateString('fa-IR')}</span>
                        <span class="article-meta-item">👁️ ${article.views || 0} بازدید</span>
                    </div>
                    <h3 class="article-title">${article.title}</h3>
                    <p class="article-excerpt">${article.excerpt}</p>
                    <div class="article-footer">
                        <div class="article-author">
                            <div class="author-avatar">${authorInitials}</div>
                            <span>${article.author}</span>
                        </div>
                        <a href="/article/${article.id}" class="article-read-more">
                            ادامه مطلب ←
                        </a>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// ========== بارگذاری صفحه اصلی ==========

async function loadHomeData() {
    // بارگذاری محصولات ویژه
    const productsResult = await apiRequest('/api/products');
    if (productsResult.success) {
        const featuredProducts = productsResult.data.slice(0, 3);
        renderFeaturedProducts(featuredProducts);
    }
    
    // بارگذاری مقالات اخیر
    const articlesResult = await apiRequest('/api/articles');
    if (articlesResult.success) {
        const recentArticles = articlesResult.data.slice(0, 3);
        renderRecentArticles(recentArticles);
    }
}

function renderFeaturedProducts(products) {
    const grid = document.querySelector('.featured-products-grid');
    if (!grid) return;
    
    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <div class="product-image-wrapper">
                <img src="${product.image_url}" alt="${product.title}" class="product-image">
            </div>
            <div class="product-info">
                <span class="product-category">${product.category}</span>
                <h3 class="product-title">${product.title}</h3>
                <div class="product-footer">
                    <span class="product-price">${product.price.toLocaleString()} تومان</span>
                    <a href="/product/${product.id}" class="btn btn-primary btn-add-cart">مشاهده</a>
                </div>
            </div>
        </div>
    `).join('');
}

function renderRecentArticles(articles) {
    const grid = document.querySelector('.recent-articles-grid');
    if (!grid) return;
    
    grid.innerHTML = articles.map(article => `
        <div class="article-card">
            <img src="${article.image_url}" alt="${article.title}" class="article-image">
            <div class="article-content">
                <h3 class="article-title">${article.title}</h3>
                <p class="article-excerpt">${article.excerpt}</p>
                <a href="/article/${article.id}" class="article-read-more">ادامه مطلب ←</a>
            </div>
        </div>
    `).join('');
}

// ========== جزئیات محصول ==========

function loadProductDetail() {
    const path = window.location.pathname;
    const productId = path.split('/').pop();
    
    if (!productId) return;
    
    // نمایش اطلاعات محصول (از تمپلیت سرور آمده)
    const addToCartBtn = document.querySelector('.add-to-cart-btn');
    if (addToCartBtn) {
        addToCartBtn.dataset.productId = productId;
        addToCartBtn.addEventListener('click', handleAddToCart);
    }
}

// ========== جزئیات مقاله ==========

function loadArticleDetail() {
    // اطلاعات مقاله از تمپلیت سرور آمده است
    // فقط می‌توانیم کارهای اضافی انجام دهیم
}

// ========== تماس با ما ==========

async function handleContact(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const subject = document.getElementById('subject').value;
    const message = document.getElementById('message').value;
    
    const result = await apiRequest('/api/contact', 'POST', { name, email, subject, message });
    
    if (result.success) {
        showToast(result.message, 'success');
        e.target.reset();
    } else {
        showToast(result.message, 'error');
    }
}

// ========== پنل ادمین ==========

function loadAdminPanel() {
    if (!currentUser || !currentUser.is_admin) {
        window.location.href = '/login';
        return;
    }
    
    setupAdminTabs();
    loadAdminProducts();
}

function setupAdminTabs() {
    const tabs = document.querySelectorAll('.admin-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            const section = tab.dataset.section;
            document.querySelectorAll('.admin-section').forEach(s => s.style.display = 'none');
            document.getElementById(section).style.display = 'block';
        });
    });
}

async function loadAdminProducts() {
    const result = await apiRequest('/api/admin/products', 'POST', { action: 'get_all' });
    
    if (result.success) {
        renderAdminProductsTable(result.data);
    }
}

function renderAdminProductsTable(products) {
    const tbody = document.querySelector('#productsSection tbody');
    if (!tbody) return;
    
    tbody.innerHTML = products.map(p => `
        <tr>
            <td>${p.id}</td>
            <td>${p.title}</td>
            <td>${p.category}</td>
            <td>${p.price.toLocaleString()}</td>
            <td>${p.stock}</td>
            <td>
                <button class="btn btn-danger" style="padding: 5px 10px;" onclick="deleteProduct(${p.id})">حذف</button>
            </td>
        </tr>
    `).join('');
}

async function deleteProduct(id) {
    if (!confirm('آیا مطمئن هستید؟')) return;
    
    const result = await apiRequest('/api/admin/products', 'POST', { action: 'delete', id });
    
    if (result.success) {
        showToast(result.message, 'success');
        loadAdminProducts();
    } else {
        showToast(result.message, 'error');
    }
}

// ========== Toast Notifications ==========

function showToast(message, type = 'success') {
    const container = document.querySelector('.toast-container') || createToastContainer();
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    // حذف خودکار پس از 4 ثانیه
    setTimeout(() => {
        toast.style.animation = 'slideInLeft 0.4s ease reverse';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// ========== Utility Functions ==========

function formatPrice(price) {
    return price.toLocaleString('fa-IR') + ' تومان';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
}

// خروجی برای دیباگ
console.log('🏥 Nursimed App Loaded Successfully');
