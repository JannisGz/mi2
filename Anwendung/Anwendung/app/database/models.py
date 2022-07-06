from Anwendung.app.extensions import ma
class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose, add more if needed. deleted role_id
        fields = ("email", "name", "username", "joined_date")
