import time
import asyncio # <--- Добавь импорт asyncio
from flask import (render_template, flash, redirect, url_for, request, Blueprint,
                   current_app, session)
from flask_login import login_user, logout_user, current_user
from app import db
from app.forms import OtpForm
from app.models import User
from app.utils import generate_otp, send_telegram_otp

bp = Blueprint('auth', __name__)

@bp.route('/request_otp')
def request_otp():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_index'))

    otp_code = generate_otp()
    expiry_time = time.time() + current_app.config['OTP_EXPIRY_SECONDS']
    session['otp_code'] = otp_code
    session['otp_ts'] = expiry_time
    session['otp_attempts'] = 0

    send_successful = asyncio.run(send_telegram_otp(otp_code))

    if send_successful:
        flash('Код подтверждения отправлен в ваш Telegram.', 'info')
    else:
        flash('Не удалось отправить код в Telegram. Проверьте настройки и логи сервера.', 'danger')

    return redirect(url_for('auth.verify_otp'))

@bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_index'))

    form = OtpForm()

    stored_code = session.get('otp_code')
    stored_ts = session.get('otp_ts')
    if not stored_code or not stored_ts:
         flash('Сначала запросите код доступа.', 'warning')
         return redirect(url_for('main.index'))

    if form.validate_on_submit():
        entered_otp = form.otp.data
        attempts = session.get('otp_attempts', 0)

        if attempts >= 5:
            session.pop('otp_code', None)
            session.pop('otp_ts', None)
            session.pop('otp_attempts', None)
            flash('Слишком много неверных попыток. Запросите код заново.', 'danger')
            return redirect(url_for('main.index'))

        if time.time() > stored_ts:
            session.pop('otp_code', None)
            session.pop('otp_ts', None)
            session.pop('otp_attempts', None)
            flash('Код подтверждения истек. Запросите новый.', 'warning')
            return redirect(url_for('auth.request_otp'))

        if entered_otp == stored_code:
            session.pop('otp_code', None)
            session.pop('otp_ts', None)
            session.pop('otp_attempts', None)

            admin_user = User.query.get(current_app.config['ADMIN_USER_ID'])
            if not admin_user:
                admin_user = User(id=current_app.config['ADMIN_USER_ID'],
                                  username=current_app.config['ADMIN_USERNAME'])
                db.session.add(admin_user)
                try:
                    db.session.commit()
                    flash('Учетная запись администратора создана.', 'info')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Не удалось создать пользователя: {e}', 'danger')
                    print(f"Ошибка создания админа: {e}")
                    return render_template('auth/verify_otp.html', title='Подтверждение кода', form=form)


            login_user(admin_user, remember=True)

            next_page = request.args.get('next')
            try:
                from urllib.parse import urlparse
            except ImportError:
                from urlparse import urlparse

            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('admin_index')
            flash('Вход выполнен успешно!', 'success')
            return redirect(next_page)
        else:
            session['otp_attempts'] = attempts + 1
            flash(f'Неверный код. Осталось попыток: {5 - session["otp_attempts"]}', 'danger')

    return render_template('auth/verify_otp.html', title='Подтверждение кода', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect("/")
