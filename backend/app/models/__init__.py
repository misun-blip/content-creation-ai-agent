# Models package
# backend/app/models/__init__.py
# 确保所有模型都被导入，SQLAlchemy 才能正确建表和处理关联
from app.models.user import User        # noqa: F401
from app.models.record import Record, Version  # noqa: F401
from app.models.material import Material  # noqa: F401
from app.models.tag import Tag, material_tags  # noqa: F401