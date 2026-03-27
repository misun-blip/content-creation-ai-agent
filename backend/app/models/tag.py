from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy import func
from sqlalchemy.orm import relationship
from app.core.database import Base


# 素材-标签多对多关联表
material_tags = Table(
    "material_tags",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("material_id", Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("material_id", "tag_id", name="uk_material_tag"),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    usage_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联：通过 material_tags 与 Material 多对多
    materials = relationship(
        "Material",
        secondary="material_tags",
        back_populates="tags",
    )
