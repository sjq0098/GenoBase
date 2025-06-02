from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import db
from app.auth import bp
from app.forms import LoginForm, RegistrationForm, CreatorProfileForm, ManagerProfileForm, ReaderProfileForm
from app.models import Users, Creators, Managers, Readers, Genes, Proteins, Publications
from app.utils import generate_api_key
import secrets

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='登录', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(
            username=form.username.data,
            email=form.email.data,
            user_type=form.user_type.data,
            api_key=generate_api_key()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # 根据用户类型创建对应的角色记录
        if user.is_creator():
            creator = Creators(user_id=user.user_id)
            db.session.add(creator)
        elif user.is_manager():
            manager = Managers(user_id=user.user_id, access_level='limited')
            db.session.add(manager)
        elif user.is_reader():
            reader = Readers(user_id=user.user_id, subscription_type='free')
            db.session.add(reader)
        
        db.session.commit()
        flash('注册成功，请完善您的资料')
        login_user(user)
        return redirect(url_for('auth.profile'))
    return render_template('auth/register.html', title='注册', form=form)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # 根据用户类型选择合适的表单
    if current_user.is_creator():
        form = CreatorProfileForm()
        if form.validate_on_submit():
            creator = current_user.creator or Creators(user_id=current_user.user_id)
            creator.institution = form.institution.data
            creator.research_field = form.research_field.data
            if not current_user.creator:
                db.session.add(creator)
            db.session.commit()
            flash('资料已更新')
            return redirect(url_for('main.index'))
        elif request.method == 'GET' and current_user.creator:
            form.institution.data = current_user.creator.institution
            form.research_field.data = current_user.creator.research_field
        
        # 获取统计数据
        genes_count = Genes.query.filter_by(creator_id=current_user.user_id).count()
        proteins_count = Proteins.query.filter_by(creator_id=current_user.user_id).count()
        publications_count = Publications.query.filter_by(creator_id=current_user.user_id).count()
        
        return render_template('auth/creator_profile.html', 
                             title='创建者资料', 
                             form=form,
                             genes_count=genes_count,
                             proteins_count=proteins_count,
                             publications_count=publications_count)
    
    elif current_user.is_manager():
        form = ManagerProfileForm()
        if form.validate_on_submit():
            manager = current_user.manager or Managers(user_id=current_user.user_id)
            manager.department = form.department.data
            manager.access_level = form.access_level.data
            if not current_user.manager:
                db.session.add(manager)
            db.session.commit()
            flash('资料已更新')
            return redirect(url_for('main.index'))
        elif request.method == 'GET' and current_user.manager:
            form.department.data = current_user.manager.department
            form.access_level.data = current_user.manager.access_level
        return render_template('auth/manager_profile.html', title='管理员资料', form=form)
    
    elif current_user.is_reader():
        form = ReaderProfileForm()
        if form.validate_on_submit():
            reader = current_user.reader or Readers(user_id=current_user.user_id)
            reader.organization = form.organization.data
            reader.subscription_type = form.subscription_type.data
            if not current_user.reader:
                db.session.add(reader)
            db.session.commit()
            flash('资料已更新')
            return redirect(url_for('main.index'))
        elif request.method == 'GET' and current_user.reader:
            form.organization.data = current_user.reader.organization
            form.subscription_type.data = current_user.reader.subscription_type
        return render_template('auth/reader_profile.html', title='读者资料', form=form)
    
    # 默认返回
    return redirect(url_for('main.index')) 

@bp.route('/reset_api_key', methods=['POST'])
@login_required
def reset_api_key():
    current_user.api_key = generate_api_key()
    db.session.commit()
    flash('API密钥已重置')
    return redirect(url_for('auth.profile'))

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user
    # 也可以通过 user_id = request.args.get('user_id') 获取他人信息（需权限校验）

    if user.is_creator():
        form = CreatorProfileForm(obj=user.creator)
        if form.validate_on_submit():
            user.creator.institution = form.institution.data
            user.creator.research_field = form.research_field.data
            db.session.commit()
            flash('资料已更新')
            return redirect(url_for('main.user_profile', user_id=user.user_id))
        elif request.method == 'GET':
            form.institution.data = user.creator.institution
            form.research_field.data = user.creator.research_field
        return render_template('auth/edit_profile.html', form=form, user=user)

    elif user.is_manager():
        form = ManagerProfileForm(obj=user.manager)
        if form.validate_on_submit():
            user.manager.department = form.department.data
            user.manager.access_level = form.access_level.data
            db.session.commit()
            flash('资料已更新')
            return redirect(url_for('main.user_profile', user_id=user.user_id))
        elif request.method == 'GET':
            form.department.data = user.manager.department
            form.access_level.data = user.manager.access_level
        return render_template('auth/edit_profile.html', form=form, user=user)

    elif user.is_reader():
        form = ReaderProfileForm(obj=user.reader)
        if form.validate_on_submit():
            user.reader.organization = form.organization.data
            user.reader.subscription_type = form.subscription_type.data
            db.session.commit()
            flash('资料已更新')
            return redirect(url_for('main.user_profile', user_id=user.user_id))
        elif request.method == 'GET':
            form.organization.data = user.reader.organization
            form.subscription_type.data = user.reader.subscription_type
        return render_template('auth/edit_profile.html', form=form, user=user)

    flash('未知用户类型')
    return redirect(url_for('main.index'))

@bp.route('/regenerate_api_key')
@login_required
def regenerate_api_key():
    user = current_user
    user.api_key = secrets.token_hex(32)
    db.session.commit()
    flash('API Key 已重置')
    return redirect(url_for('main.user_profile', user_id=user.user_id)) 