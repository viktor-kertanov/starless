from sqlalchemy import Column, ForeignKey, Integer, Float, String, Boolean, DateTime, Interval, func
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
    release_year = Column(Integer, nullable=True, unique=False)
    release_date = Column(DateTime, nullable=True, unique=False)
    in_num_charts = Column(Integer, nullable=True, unique=False)
    total_ranking = Column(Integer, nullable=True, unique=False)
    album_art_url = Column(String(128), unique=False, nullable=True)
    release_url = Column(String, unique=False, nullable=True)
    num_ratings = Column(Integer, unique=False, nullable=True)
    top_percentile = Column(Float, unique=False, nullable=True)
    bayes_avg_rating = Column(Float, unique=False, nullable=True)
    mean_avg_rating = Column(Float, unique=False, nullable=True)
    std_rating = Column(Float, unique=False, nullable=True)
    num_favourites = Column(Integer, unique=False, nullable=True)
    
    def __repr__(self):
        return f"Release: {self.release_metadata}"


class ChartRelease(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'chart_release'
    release_id = Column(UUID(as_uuid=True), ForeignKey(Release.id), unique=False, nullable=False)
    chart_id = Column(UUID(as_uuid=True), ForeignKey(MusicChart.id), unique=False, nullable=False)
    position = Column(Integer, nullable=True, unique=False)
    release = relationship('Release', backref='chart_releases')
    chart  = relationship('MusicChart', backref='chart_releases')


class Track(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'tracks'
    release_id = Column(UUID(as_uuid=True), ForeignKey(Release.id), unique=False, nullable=False)
    track_title = Column(String, unique=False, nullable=False)
    idx_in_release = Column(Integer, unique=False, nullable=False)
    track_duration = Column(Interval, unique=False, nullable=True)
    user_avg_rating = Column(Float, unique=False, nullable=True)
    user_num_votes = Column(Integer, unique=False, nullable=True)

    release = relationship('Release', backref='tracks')

    def __repr__(self):
        return f"Track # {self.idx_in_release}: {self.track_title}. Duration: {self.track_duration}"


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)