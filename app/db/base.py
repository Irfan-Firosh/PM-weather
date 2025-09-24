from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Make sure Base is available for import
__all__ = ['Base']