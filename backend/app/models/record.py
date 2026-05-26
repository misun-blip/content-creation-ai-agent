from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Record(Base):
    __tablename__ = "records"
    __table_args__ = (
        Index("ix_records_user_id_created_at", "user_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)   # douyin / xiaohongshu / wechat / bilibili
    content = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="draft", index=True)  # draft / published / archived
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关联
    user = relationship("User", back_populates="records")
    versions = relationship("Version", back_populates="record", cascade="all, delete-orphan", order_by="Version.version_number")


class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("records.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)   # 1, 2, 3 ...
    content = Column(Text, nullable=False)
    change_note = Column(String(500), nullable=True)              # 本次版本的修改说明
    is_ai_generated = Column(Boolean, nullable=False, default=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    record = relationship("Record", back_populates="versions")