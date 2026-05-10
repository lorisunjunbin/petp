import logging

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil
from utils.OSUtils import OSUtils


class OCRProcessor(Processor):
    TPL: str = '{"image_path":"", "image_path_key":"", "lang":"ch", "backend":"auto", "preprocess":"none", "filter_func":"return True", "result_key":"ocr_result", "text_key":"ocr_text"}'
    DESC: str = '''
        Extract text from an image using local OCR (no API key required).
        Supports Chinese, English, and many other languages.

        Available backends:
        - paddleocr  Best for Windows/Linux x86_64. pip install paddlepaddle paddleocr
        - rapidocr   PaddleOCR ONNX port. Lightweight, no PyTorch, cross-platform.
                     Recommended default for ARM. pip install rapidocr-onnxruntime
        - easyocr    Best accuracy on low-quality images, handwriting, complex backgrounds.
                     Supports MPS (Metal GPU) on Apple Silicon. Larger download (~500MB).
                     pip install easyocr

        backend="auto" selects by OS + CPU:
        - win32  + x86_64/amd64  ->  paddleocr
        - linux  + x86_64        ->  paddleocr
        - linux  + arm64         ->  rapidocr
        - darwin + arm64 (Apple Silicon M1/M2/M3)  ->  rapidocr
        - darwin + x86_64 (Intel Mac)              ->  paddleocr
        Note: easyocr is never selected automatically; set backend="easyocr" to use it explicitly.

        Available preprocess modes (applied before OCR, requires Pillow + numpy):
        - none       No preprocessing (default)
        - grayscale  Convert to grayscale only
        - binarize   Otsu global binarization; best for printed text on clean uniform background
        - denoise    Median filter + gentle Gaussian; good for scanned documents with noise
        - sharpen    Contrast stretch (2–98 percentile) + strong unsharp mask; good for blurry images
        - upscale    3x upscale + sharpen; good for small/low-resolution images
        - adaptive   Local adaptive binarization; best for uneven lighting, shadows, photos of documents
        - auto       Contrast stretch + denoise + sharpen; general-purpose enhancement
        pip install Pillow numpy (numpy also needed by most OCR backends)

        - image_path: path to the image file (supports expression)
        - image_path_key: key of data_chain to get the image path; takes priority over image_path if set
        - lang: OCR language code, e.g. "ch" (Chinese+English), "en" (English only) (default: "ch")
        - backend: OCR backend to use: "auto", "paddleocr", "rapidocr", "easyocr" (default: "auto")
        - preprocess: image preprocessing mode before OCR (default: "none")
          none      - no preprocessing; use when image quality is already good
          grayscale - convert to grayscale only; use when colour causes false detections
          binarize  - Otsu global binarization (optimal threshold); use for printed text on clean,
                      uniform-background documents (receipts, typed documents)
          denoise   - median filter + gentle Gaussian; use for scanned documents or images with
                      salt-and-pepper noise
          sharpen   - histogram contrast stretch (2–98 percentile) + unsharp mask; use for blurry,
                      low-contrast, or faded images
          upscale   - 3× upscale + sharpen; use for small thumbnails or very low-resolution images
                      where characters are too small for the OCR engine
          adaptive  - local adaptive binarization (per-region threshold); use for photos of documents
                      with uneven lighting, shadows, or curved pages (requires scipy)
          auto      - contrast stretch + denoise + sharpen pipeline; general-purpose enhancement,
                      good starting point when unsure which mode to use
        - filter_func: Python function body to filter OCR lines; receives (line) where line is
          {{"text": str, "confidence": float, "box": list}}; return True to keep, False to discard
          (default: "return True")
        - result_key: key of data_chain to store the full OCR result list (each item has text/confidence/box)
        - text_key: key of data_chain to store the joined plain text string
    '''

    _AUTO_RAPID = {('darwin', 'arm64'), ('linux', 'arm64')}

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        image_path = self.get_data(self.get_param('image_path_key')) if self.has_param('image_path_key') \
            else self.expression2str(self.get_param('image_path'))

        lang = self.explain_param_or_default('lang', 'ch')
        backend = self.explain_param_or_default('backend', 'auto')
        preprocess = self.explain_param_or_default('preprocess', 'none')
        filter_func_body = self.explain_param_or_default('filter_func', 'return True')
        result_key = self.explain_param_or_default('result_key', 'ocr_result')
        text_key = self.explain_param_or_default('text_key', 'ocr_text')

        filter_fn = CodeExplainerUtil.create_and_execute_func(
            'OCRProcessor_filter', '(line, p)', filter_func_body
        )

        resolved = self._resolve_backend(backend)
        logging.debug('Running OCR on: %s (lang=%s, backend=%s, preprocess=%s)', image_path, lang, resolved, preprocess)

        actual_path = self._preprocess_image(image_path, preprocess) if preprocess != 'none' else image_path

        if resolved == 'paddleocr':
            result = self._run_paddleocr(actual_path, lang)
        elif resolved == 'rapidocr':
            result = self._run_rapidocr(actual_path)
        elif resolved == 'easyocr':
            result = self._run_easyocr(actual_path, lang)
        else:
            raise ValueError(f'Unknown OCR backend: {resolved}. Choose from: auto, paddleocr, rapidocr, easyocr')

        result = [line for line in result if filter_fn(line, self)]

        plain_text = '\n'.join(r['text'] for r in result)

        logging.info('OCR complete: %d lines extracted', len(result))
        logging.info('OCR text: %s (preprocess=%s, lang=%s, backend=%s, image=%s)', plain_text, preprocess, lang,
                     resolved, image_path)

        self.populate_data(result_key, result)
        self.populate_data(text_key, plain_text)

    @staticmethod
    def _preprocess_image(image_path: str, mode: str) -> str:
        import os
        import tempfile
        import numpy as np
        from PIL import Image, ImageFilter

        img = Image.open(image_path).convert('RGB')

        if mode == 'grayscale':
            img = img.convert('L')

        elif mode == 'binarize':
            # Otsu's thresholding — finds optimal global threshold by maximising inter-class variance
            gray = np.array(img.convert('L'))
            hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))
            total = gray.size
            sum_all = np.dot(np.arange(256), hist)
            sum_bg, w_bg, max_var, threshold = 0.0, 0.0, 0.0, 0
            for t in range(256):
                w_bg += hist[t]
                if w_bg == 0:
                    continue
                w_fg = total - w_bg
                if w_fg == 0:
                    break
                sum_bg += t * hist[t]
                m_bg = sum_bg / w_bg
                m_fg = (sum_all - sum_bg) / w_fg
                var = w_bg * w_fg * (m_bg - m_fg) ** 2
                if var > max_var:
                    max_var, threshold = var, t
            img = Image.fromarray((gray > threshold).astype(np.uint8) * 255, mode='L')

        elif mode == 'denoise':
            # bilateral-style denoise: reduce noise while preserving edges better than median
            arr = np.array(img.convert('L')).astype(np.float32)
            from PIL import ImageFilter as IF
            img = Image.fromarray(arr.astype(np.uint8), mode='L')
            img = img.filter(IF.MedianFilter(size=3))
            # second pass with gentle gaussian to smooth residual noise
            img = img.filter(IF.GaussianBlur(radius=0.5))

        elif mode == 'sharpen':
            gray = img.convert('L')
            # contrast stretch: expand histogram to full 0-255 range
            arr = np.array(gray).astype(np.float32)
            lo, hi = np.percentile(arr, 2), np.percentile(arr, 98)
            if hi > lo:
                arr = np.clip((arr - lo) / (hi - lo) * 255, 0, 255)
            img = Image.fromarray(arr.astype(np.uint8), mode='L')
            # strong unsharp mask for edge enhancement
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=2))

        elif mode == 'upscale':
            # 3x upscale + sharpen after resize to recover edge definition
            img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
            img = img.convert('L')
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=2))

        elif mode == 'adaptive':
            # adaptive (local) binarization — handles uneven lighting / shadows
            arr = np.array(img.convert('L')).astype(np.float32)
            from scipy.ndimage import uniform_filter
            block = max(15, min(arr.shape[:2]) // 8 | 1)  # odd block size
            local_mean = uniform_filter(arr, size=block)
            binary = (arr > local_mean - 5).astype(np.uint8) * 255
            img = Image.fromarray(binary, mode='L')

        elif mode == 'auto':
            # pipeline: grayscale → contrast stretch → denoise → sharpen
            arr = np.array(img.convert('L')).astype(np.float32)
            # contrast stretch
            lo, hi = np.percentile(arr, 2), np.percentile(arr, 98)
            if hi > lo:
                arr = np.clip((arr - lo) / (hi - lo) * 255, 0, 255)
            img = Image.fromarray(arr.astype(np.uint8), mode='L')
            # denoise
            img = img.filter(ImageFilter.MedianFilter(size=3))
            # sharpen
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=180, threshold=2))

        suffix = os.path.splitext(image_path)[1] or '.png'
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        img.save(tmp.name)
        logging.debug('Preprocessed image saved to: %s', tmp.name)
        return tmp.name

    @classmethod
    def _resolve_backend(cls, backend: str) -> str:
        if backend != 'auto':
            return backend
        key = (OSUtils.get_system(), OSUtils.get_machine())
        return 'rapidocr' if key in cls._AUTO_RAPID else 'paddleocr'

    @staticmethod
    def _run_paddleocr(image_path, lang):
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
        raw = ocr.ocr(image_path, cls=True)
        result = []
        for page in (raw or []):
            for item in (page or []):
                box, (text, confidence) = item
                result.append({'text': text, 'confidence': round(float(confidence), 4), 'box': box})
        return result

    @staticmethod
    def _run_rapidocr(image_path):
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR()
        raw, _ = ocr(image_path)
        result = []
        for item in (raw or []):
            box, text, confidence = item
            result.append({'text': text, 'confidence': round(float(confidence), 4), 'box': box})
        return result

    @staticmethod
    def _run_easyocr(image_path, lang):
        import ssl
        import easyocr
        ssl._create_default_https_context = ssl._create_unverified_context
        lang_map = {'ch': ['ch_sim', 'en'], 'en': ['en']}
        langs = lang_map.get(lang, [lang, 'en'])
        reader = easyocr.Reader(langs, gpu=True)
        raw = reader.readtext(image_path)
        result = []
        for (box, text, confidence) in (raw or []):
            result.append({'text': text, 'confidence': round(float(confidence), 4), 'box': box})
        return result
