# models.py
from sqlalchemy import Column, Integer, String, Float, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Plant(Base):
    __tablename__ = 'plants'

    # Basic Information
    id = Column(Integer, primary_key=True)
    common_name = Column(String, nullable=False)
    scientific_name = Column(String, nullable=False)
    other_name = Column(JSON)  #  alternate names
    family = Column(String)
    origin = Column(String)

    # Images
    default_image = Column(JSON)  # 

    # Characteristics
    cycle = Column(String)  # life cycle (e.g., annual, perennial)
    watering = Column(String)  # watering needs (e.g., frequent)
    sunlight = Column(String)  # sunlight requirements (e.g., full sun, partial shade)
    growth_rate = Column(String)  # growth speed (e.g., slow, fast)
    dimensions = Column(JSON)  # contains data like height and spread
    toxicity = Column(String)  # toxicity details (if applicable)
    attractants = Column(JSON)  # animals/insects attracted (e.g., butterflies)

    # Care
    care_instructions = Column(JSON)

    # Additional Attributes
    soil = Column(String)  # soil preferences
    propagation_methods = Column(JSON)  # propagation details (e.g., cuttings, seeds)
    common_issues = Column(JSON)  #  common diseases or pests
    pruning = Column(String)  # pruning requirements

    def __repr__(self):
        return f"<Plant(id={self.id}, common_name='{self.common_name}', scientific_name='{self.scientific_name}')>"

DATABASE_URL = 'sqlite:///plants.db'  # change for production Snowflake usage
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
