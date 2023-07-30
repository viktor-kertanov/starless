from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Interval, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from database.db_config import Base, engine
import uuid


class UUIDPrimaryKeyMixin:
    @declared_attr
    def id(cls):
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    @declared_attr
    def created(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def modified(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class MusicChart(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'music_charts'
    chart_name = Column(String(256), unique=False, nullable=False)
    chart_by = Column(String(128), unique=False, nullable=True)
    chart_description = Column(String, unique=False, nullable=True)
    chart_url = Column(String(256), unique=True, nullable=False)
    chart_contents_url = Column(String(256), unique=True, nullable=True)
    chart_external_urls = Column(String, unique=False, nullable=True)
    chart_year = Column(Integer, nullable=True, unique=False)
    source_recognised = Column(Boolean, unique=False, nullable=True)

    def __repr__(self):
        return f"{self.chart_name} by {self.chart_by}"


class Release(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'music_releases'
    release_metadata = Column(String, unique=True, nullable=False)
    release_artist = Column(String, unique=False, nullable=False)
    release_title = Column(String, unique=False, nullable=False)
    release_country = Column(String(128), unique=False, nullable=True)
    release_year = Column(Integer, nullable=True, unique=False)
    appears_in_num_charts = Column(Integer, nullable=True, unique=False)
    release_duration = Column(Interval, nullable=True, unique=False)
    album_art_url = Column(String(128), unique=False, nullable=True)
    release_isrc = Column(String(128), unique=True, nullable=True)
    release_url = Column(String, unique=False, nullable=True)
    risky_metadata = Column(Boolean, unique=False, nullable=True)

    def __repr__(self):
        return f"Release: {self.release_metadata}"


class ReleaseChart(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'release_music_chart'
    release_id = Column(String, unique=False, nullable=False)
    chart_id = Column(String, unique=False, nullable=False)
    position = Column(Integer, nullable=True, unique=False)

    def __repr__(self):
        return f"Release id: {self.release_id} in chart [{self.chart_id}], position # {self.position}"


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)