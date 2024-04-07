import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    task_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tag_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tags.id"))
    status = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    user = orm.relationship("User")

    tag = orm.relationship("Tags", back_populates="tasks")

