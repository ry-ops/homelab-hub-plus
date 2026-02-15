from ..models import Storage
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("storage", Storage)
