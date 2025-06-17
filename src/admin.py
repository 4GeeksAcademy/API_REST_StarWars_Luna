import os
from flask_admin import Admin
from models import db, User, Planet, Character, Favorite_Planet, Favorite_Character
from flask_admin.contrib.sqla import ModelView


class UserModelView(ModelView):
    column_auto_select_related = True
    column_list = ['id', 'user', 'first_name', 'last_name',
                   'subscription_date', 'email', 'is_active', 'fav_planet', 'fav_character']

class PlanetModelView(ModelView):  
    column_auto_select_related = True
    column_list = ['id', 'name', 'weather', 'native_characters', 'favorite']

class CharacterModelView(ModelView):  
    column_auto_select_related = True
    column_list = ['id', 'name', 'species',
                   'planet_origin', 'native_of', 'favorites']
    
class FavoritePlanetsModelView(ModelView):  
    column_auto_select_related = True
    column_list = ['id', 'user_id', 'planet_id',
                   'favorite_planet_by', 'planet_inf']

class FavoriteCharactersModelView(ModelView):  
    column_auto_select_related = True
    column_list = ['id', 'user_id', 'character_id',
                   'favorite_character_by', 'character_inf']


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(PlanetModelView(Planet, db.session))
    admin.add_view(CharacterModelView(Character, db.session))
    admin.add_view(FavoritePlanetsModelView(Favorite_Planet, db.session))
    admin.add_view(FavoriteCharactersModelView(Favorite_Character, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))
