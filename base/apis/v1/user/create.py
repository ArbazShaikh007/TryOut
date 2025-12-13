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
from base.common.utils import create_response,upload_audio_local,delete_audio_local
    # push_notification,upload_photos_local,upload_photos,user_send_reset_email
from base.apis.v1.user.models import User,token_required
from base.apis.v1.admin.models import PlayerPool,Athletes,PlayerPoolNotes,Teams

class TeamFormationResource(Resource):
    @token_required
    def post(self,active_user):
        try:
            data = request.get_json() or {}

            team_id = data.get("team_id")
            formation = data.get("formation")

            if not team_id:
                return jsonify({"status": 0,"messege": "Please select team first"})
            if not formation:
                return jsonify({"status": 0,"messege": "Please provide formation"})

            get_team_data = Teams.query.filter_by(id = team_id,is_deleted = False,user_id = active_user.id).first()
            if not get_team_data:
                return jsonify({"status": 0,"messege": "Invalid team data"})

            get_team_data.formation =formation
            db.session.commit()

            return jsonify({'status': 1,'messege': 'Formation updated successfully','formation': formation})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

class CreatePlayerPoolNotesResource(Resource):
    @token_required
    def post(self,active_user):
        try:
            # data = request.form

            data = request.get_json()

            # note_type = data.get("note_type")
            time_string = data.get("time_string")
            # audio = request.files.get("audio")
            text = data.get("text")
            pool_id = data.get("pool_id")

            # if not note_type in ["audio","text"]:
            #     return create_response(0,"Invalid note type")

            if not text:
                return create_response(0,"Please provide text for note")
            # if not time_string:
            #     return create_response(0,"Please provide date and time")
            if not pool_id:
                return create_response(0,"Invalid data")

            get_pool_data = PlayerPool.query.filter_by(id = pool_id,is_deleted = False).first()
            if not get_pool_data:
                return create_response(0,"Invalid data")

            # if audio:
            #     if text:
            #         return create_response(0,"You cannot be add voice note and text same time")
            #     file_path, picture = upload_audio_local(audio)
            # else:
            #     file_path = None
            #     picture = None

            add_notes = PlayerPoolNotes(time_string =time_string,
                                        text=text,pool_id=pool_id,created_time=datetime.utcnow(),user_id=active_user.id)

            db.session.add(add_notes)
            db.session.commit()

            return create_response(1,"Note created successfully")

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

class GetPlayerPoolNotesResource(Resource):
    @token_required
    def post(self,active_user):
        try:
            data = request.get_json() or {}

            page = int(data.get('page', 1))
            per_page = 10

            pool_id = data.get("pool_id")

            if not pool_id:
                return create_response(0,"Invalid data")

            get_pool_data = PlayerPool.query.filter_by(id = pool_id,is_deleted = False).first()
            if not get_pool_data:
                return create_response(0,"Invalid data")

            get_notes = PlayerPoolNotes.query.filter(PlayerPoolNotes.pool_id==pool_id).order_by(
                PlayerPoolNotes.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

            get_notes_list = [ i.as_dict() for i in get_notes.items ]

            has_next = get_notes.has_next
            total_pages = get_notes.pages

            # Pagination information
            pagination_info = {
            "current_page": page,
            "has_next": has_next,
            "per_page": per_page,
            "total_pages": total_pages,
        }

            return create_response(1,"Success",get_notes_list,pagination_info)

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

    @token_required
    def delete(self, active_user):
        try:
            data = request.get_json() or {}

            pool_id = data.get("pool_id")
            note_id = data.get("note_id")

            if not pool_id:
                return create_response(0, "Invalid data")
            if not note_id:
                return create_response(0, "Please select note first")

            get_pool_data = PlayerPool.query.filter_by(id=pool_id, is_deleted=False).first()
            if not get_pool_data:
                return create_response(0, "Invalid data")

            get_note_data = PlayerPoolNotes.query.filter(PlayerPoolNotes.pool_id == pool_id,PlayerPoolNotes.id == note_id).first()

            if not get_note_data:
                return create_response(0, "Invalid note data")

            if get_note_data.audio_name is not None:
                delete_audio_local(get_note_data.audio_name)

            db.session.delete(get_note_data)
            db.session.commit()

            return create_response(1, "Note deleted successfully")

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

