
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Import explicite de chaque modèle pour garantir leur enregistrement dans Base.metadata
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.db.models.document import Document
from app.db.models.job import Job

