// جاوااسکریپت ساده برای سایت نرسیمد

// وقتی صفحه لود شد
document.addEventListener('DOMContentLoaded', function() {
    console.log('سایت نرسیمد بارگذاری شد');
    
    // اضافه کردن کلاس active به منوی فعلی
    var currentPage = window.location.pathname;
    var navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPage) {
            link.style.opacity = '0.7';
        }
    });
    
    // انیمیشن ساده برای کارت‌ها
    var cards = document.querySelectorAll('.service-card, .article-card');
    cards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            console.log('کارت هاور شد');
        });
    });
});

// تابع برای نمایش پیام خوش‌آمدگویی
function showWelcomeMessage() {
    alert('به نرسیمد خوش آمدید!');
}

// تابع برای اعتبارسنجی فرم
function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return false;
    
    var inputs = form.querySelectorAll('input[required], textarea[required]');
    var isValid = true;
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.style.borderColor = 'red';
            isValid = false;
        } else {
            input.style.borderColor = '#ddd';
        }
    });
    
    if (!isValid) {
        alert('لطفا تمام فیلدهای الزامی را پر کنید');
    }
    
    return isValid;
}
