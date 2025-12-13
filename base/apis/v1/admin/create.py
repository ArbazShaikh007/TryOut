from flask import request, make_response, render_template, jsonify, url_for, redirect
from flask_restful import Resource
from datetime import datetime, timedelta
import os
import jwt
import secrets
import random
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from base.apis.v1.admin.models import Admin,admin_login_required,PlayerPool,Athletes,Teams
from base.database.db import db
# from base.common.utils import user_send_reset_email,upload_photos_local,upload_photos,send_otp
from base.common.utils import create_response
from base.apis.v1.admin.schema import AdminSchema,LoginSchema
from base.common.helpers import generate_token
from base.apis.v1.user.models import User

from dotenv import load_dotenv
from pathlib import Path
from base.common.helpers import validate_schema

# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)

load_dotenv()

class AddUserResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:

            data = request.get_json() or {}

            # admin_schema = AdminSchema()
            #
            # is_valid, result, status = validate_schema(admin_schema, data)
            # if not is_valid:
            #     return result, status

            name = data.get("name")
            email = data.get("email")
            password = data.get("password")

            hashed_password = generate_password_hash(password)

            validate_user = User.query.filter_by(email=email,is_deleted = False).first()

            if validate_user:
                if validate_user.is_block == True:
                    return jsonify({'status':0,'message': "Your account has been blocked by admin.."})

                return jsonify({'status':0,'message': "Email already exists. Please try another one."})

            add_user = User(
                name=name,
                email=email,
                password=hashed_password,
                created_time=datetime.utcnow(),
                subadmin_id = active_user.id,
                token_version = 1
            )

            db.session.add(add_user)
            db.session.commit()

            # token = generate_token(add_user.id, os.getenv("ADMIN_SECRET_KEY"))

            return jsonify({'status': 1,'message': "User added successfully."})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

class CreatePlayerPoolResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:

            data = request.get_json() or {}

            # admin_schema = AdminSchema()
            #
            # is_valid, result, status = validate_schema(admin_schema, data)
            # if not is_valid:
            #     return result, status

            name = data.get("name")
            user_id = data.get("user_id")

            add_player_pool = PlayerPool(
                name=name,
                created_time=datetime.utcnow(),
                user_id=user_id,
                subadmin_id = active_user.id
            )

            db.session.add(add_player_pool)
            db.session.commit()

            return jsonify({'status': 1,'message': "Player pool added successfully."})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

class CreateAthleteResource(Resource):
    @admin_login_required
    def post(self, active_user):

        try:
            data = request.get_json() or {}

            # admin_schema = AdminSchema()
            #
            # is_valid, result, status = validate_schema(admin_schema, data)
            # if not is_valid:
            #     return result, status

            name = data.get("name")
            jeresy_no = data.get("jeresy_no")
            pool_id = data.get("pool_id")

            get_pool_data = PlayerPool.query.filter_by(id = pool_id,is_deleted = False).first()
            if not get_pool_data:
                return jsonify({'status': 0,'message': 'Invalid data'})

            add_athlete = Athletes(
                name=name,
                jeresy_no=jeresy_no,
                created_time=datetime.utcnow(),
                user_id=get_pool_data.user_id,
                subadmin_id = active_user.id,
                pool_id=pool_id
            )

            db.session.add(add_athlete)
            db.session.commit()

            return jsonify({'status': 1,'message': "Athlete added successfully."})

        except Exception as e:
            # db.session.rollback()
            print('errorrrrrrrrrrrrr:', str(e))
            return jsonify({'status': 0, 'message': 'Something went wrong'}), 500

class CreateTeamsResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:

            data = request.get_json() or {}

            # admin_schema = AdminSchema()
            #
            # is_valid, result, status = validate_schema(admin_schema, data)
            # if not is_valid:
            #     return result, status

            name = data.get("name")
            user_id = data.get("user_id")

            if not name:
                return create_response(0,"Please provide name")
            if not user_id:
                return create_response(0,"Please provide coach")

            get_user = User.query.filter_by(id = user_id, is_deleted = False).first()
            if not get_user:
                return create_response(0,"Invalid coach")

            add_new_team = Teams(
                name=name,
                created_time=datetime.utcnow(),
                user_id=user_id,
                subadmin_id = active_user.id
            )

            db.session.add(add_new_team)
            db.session.commit()

            return jsonify({'status': 1,'message': "Team added successfully."})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500