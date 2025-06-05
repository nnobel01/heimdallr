import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional, Tuple
import os
import hashlib
from pathlib import Path

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

from ..utils.logger import get_logger

logger = get_logger()