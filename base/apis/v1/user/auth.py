import jwt
import os
from datetime import datetime, timedelta
from flask import request, jsonify,make_response,render_template,redirect,url_for
from flask_restful import Resource
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from base.database.db import db
from dotenv import load_dotenv
from pathlib import Path
# from base.common.utils import push_notification,upload_photos_local,upload_photos,user_send_reset_email
from base.apis.v1.user.models import User,token_required
from base.common.helpers import generate_token
# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)

load_dotenv()

class UserLoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()

            email = data.get('email')
            password = data.get('password')

            check_email = User.query.filter_by(email=email, is_deleted=False).first()

            if check_email:
                if check_email.is_block == True:
                    return jsonify({'status': 0, 'message': 'Your account blocked by admin with this email.'})

            if not check_email:
                return jsonify({'status':0, 'message':'Invalid email,please try again'})


            if check_email and check_email.check_password(password):
                # none_exitsting_device_token = User.query.filter_by(device_token=device_token).first()
                # if none_exitsting_device_token:
                #     none_exitsting_device_token.device_token = None
                #     none_exitsting_device_token.device_type = None
                #     db.session.commit()

                # check_email.device_token = device_token
                # check_email.device_type = device_type
                # db.session.commit()

                check_email.token_version = (check_email.token_version or 0) + 1
                db.session.commit()

                print('check_email.token_version',check_email.token_version)

                token = generate_token(check_email.id, os.getenv("SECRET_KEY"),check_email.token_version)

                return jsonify({ 'status': 1, 'message':'Login successfully','data': check_email.as_dict(token)})
            else:
                return jsonify({ 'status': 0, 'message': 'Incorrect Password, try again.'})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500