from base.database.db import db
from datetime import datetime, timedelta
from base.common.path import COMMON_URL
from itsdangerous import URLSafeTimedSerializer as Serializer
import os
import jwt
from dotenv import load_dotenv
from flask import request
from functools import wraps
from base.common.path import generate_presigned_url
from pathlib import Path
import json

# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)

load_dotenv()

FMT = "%H:%M"  # 24h like '05:00'


def get_hourly_slots_seperate(day_name: str):
    store = Store.query.filter(Store.day == day_name).first()
    if not store or not store.open_time or not store.close_time:
        return []

    print('storeeeeeeeeeeeeeeeeeeee', store)

    start = datetime.strptime(store.open_time, FMT)
    end = datetime.strptime(store.close_time, FMT)

    # If your data can cross midnight (e.g., 22:00 -> 02:00), uncomment:
    # if end <= start:
    #     end += timedelta(days=1)

    slots = []
    cur = start
    while cur + timedelta(hours=1) <= end:
        nxt = cur + timedelta(hours=1)
        slots.append({
            "start_time": cur.strftime(FMT),
            "end_time": nxt.strftime(FMT),
        })
        cur = nxt
    return slots

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150), nullable=True)
    lastname = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    otp = db.Column(db.String(6), nullable=True)
    image_name = db.Column(db.String(150), nullable=True)
    image_path = db.Column(db.String(150), nullable=True)
    password = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())
    is_subadmin = db.Column(db.Boolean(), default=False)
    is_block = db.Column(db.Boolean(), default=False)

    country_code = db.Column(db.String(5))
    mobile_number = db.Column(db.String(20))

    def as_dict(self, token):

        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'profile_pic': self.image_path if self.image_name is not None else '',
            'created_at': str(self.created_at),
            'token': token,
            'is_subadmin': self.is_subadmin
        }

    def as_dict_admin(self):

        return {

            'id': self.id,
            'name': self.firstname + ' ' + self.lastname if self.firstname is not None else '',
            'county_code': self.country_code if self.country_code is not None else '',
            'mobile_number': self.mobile_number if self.mobile_number is not None else '',
            'email': self.email if self.email is not None else '',
            # 'image': generate_presigned_url(self.image_name) if self.image_name is not None else '',
            'image': COMMON_URL + self.image_path + self.image_name if self.image_name is not None else '',
        }

    def get_admin_token(self, expiress_sec=1800):
        serial = Serializer(os.getenv("ADMIN_SECRET_KEY"))
        return serial.dumps({'user_id': self.id})

    @staticmethod
    def verify_admin_token(token):
        serial = Serializer(os.getenv("ADMIN_SECRET_KEY"))
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return Admin.query.get(user_id)

def admin_login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if "authorization" in request.headers:
            token = request.headers["authorization"]
            print('token',token)

        if not token:
            return {"status": 0, "message": "a valid token is missing"}
        try:
            data = jwt.decode(token, os.getenv("ADMIN_SECRET_KEY"), algorithms=["HS256"])
            active_user = Admin.query.filter_by(id=data["id"]).first()
        except jwt.ExpiredSignatureError:
            return {"status": 0, "message": "Token has expired"},401
        except jwt.InvalidTokenError:
            return {"status": 0, "message": "Invalid token"},401
        except Exception as e:
            return {"status": 0, "message": f"An error occurred: {str(e)}"}

        kwargs['active_user'] = active_user

        return f( *args, **kwargs)

    return decorator

class Cms(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)

    content = db.Column(db.Text, nullable=False)

    def as_dict(self):
        return {
            'content': self.content
        }

class PlayerPool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    created_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean(), default=False)

    subadmin_id = db.Column(db.Integer, db.ForeignKey('admin.id', ondelete='CASCADE', onupdate='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))

    def as_dict(self):

        return {
            "id": self.id,
            "name": self.name
        }

class UserPlayerPool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, db.ForeignKey('player_pool.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)
    subadmin_id = db.Column(db.Integer, db.ForeignKey('admin.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False)

class PlayerPoolNotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_type = db.Column(db.String(10), default='text')
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
        input_date = datetime.strptime(str(self.created_time), "%Y-%m-%d %H:%M:%S")
        output_date = input_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return {

            'id': self.id,
            'note_type': self.note_type,
            'time_string': self.time_string,
            'audio': audio,
            'text': self.text if self.text is not None else '',
            'created_time': output_date

        }

class Athletes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    image_name = db.Column(db.String(150), default="default.png")
    image_path = db.Column(db.String(150), default="/static/user_images/")
    jeresy_no = db.Column(db.String(10), nullable=False)
    level = db.Column(db.Integer())
    position = db.Column(db.String(10))
    position_code = db.Column(db.String(10))
    status = db.Column(db.String(10),default='Not Assign')
    primary = db.Column(db.String(10))
    alt = db.Column(db.String(10))
    created_time = db.Column(db.DateTime)
    accepted_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean(), default=False)
    order = db.Column(db.Integer())

    subadmin_id = db.Column(db.Integer, db.ForeignKey('admin.id', ondelete='CASCADE', onupdate='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))
    pool_id = db.Column(db.Integer, db.ForeignKey('player_pool.id', ondelete='CASCADE', onupdate='CASCADE'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE', onupdate='CASCADE'))

    def as_dict(self):
        image = COMMON_URL + self.image_path + self.image_name

        return {
            "id": self.id,
            "name": self.name if self.name is not None else '',
            "jeresy_no": self.jeresy_no if self.jeresy_no is not None else '',
            "status": self.status if self.status is not None else '',
            "level": self.level if self.level is not None else '',
            "position": self.position if self.position is not None else '',
            "image": image,
            "primary": self.primary if self.primary is not None else '',
            "alt": self.alt if self.alt is not None else ''
        }

class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    formation = db.Column(db.String(150), default="4-2-3-1")
    created_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean(), default=False)

    subadmin_id = db.Column(db.Integer, db.ForeignKey('admin.id', ondelete='CASCADE', onupdate='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))

    def as_dict(self):
        input_date = datetime.strptime(str(self.created_time), "%Y-%m-%d %H:%M:%S")
        output_date = input_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return {
            "id": self.id,
            "name": self.name,
            "created_time": output_date,
            "formation": self.formation
        }