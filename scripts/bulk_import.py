import os
import sys
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BASE_DIR.as_posix())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supernovae.settings")

django.setup()

# Data migration logic