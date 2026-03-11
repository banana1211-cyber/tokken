"""
SQLAlchemyモデル定義 - 仕様書準拠の6テーブル
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


def new_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=new_uuid)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum("admin", "attorney", "client", name="user_role"), nullable=False, default="client")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    projects = relationship("Project", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=new_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    github_repo_url = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    status = Column(Enum("draft", "in_review", "submitted", "completed", name="project_status"), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    patent_drafts = relationship("PatentDraft", back_populates="project")
    hearing_sheets = relationship("HearingSheet", back_populates="project")
    files = relationship("File", back_populates="project")


class PatentDraft(Base):
    __tablename__ = "patent_drafts"

    id = Column(String, primary_key=True, default=new_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    generated_by = Column(Enum("ai", "manual", name="generated_by"), default="ai")
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="patent_drafts")
    comments = relationship("Comment", back_populates="draft")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=new_uuid)
    draft_id = Column(String, ForeignKey("patent_drafts.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    parent_comment_id = Column(String, ForeignKey("comments.id"), nullable=True)
    text = Column(Text, nullable=False)
    selected_text = Column(Text, nullable=True)
    selection_start = Column(Integer, default=0)
    selection_end = Column(Integer, default=0)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    draft = relationship("PatentDraft", back_populates="comments")
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", foreign_keys=[parent_comment_id])


class HearingSheet(Base):
    __tablename__ = "hearing_sheets"

    id = Column(String, primary_key=True, default=new_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    patent_name = Column(String, nullable=True)
    problem_to_solve = Column(Text, nullable=True)
    existing_tech_problems = Column(Text, nullable=True)
    composition = Column(Text, nullable=True)
    features = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="hearing_sheets")


class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=new_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    type = Column(Enum("reference", "drawing", name="file_type"), default="reference")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="files")
