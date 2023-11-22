import logging
import ssl
from core.processor import Processor
from pytube import YouTube


# https://pytube.io/en/latest/user/quickstart.html

class PYTUBEProcessor(Processor):
    TPL: str = '{' \
               '"video_url":"https://www.youtube.com/shorts/Fn-osmFZbnA"' \
               ',"file_extension":"mp4"' \
               ',"download_folder":""' \
               ',"specific_file_name":""' \
               ',"file_prefix":""' \
               ',"quality":"HIGH|LOW"' \
               ',"file_download_path_key":""' \
               ',"max_retries":3' \
               ',"timeout":""' \
               '}'
    DESC: str = f''' 
        - To download a YouTube video with a specific link, support different video formats and resolutions.
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_YUTUBE

    def process(self):
        video_url = self.expression2str(self.get_param('video_url')) if self.has_param('video_url') else None
        file_extension = self.expression2str(self.get_param('file_extension')) if self.has_param(
            'file_extension') else 'mp4'
        download_folder = self.expression2str(self.get_param('download_folder')) if self.has_param(
            'download_folder') else 'download'
        specific_file_name = self.expression2str(self.get_param('specific_file_name')) if self.has_param(
            'specific_file_name') else None
        file_prefix = self.expression2str(self.get_param('file_prefix')) if self.has_param('file_prefix') else None
        quality = self.expression2str(self.get_param('quality')) if self.has_param('quality') else None
        timeout = self.expression2str(self.get_param('timeout')) if self.has_param('timeout') else None
        max_retries = self.get_param('max_retries') if self.has_param('max_retries') else 0

        high_quality = True if 'HIGH' in quality else False

        logging.debug('start downloding from' + video_url)

        ssl._create_default_https_context = ssl._create_unverified_context

        yd = YouTube(video_url,
                     on_progress_callback=self._handle_progress,
                     on_complete_callback=self._handle_complete) \
            .streams.filter(progressive=True, file_extension=file_extension).order_by('resolution')

        if high_quality:
            yd = yd.desc()
        else:
            yd = yd.asc()

        yd.first().download(
            output_path=download_folder,
            filename=specific_file_name,
            filename_prefix=file_prefix,
            max_retries=max_retries,
            timeout=timeout
        )

    def _handle_progress(self, stream, chunk, bytes_remaining):
        percentage = (stream.filesize - bytes_remaining) / stream.filesize
        percentage = round(percentage * 100, 2)
        logging.debug(str(percentage) + '% downloaded.')

    def _handle_complete(self, stream, msg):
        logging.debug(f'Download completed, ' + msg)
        path_video_download = self.expression2str(self.get_param('file_download_path_key')) if self.has_param(
            'file_download_path_key') else None

        if not path_video_download is None:
            self.populate_data(path_video_download, msg)
