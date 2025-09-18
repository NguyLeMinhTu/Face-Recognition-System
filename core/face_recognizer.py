from typing import List, Optional, Dict
from pathlib import Path
import numpy as np

'''
Tác dụng: Wrapper đơn giản xung quanh mô hình nhận diện khuôn mặt InsightFace.
Sử dụng FaceAnalysis để phát hiện khuôn mặt, trích xuất embedding và các thuộc tính khác.

Cung cấp phương thức analyze_bgr để phân tích hình ảnh BGR và trả về danh sách khuôn mặt với bounding box, điểm mốc, embedding và các thuộc tính khác.
'''
FaceAnalysis = None
try:
    # newer insightface exposes FaceAnalysis in the app submodule
    from insightface.app import FaceAnalysis as _FaceAnalysis
    FaceAnalysis = _FaceAnalysis
except Exception:
    try:
        # fallback: some installs may expose FaceAnalysis at package root
        from insightface import FaceAnalysis as _FaceAnalysis
        FaceAnalysis = _FaceAnalysis
    except Exception:
        FaceAnalysis = None


class FaceRecognizer:
    def __init__(self, model_name: str = 'buffalo_s', device: str = 'cpu', local_path: Optional[str] = None):
        self.model_name = model_name
        self.device = device
        self.local_path = local_path
        self.analyzer = None
        if FaceAnalysis is None:
            raise RuntimeError('insightface is not available in this environment')
        # instantiate FaceAnalysis, pass normalized local model root if available
        if self.local_path:
            # Resolve the provided path to an absolute Path for reliable part inspection
            p = Path(self.local_path).resolve()
            parts = [part.lower() for part in p.parts]
            # look for the first occurrence of the sequence ['models', <model_name>]
            seq = ['models', self.model_name.lower()]
            root_path = p
            try:
                for i in range(len(parts) - 1):
                    if parts[i:i+2] == seq:
                        # root should be the path before the 'models' segment
                        root_path = Path(*p.parts[:i]) if i > 0 else Path(p.anchor or '.')
                        break
            except Exception:
                root_path = p

            root = str(root_path)
            # defensive: if root ends up empty, fallback to provided path
            if not root:
                root = str(p)
            try:
                # instantiate FaceAnalysis with normalized root
                self.analyzer = FaceAnalysis(name=self.model_name, root=root)
            except Exception:
                # fallback: try original provided path
                try:
                    self.analyzer = FaceAnalysis(name=self.model_name, root=str(self.local_path))
                except Exception:
                    # last resort: no root passed
                    self.analyzer = FaceAnalysis(name=self.model_name)
        else:
            self.analyzer = FaceAnalysis(name=self.model_name)
        # prepare models for CPU (ctx_id=-1)
        self.analyzer.prepare(ctx_id=-1)

    def analyze_bgr(self, bgr_image: np.ndarray) -> List[Dict]:
        faces = self.analyzer.get(bgr_image)
        out = []
        for f in faces:
            item = {
                'bbox': [float(x) for x in getattr(f, 'bbox', [])],
                'score': float(getattr(f, 'det_score', getattr(f, 'score', 0.0)))
            }
            kps = getattr(f, 'kps', None)
            if kps is not None:
                item['landmarks'] = [[float(x), float(y)] for (x, y) in kps]
            emb = getattr(f, 'embedding', None)
            if emb is not None:
                item['embedding'] = emb.tolist()
            # gender/age (if models provide them)
            gender = getattr(f, 'gender', None)
            age = getattr(f, 'age', None)
            if gender is not None:
                # insightface uses 1 for male, 0 for female in some models
                try:
                    item['gender'] = 'M' if int(gender) == 1 else 'F'
                except Exception:
                    item['gender'] = gender
            if age is not None:
                try:
                    item['age'] = int(age)
                except Exception:
                    item['age'] = age
            # placeholders for attributes that need dedicated models
            item['race'] = None
            item['emotion'] = None
            out.append(item)
        return out
