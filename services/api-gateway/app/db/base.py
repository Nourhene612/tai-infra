
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Import explicite de chaque modèle pour garantir leur enregistrement dans Base.metadata
def _safe_import(module_path, symbol=None):
	try:
		if symbol:
			__import__(module_path, fromlist=[symbol])
		else:
			__import__(module_path)
	except Exception as e:
		print(f"[WARN] could not import {module_path}: {e}")

_safe_import('app.db.models.tenant', 'Tenant')
_safe_import('app.db.models.user', 'User')
_safe_import('app.db.models.document', 'Document')
_safe_import('app.db.models.AuthSession', 'AuthSession')
_safe_import('app.db.models.AuthLog', 'AuditLog')
_safe_import('app.db.models.CompanyAsset', 'CompanyAsset')

_safe_import('app.db.models.proposal', 'Proposal')
_safe_import('app.db.models.role', 'Role')
_safe_import('app.db.models.LoginAttempt', 'LoginAttempt')
_safe_import('app.db.models.ComplimeceReport', 'ComplianceReport')


