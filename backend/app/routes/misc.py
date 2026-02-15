from ..models import Misc
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("misc", Misc)
