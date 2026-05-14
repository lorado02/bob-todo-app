from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# Create SQLite database engine
engine = create_engine('sqlite:///database.db', echo=True)

# Create a scoped session
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

# Create base class for declarative models
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Initialize the database by creating all tables."""
    # Import all modules here that might define models so that
    # they will be registered properly on the metadata
    import models
    Base.metadata.create_all(bind=engine)


def shutdown_session(exception=None):
    """Remove database session at the end of the request or when the application shuts down."""
    db_session.remove()

# Made with Bob
