# from datetime import datetime
# from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
# from sqlalchemy.orm import declarative_base, relationship

# Base = declarative_base()

# class User(Base):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True)
#     username = Column(String, unique=True, nullable=False)
#     path = relationship('UserPath', uselist=False, back_populates='user')


# class UserPath(Base):
#     __tablename__ = 'user_paths'

#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'), unique=True)
#     base_path = Column(String, nullable=False)
#     updated_at = Column(DateTime, default=datetime.utcnow)
#     user = relationship('User', back_populates='path')


# class DocumentRecord(Base):
#     __tablename__ = 'documents'

#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     relative_path = Column(String)
#     filename = Column(String)
#     classified = Column(Boolean, default=False)
#     verified = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
