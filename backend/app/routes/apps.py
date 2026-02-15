from ..models import AppService
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("apps", AppService)
