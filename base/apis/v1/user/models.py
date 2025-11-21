from base.database.db import db
from functools import wraps
from flask import request
import jwt, os
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from pathlib import Path
from itsdangerous import URLSafeTimedSerializer as Serializer
from base.common.path import COMMON_URL
from datetime import datetime
from base.common.path import generate_presigned_url

# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)

load_dotenv()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    name = db.Column(db.String(150))
    email = db.Column(db.String(50))
    password = db.Column(db.String(250))

    # image_name = db.Column(db.String(100))
    # image_path = db.Column(db.String(200))

    is_deleted = db.Column(db.Boolean(), default=False)
    # delete_reason = db.Column(db.String(1000))
    deleted_time = db.Column(db.DateTime)

    is_block = db.Column(db.Boolean(), default=False)
    # device_token = db.Column(db.String(500))
    # device_type = db.Column(db.String(50))

    created_time = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    token_version = db.Column(db.Integer, nullable=False, default=0)
    subadmin_id = db.Column(db.Integer)

    def get_user_token(self, expiress_sec=1800):
        serial = Serializer(os.getenv("SECRET_KEY"))
        return serial.dumps({'user_id': self.id})

    @staticmethod
    def verify_user_token(token):
        serial = Serializer(os.getenv("SECRET_KEY"))
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def as_dict(self,token=""):

        return {

            'id': str(self.id),
            'name': self.name if self.name is not None else '',
            'email': self.email if self.email is not None else '',
            'token': token

            # 'country_code': self.country_code if self.country_code is not None else '',
            # 'mobile': self.mobile_number if self.mobile_number is not None else '',
            # 'image': generate_presigned_url(self.image_name) if self.image_name is not None else '',
            # 'notification_button': self.is_notification,
            # 'device_type': self.device_type if self.device_type is not None else '',
            # 'device_token': self.device_token if self.device_token is not None else '',
            # 'last_login_date_and_time': self.last_login,
        }

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "authorization" in request.headers:
            token = request.headers["authorization"]
        if not "authorization" in request.headers:
            return {'status': 0,'message': 'Authorization is missing'}, 401

        if not token:
            return {"status": 0, "message": "a valid token is missing"}, 401
        try:
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            token_version_in_token = data.get("token_version")

            active_user = User.query.filter_by(id=data["id"]).first()

            if active_user is None:
                return {'status': 0, 'message': 'Invalid user'}, 401

            if active_user.is_block == True:
                return {'status': 0, 'message': "Your account has been blocked by the admin. Please contact the admin to reactivate your account."}, 401

            if active_user.is_deleted == True:
                return {'status': 0, 'message': "Your account is deleted."}, 401

            if token_version_in_token is None or (token_version_in_token != (active_user.token_version or 0)):
                message = "Session expired. You signed in on another device."

                return {'status': 0, 'message': message}, 401

        except jwt.ExpiredSignatureError:
            return {"status": 0, "message": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"status": 0, "message": "Invalid token"}, 401
        except Exception as e:
            return {"status": 0, "message": f"An error occurred: {str(e)}"}, 401

        if not active_user:
            return {'status': 0, 'message': 'Invalid user'}, 401

        active_user.last_login = datetime.utcnow()
        db.session.commit()

        kwargs['active_user'] = active_user

        return f(*args, **kwargs)

    return decorator

class AthleteIdpNotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_type = db.Column(db.String(10), nullable=False)
    time_string = db.Column(db.String(80), nullable=True)
    audio_name = db.Column(db.String(40), nullable=True)
    audio_path = db.Column(db.String(80), nullable=True)
    text = db.Column(db.Text(), nullable=True)
    created_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean(), default=False)

    pool_id = db.Column(db.Integer, db.ForeignKey('player_pool.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False)

    def as_dict(self):
        audio = COMMON_URL + self.audio_path + self.audio_name if self.audio_name is not None else ''

        return {

            'id': self.id,
            'note_type': self.note_type,
            'time_string': self.time_string,
            'audio': audio,
            'text': self.text if self.text is not None else ''

        }