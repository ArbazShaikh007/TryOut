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
from base.common.utils import create_response
    # push_notification,upload_photos_local,upload_photos,user_send_reset_email
from base.apis.v1.user.models import User,token_required
from base.apis.v1.admin.models import PlayerPool,Athletes,Teams

class GetPlayerPoolResource(Resource):
    @token_required
    def get(self,active_user):
        try:

            get_my_player_pools = PlayerPool.query.filter_by(is_deleted = False,user_id = active_user.id).all()

            my_player_pools_list = [ i.as_dict() for i in get_my_player_pools ]

            return jsonify({ 'status': 1, 'message': 'Success','data': my_player_pools_list })

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

class GetPlayerPoolAthletesResource(Resource):
    @token_required
    def post(self,active_user):
        try:
            data = request.get_json() or {}

            pool_id = data.get("pool_id")

            if not pool_id:
                return jsonify({'status': 0,'message': "Please select player pool first"})

            get_pool_data = PlayerPool.query.filter_by(id=pool_id, is_deleted=False).first()
            if not get_pool_data:
                return jsonify({'status': 0, 'message': 'Invalid data'})

            get_player_pool_athletes = Athletes.query.filter_by(is_deleted = False,user_id = active_user.id,pool_id = pool_id).all()

            player_pools_athletes_list = [ i.as_dict() for i in get_player_pool_athletes ]

            return jsonify({ 'status': 1, 'message': 'Success','data': player_pools_athletes_list })

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

class GivePlayerPoolAthletePositionResource(Resource):
    @token_required
    def post(self,active_user):
        try:
            data = request.get_json() or {}

            position = data.get("position")
            level = data.get("level")
            status = data.get("status")
            pool_id = data.get("pool_id")
            athlete_id = data.get("athlete_id")

            if not pool_id:
                return jsonify({'status': 0,'message': "Please select player pool first"})
            if not athlete_id:
                return jsonify({'status': 0,'message': "Please select athlete first"})
            if not position and not level and not status:
                return jsonify({'status': 0,'message': "You not select anything"})

            get_pool_data = PlayerPool.query.filter_by(id=pool_id, is_deleted=False).first()
            if not get_pool_data:
                return jsonify({'status': 0, 'message': 'Invalid data'})

            get_athlete_data = Athletes.query.filter_by(id=athlete_id,pool_id=pool_id, is_deleted=False).first()
            if not get_athlete_data:
                return jsonify({'status': 0, 'message': 'Invalid athlete data'})

            if position:
                get_athlete_data.position = position

            if level:
                get_athlete_data.level = level

            if status:
                if status == "Accepted":
                    get_athlete_data.accepted_time = datetime.utcnow()

                get_athlete_data.status = status

            else:
                get_athlete_data.status = "Assigned"

            db.session.commit()

            return jsonify({ 'status': 1, 'message': 'Success' })

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

class GroundPositionPlayerPoolResource(Resource):
    @token_required
    def post(self, active_user):
        try:
            data = request.get_json() or {}
            pool_id = data.get("pool_id")

            if not pool_id:
                return jsonify({'status': 0, 'message': "Please select player pool first"})

            get_pool_data = PlayerPool.query.filter_by(id=pool_id, is_deleted=False).first()
            if not get_pool_data:
                return jsonify({'status': 0, 'message': 'Invalid data'})

            # --- do not change this query ---
            get_athlete_data = Athletes.query.filter(
                Athletes.position != None,
                Athletes.pool_id == pool_id,
                Athletes.is_deleted == False,
                Athletes.status != "Declined"
            ).all()

            # fixed order of positions
            positions = [
                "GK", "RD", "LD", "CD", "CDM",
                "RSF", "CM", "S", "CAM", "LSF"
            ]

            # prepare response data directly (ordered + default 0|0)
            data_out = [
                {"position": p, "assigned": 0, "accepted": 0, "assigned_accepted": "0 | 0"}
                for p in positions
            ]

            # mapping for quick lookup without extra loop
            index_map = {p: i for i, p in enumerate(positions)}

            # -------- only ONE loop ----------
            for a in get_athlete_data:
                pos = a.position
                if pos not in index_map:
                    continue

                i = index_map[pos]

                # update assigned
                data_out[i]["assigned"] += 1

                # update accepted
                if a.status == "Accepted":
                    data_out[i]["accepted"] += 1

                # update "2 | 1"
                assigned = data_out[i]["assigned"]
                accepted = data_out[i]["accepted"]
                data_out[i]["assigned_accepted"] = f"{assigned} | {accepted}"
            # ---------------------------------

            return jsonify({
                'status': 1,
                'message': 'Success',
                'data': data_out
            })

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

class GetTeamsResource(Resource):
    @token_required
    def get(self,active_user):
        try:

            get_teams_data = Teams.query.filter_by(is_deleted = False,user_id = active_user.id).all()

            teams_list = [ i.as_dict() for i in get_teams_data ]

            return jsonify({ 'status': 1, 'message': 'Success','data': teams_list,'recent_notes': [], 'athlete_activity': [] })

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500

class GetTeamsAthletesResource(Resource):
    @token_required
    def post(self,active_user):
        try:
            data = request.get_json() or {}

            page = int(data.get('page', 1))
            per_page = 10

            team_id = data.get("team_id")

            if not team_id:
                return create_response(0,"Please select team first")

            get_teams_data = Teams.query.filter_by(is_deleted = False,user_id = active_user.id,id = team_id).first()
            if not get_teams_data:
                return create_response(0,"Invalid team data")

            get_athletes = Athletes.query.filter(Athletes.is_deleted == False,Athletes.team_id == team_id,Athletes.user_id == active_user.id).order_by(
                Athletes.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

            athletes_list = [ i.as_dict() for i in get_athletes.items ]

            return jsonify({ 'status': 1, 'message': 'Success','data': athletes_list,"formation": get_teams_data.formation })

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': str(e)}, 500
