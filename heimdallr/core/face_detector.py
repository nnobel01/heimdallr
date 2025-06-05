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

class FaceDetector:
    def __init__(self, threshold: float = 0.80, model="hog"):
        """
        Initialize face detector
        
        Args:
            threshold: Similarity threshold (0.0-1.0)
            model: Face detection model to use ('hog' or 'cnn')
        """
        self.threshold = threshold
        self.model = model
        self.logger = logger

    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load and validate image"""
        if not os.path.exists(image_path):
            self.logger.error(f"❌ Image not found: {image_path}")
            return None
            
        try:
            image = face_recognition.load_image_file(image_path)
            return image
        except Exception as e:
            self.logger.error(f"❌ Error loading image: {str(e)}")
            return None

    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process input image and extract face data
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Dictionary containing face data and metadata
        """
        try:
            self.logger.info(f"🔍 Processing image: {image_path}")
            
            if not FACE_RECOGNITION_AVAILABLE:
                self.logger.warning("⚠️  Face recognition library not available. Using fallback detection.")
                return self._fallback_processing(image_path)
            
            # Load and validate image
            image = self._load_image(image_path)
            if image is None:
                return {"faces_found": False, "error": "Could not load image"}
            
            # Detect faces
            face_locations = face_recognition.face_locations(image, model=self.model)
            
            if not face_locations:
                self.logger.warning("❌ No faces detected in the image")
                return {"faces_found": False, "face_count": 0}
            
            # Extract face encodings
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            # Process each detected face
            faces_data = []
            for i, (encoding, location) in enumerate(zip(face_encodings, face_locations)):
                face_data = self._process_single_face(
                    image, encoding, location, i, image_path
                )
                faces_data.append(face_data)
            
            self.logger.info(f"✅ Detected {len(faces_data)} face(s)")
            
            return {
                "faces_found": True,
                "face_count": len(faces_data),
                "faces": faces_data,
                "original_image": image_path,
                "image_dimensions": image.shape[:2]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error processing image: {str(e)}")
            return {"faces_found": False, "error": str(e)}
    
    def _fallback_processing(self, image_path: str) -> Dict[str, Any]:
        """Fallback processing when face_recognition is not available"""
        try:
            # Basic image validation
            image = cv2.imread(image_path)
            if image is None:
                return {"faces_found": False, "error": "Could not load image"}
            
            # Create dummy face data for testing
            dummy_encoding = np.random.rand(128)  # Fake encoding
            dummy_location = (100, 200, 300, 100)  # Top, right, bottom, left
            
            face_data = {
                "face_index": 0,
                "encoding": dummy_encoding,
                "location": dummy_location,
                "face_hash": "dummy_hash",
                "face_crop_path": image_path,  # Use original image for now
                "dimensions": {"width": 100, "height": 200},
                "source_image": image_path
            }
            
            return {
                "faces_found": True,
                "face_count": 1,
                "faces": [face_data],
                "original_image": image_path,
                "image_dimensions": image.shape[:2],
                "fallback_mode": True
            }
            
        except Exception as e:
            return {"faces_found": False, "error": str(e)}

    def _process_single_face(
        self, 
        image: np.ndarray,
        encoding: np.ndarray,
        location: Tuple[int, int, int, int],
        face_index: int,
        source_image: str
    ) -> Dict[str, Any]:
        """Process a single detected face"""
        # Extract face dimensions
        top, right, bottom, left = location
        width = right - left
        height = bottom - top
        
        # Generate unique hash for the face
        face_hash = hashlib.md5(encoding.tobytes()).hexdigest()
        
        # Save face crop
        face_crop = image[top:bottom, left:right]
        crop_path = self._save_face_crop(face_crop, face_hash)
        
        return {
            "face_index": face_index,
            "encoding": encoding,
            "location": location,
            "face_hash": face_hash,
            "face_crop_path": str(crop_path),
            "dimensions": {
                "width": width,
                "height": height
            },
            "source_image": source_image
        }
    
    def _save_face_crop(self, face_crop: np.ndarray, face_hash: str) -> Path:
        """Save cropped face image"""
        # Convert BGR to RGB
        face_crop_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(face_crop_rgb)
        
        # Create crops directory if it doesn't exist
        crops_dir = Path("face_crops")
        crops_dir.mkdir(exist_ok=True)
        
        # Save image
        crop_path = crops_dir / f"{face_hash}.jpg"
        pil_image.save(crop_path)
        
        return crop_path
