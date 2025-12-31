# app/universe/loader.py

from .lq45 import LQ45
from .idx30 import IDX30
from .kompas100 import KOMPAS100
from .konglo import KONGLO


UNIVERSE_MAP = {
    "LQ45": LQ45,
    "IDX30": IDX30,
    "Kompas100": KOMPAS100,
    "Konglo": KONGLO,
}



def load_universe(name: str) -> list[str]:
    if name not in UNIVERSE_MAP:
        raise ValueError(f"Universe '{name}' tidak dikenal")

    return UNIVERSE_MAP[name]
