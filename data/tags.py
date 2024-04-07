import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm


class Tags(SqlAlchemyBase):
    __tablename__ = 'tags'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    tag_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    emoji = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    # Existing relationship with User
    user = orm.relationship("User")

    # Establish the bidirectional relationship on the Tags side
    tasks = orm.relationship("Task", back_populates="tag")

