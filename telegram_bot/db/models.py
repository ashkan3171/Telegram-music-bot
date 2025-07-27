from tortoise import  fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(primary_key=True)
    user_id = fields.IntField(unique=True)
    chat_id = fields.IntField(unique=True)
    first_name = fields.CharField(max_length=50, null=True)
    username = fields.CharField(max_length=255, null=True)
    chat_type = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta: 
        table = "users"  #Table's name

class Music(Model):
    id = fields.IntField(primary_key=True)
    music_id = fields.CharField(max_length=100, unique=True) 
    file_id = fields.CharField(max_length=255, null=True) 
    title = fields.CharField(max_length=255)
    duration = fields.IntField()
    youtube_url = fields.CharField(max_length=255)
    uploader = fields.CharField(max_length=255, null=True)
    audio_file = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = 'musics'


class Playlist(Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField('models.User', related_name='playlists')
    music = fields.ForeignKeyField('models.Music', related_name='playlists')
    added_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "playlist"
        unique_together = ('user', 'music')

class SearchLog(Model):
    id = fields.IntField(primary_key=True)
    query = fields.CharField(max_length=255)     
    results = fields.JSONField()                 
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "search_logs"