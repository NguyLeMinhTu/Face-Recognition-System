'''
Tác dụng: Các hàm tiện ích để quản lý cơ sở dữ liệu khuôn mặt đơn giản dựa trên file, 
lưu trữ embeddings dưới dạng .npy và metadata trong JSON.
'''

from pathlib import Path
import json
import numpy as np
from typing import Optional, Tuple, List


class FaceDatabase:
    """ 
    Cơ sở dữ liệu khuôn mặt đơn giản dựa trên file.
    Lưu trữ embeddings dưới dạng .npy và metadata trong JSON index file.
    """

    def __init__(self, db_dir: str = 'data/known_faces'):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.db_dir / 'index.json'
        if not self.index_file.exists():
            self._write_index({})

    def _read_index(self) -> dict:
        return json.loads(self.index_file.read_text())

    def _write_index(self, data: dict):
        self.index_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def add(self, person_id: str, embedding: np.ndarray) -> None:
        idx = self._read_index()
        emb_path = self.db_dir / f"{person_id}.npy"
        np.save(str(emb_path), embedding)
        idx[person_id] = str(emb_path.name)
        self._write_index(idx)

    def list_ids(self) -> List[str]:
        return list(self._read_index().keys())

    def get_embedding(self, person_id: str) -> Optional[np.ndarray]:
        idx = self._read_index()
        if person_id not in idx:
            return None
        path = self.db_dir / idx[person_id]
        if not path.exists():
            return None
        return np.load(str(path))

    def find_best(self, embedding: np.ndarray) -> Optional[Tuple[str, float]]:
        # simple cosine similarity search
        idx = self._read_index()
        best_id = None
        best_score = -1.0
        for pid, fname in idx.items():
            path = self.db_dir / fname
            if not path.exists():
                continue
            other = np.load(str(path))
            # cosine similarity
            a = embedding
            b = other
            denom = (np.linalg.norm(a) * np.linalg.norm(b))
            if denom == 0:
                score = 0.0
            else:
                score = float(np.dot(a, b) / denom)
            if score > best_score:
                best_score = score
                best_id = pid
        if best_id is None:
            return None
        return best_id, best_score
