from flask_restful import Api

# Admin Auth

from base.apis.v1.admin.auth import AdminRegisterResource,AdminLoginResource

# Admin Create

from base.apis.v1.admin.create import AddUserResource,CreatePlayerPoolResource,CreateAthleteResource,CreateTeamsResource

# User View

from base.apis.v1.user.view import GetTeamsAthletesResource,GetTeamsResource,GroundPositionPlayerPoolResource,GetPlayerPoolResource,GetPlayerPoolAthletesResource,GivePlayerPoolAthletePositionResource

# User Create

from base.apis.v1.user.create import CreatePlayerPoolNotesResource,GetPlayerPoolNotesResource

# User Auth

from base.apis.v1.user.auth import UserLoginResource

api = Api()

admin_base = '/admin/'

#Admin Auth

api.add_resource(AdminRegisterResource, admin_base+"register")
api.add_resource(AdminLoginResource, admin_base+"login")

# Admin Create

api.add_resource(AddUserResource, admin_base+"add_user")
api.add_resource(CreatePlayerPoolResource, admin_base+"create_player_pool")
api.add_resource(CreateAthleteResource, admin_base+"create_athlete")
api.add_resource(CreateTeamsResource, admin_base+"create_teams")

user_base = '/user/'

# User Auth

api.add_resource(UserLoginResource, user_base+"login")

# User View

api.add_resource(GetPlayerPoolResource, user_base+"get_player_pools")
api.add_resource(GetPlayerPoolAthletesResource, user_base+"player_pool_athletes")
api.add_resource(GivePlayerPoolAthletePositionResource, user_base+"assign_athlete_data")
api.add_resource(GroundPositionPlayerPoolResource, user_base+"ground_position")
api.add_resource(GetTeamsResource, user_base+"get_teams_data")
api.add_resource(GetTeamsAthletesResource, user_base+"get_team_athletes")

# User Create

api.add_resource(CreatePlayerPoolNotesResource, user_base+"create_pool_notes")
api.add_resource(GetPlayerPoolNotesResource, user_base+"get_pool_notes")
