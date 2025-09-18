"""Kiểm tra nhập khẩu nhanh cho các mô-đun Phase2."""
import sys
try:
    import core.face_recognizer as fr
    import core.face_database as db
    import utils.drawing_utils as draw
    import utils.metrics as metrics
except Exception as e:
    print('IMPORT_FAILED', e)
    raise
else:
    print('DONE')
