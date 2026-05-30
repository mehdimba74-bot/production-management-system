from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Product, Activity
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== مسیرهای احراز هویت ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('نام کاربری یا رمز عبور اشتباه است!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ==================== صفحه اصلی ====================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # واحد فروش: مشاهده همه سفارشات
    if current_user.department == 'فروش':
        products = Product.query.all()
    else:
        # واحدهای دیگر: فقط مشاهده
        products = Product.query.all()
    
    return render_template('dashboard.html', products=products)

# ==================== مسیرهای محصول ====================

@app.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    # فقط واحد فروش می‌تواند اضافه کند
    if current_user.department != 'فروش':
        flash('شما اجازه اضافه کردن سفارش ندارید!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            product = Product(
                product_type=request.form.get('product_type'),
                product_name=request.form.get('product_name'),
                brand_name=request.form.get('brand_name'),
                color=request.form.get('color'),
                finish=request.form.get('finish'),
                quantity=int(request.form.get('quantity')),
                delivery_date=datetime.strptime(request.form.get('delivery_date'), '%Y-%m-%d').date(),
                status='درحال‌انتظار',
                created_by=current_user.id,
                notes=request.form.get('notes')
            )
            db.session.add(product)
            db.session.commit()
            
            # ثبت فعالیت
            activity = Activity(
                product_id=product.id,
                user_id=current_user.id,
                action=f'محصول جدید اضافه شد'
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('سفارش با موفقیت اضافه شد!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'خطا: {str(e)}', 'danger')
    
    return render_template('add_product.html')

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # فقط واحد فروش می‌تواند ویرایش کند
    if current_user.department != 'فروش':
        flash('شما اجازه ویرایش ندارید!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            product.product_type = request.form.get('product_type')
            product.product_name = request.form.get('product_name')
            product.brand_name = request.form.get('brand_name')
            product.color = request.form.get('color')
            product.finish = request.form.get('finish')
            product.quantity = int(request.form.get('quantity'))
            product.delivery_date = datetime.strptime(request.form.get('delivery_date'), '%Y-%m-%d').date()
            product.notes = request.form.get('notes')
            
            db.session.commit()
            
            # ثبت فعالیت
            activity = Activity(
                product_id=product.id,
                user_id=current_user.id,
                action=f'محصول ویرایش شد'
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('سفارش با موفقیت ویرایش شد!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'خطا: {str(e)}', 'danger')
    
    return render_template('edit_product.html', product=product)

@app.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if current_user.department != 'فروش':
        flash('شما اجازه حذف ندارید!', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash('سفارش حذف شد!', 'success')
    except Exception as e:
        flash(f'خطا: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/product/<int:product_id>')
@login_required
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    activities = Activity.query.filter_by(product_id=product_id).order_by(Activity.timestamp.desc()).all()
    return render_template('view_product.html', product=product, activities=activities)

# ==================== خطای 404 ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# ==================== ایجاد دیتابیس ====================

@app.before_request
def create_tables():
    db.create_all()

# ==================== داده‌های نمونه ====================

@app.route('/init-db')
def init_db():
    """این صفحه فقط برای اولین‌بار برای ایجاد کاربران نمونه است"""
    
    db.create_all()
    
    # ایجاد کاربران نمونه
    users = [
        User(username='sales1', password=generate_password_hash('pass123'), department='فروش', full_name='علی - فروش'),
        User(username='plan1', password=generate_password_hash('pass123'), department='برنامه‌ریزی', full_name='رضا - برنامه‌ریزی'),
        User(username='design1', password=generate_password_hash('pass123'), department='طراحی', full_name='مریم - طراحی'),
    ]
    
    for user in users:
        if not User.query.filter_by(username=user.username).first():
            db.session.add(user)
    
    db.session.commit()
    
    return '''
    <h1>✅ دیتابیس آماده شد!</h1>
    <p>کاربران نمونه ایجاد شدند:</p>
    <ul>
        <li>نام کاربری: sales1 | رمز: pass123 | واحد: فروش</li>
        <li>نام کاربری: plan1 | رمز: pass123 | واحد: برنامه‌ریزی</li>
        <li>نام کاربری: design1 | رمز: pass123 | واحد: طراحی</li>
    </ul>
    <a href="/login">برو به ورود</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)