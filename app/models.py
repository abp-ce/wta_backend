from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


association_table = Table(
    "association_table",
    Base.metadata,
    Column("theme_id", ForeignKey("theme.id"), primary_key=True),
    Column("task_no", ForeignKey("task.no"), primary_key=True),
)


class Theme(Base):
    __tablename__ = "theme"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)
    tasks = relationship(
        "Task", secondary=association_table, back_populates="themes"
    )


class Task(Base):
    __tablename__ = "task"
    no = Column(String(30), primary_key=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=True)
    solved = Column(Integer, default=0)
    themes = relationship(
        "Theme", secondary=association_table, back_populates="tasks"
    )
