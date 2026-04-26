import logging

from core.processor import Processor


class CAPTCHAProcessor(Processor):
    TPL: str = '{"image_path":"", "image_path_key":"", "mode":"ocr", "slide_target_key":"", "result_key":"captcha_result"}'
    DESC: str = f'''
        Recognise captcha images locally using ddddocr (no API key required).
        pip install ddddocr

        Supported modes:
        - ocr        Standard text/digit captcha recognition (default).
                     Returns the recognised string.
        - slide      Slider captcha: find the gap position in a background image.
                     Requires image_path (target/piece) and slide_target_key (background).
                     Returns {{"target": [x, y]}} with the pixel offset to move the slider.
        - det        Object-detection mode: locate all text regions in the image.
                     Returns a list of bounding boxes [{{"x": x1, "y": y1, "w": w, "h": h}}].

        Tips:
        - For noisy/coloured backgrounds try setting color_filter (see advanced params).
        - Use old=true for older-style simple digit captchas if default model is less accurate.
        - result_key stores the full result; for ocr mode it is also a plain string.

        - image_path: path to the captcha image file (supports expression)
        - image_path_key: data_chain key for the image path; takes priority over image_path if set
        - mode: recognition mode — ocr | slide | det (default: "ocr")
        - slide_target_key: data_chain key for the slide background image path (required for mode=slide)
        - result_key: data_chain key to store the result (default: "captcha_result")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        import ddddocr

        image_path = self.get_data(self.get_param('image_path_key')) if self.has_param('image_path_key') \
            else self.expression2str(self.get_param('image_path'))

        mode       = self.explain_param_or_default('mode', 'ocr')
        result_key = self.explain_param_or_default('result_key', 'captcha_result')

        logging.info('Running captcha recognition: %s (mode=%s)', image_path, mode)

        ocr = ddddocr.DdddOcr(show_ad=False, det=(mode == 'det'))

        with open(image_path, 'rb') as f:
            img_bytes = f.read()

        if mode == 'ocr':
            result = ocr.classification(img_bytes)
            logging.info('Captcha OCR result: %s', result)

        elif mode == 'slide':
            bg_path = self.get_data(self.get_param('slide_target_key'))
            with open(bg_path, 'rb') as f:
                bg_bytes = f.read()
            raw = ocr.slide_match(img_bytes, bg_bytes)
            result = {'target': raw.get('target', [])}
            logging.info('Captcha slide result: %s', result)

        elif mode == 'det':
            bboxes = ocr.detection(img_bytes)
            result = [{'x': b[0], 'y': b[1], 'w': b[2] - b[0], 'h': b[3] - b[1]} for b in bboxes]
            logging.info('Captcha det result: %d regions', len(result))

        else:
            raise ValueError(f'Unknown captcha mode: {mode}. Choose from: ocr, slide, det')

        self.populate_data(result_key, result)
