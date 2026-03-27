from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)  # 可选，未登录或历史数据为空
    type = Column(String(20), nullable=False, default="template")  # template / image / video
    title = Column(String(255), nullable=False)
    # 经过迁移后，materials 表已经将 content 重命名为 description
    description = Column(Text, nullable=False)
    # 新表结构中增加的字段：category/preview/upload_date
    category = Column(String(50), nullable=False, default="default")
    preview = Column(String(1000), nullable=False, default="")
    file_path = Column(String(500), nullable=True)  # 文件存储路径
    upload_date = Column(Date, nullable=True)

    # 多对多：素材-标签（关联表在 app.models.tag 中定义为 material_tags）
    tags = relationship(
        "Tag",
        secondary="material_tags",
        back_populates="materials",
    )