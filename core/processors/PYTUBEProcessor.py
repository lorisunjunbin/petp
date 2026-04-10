import logging
import os
import socket
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any

from core.processor import Processor
from pytube import YouTube, Playlist
from pytube.exceptions import PytubeError


class PYTUBEProcessor(Processor):
    TPL: str = '{' \
               '"video_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"' \
               ',"download_type":"video|audio|both"' \
               ',"file_extension":"mp4"' \
               ',"download_folder":""' \
               ',"specific_file_name":""' \
               ',"file_prefix":""' \
               ',"quality":"highest|lowest|medium"' \
               ',"resolution":"1080p|720p|480p|360p|240p|144p"' \
               ',"audio_quality":"high|medium|low"' \
               ',"download_captions":"no|yes"' \
               ',"caption_language":"en"' \
               ',"is_playlist":"no|yes"' \
               ',"proxy_url":""' \
               ',"file_download_path_key":""' \
               ',"max_retries":3' \
               ',"timeout":30' \
               '}'
    DESC: str = f'''
        Download a YouTube video with a specific link via pytube, support different video formats and resolutions.

        - video_url: YouTube video URL (supports expression, default: "https://www.youtube.com/shorts/Fn-osmFZbnA")
        - file_extension: video file extension to filter, e.g. "mp4", "webm" (default: "mp4")
        - download_folder: local folder to save the downloaded file (default: "download")
        - specific_file_name: exact filename for the downloaded file (optional)
        - file_prefix: prefix prepended to the downloaded filename (optional)
        - quality: video quality, "HIGH" for highest resolution, "LOW" for lowest (default: "HIGH")
        - proxy_url: HTTP/HTTPS proxy URL, e.g. "http://127.0.0.1:7890" (optional, also reads env HTTP_PROXY/HTTPS_PROXY)
        - file_download_path_key: key of data_chain to store the downloaded file path (optional)
        - max_retries: number of retry attempts on download failure (default: 3)
        - timeout: download timeout in seconds (optional)

        {TPL}
    '''

    def __init__(self):
        self._proxies: Dict[str, str] = {}

    def get_category(self) -> str:
        return super().CATE_YUTUBE

    def process(self):
        try:
            params = self._get_parameters()
            self._configure_network(params)

            if params['is_playlist']:
                self._download_playlist(params)
            else:
                self._download_single_video(params)

        except (urllib.error.URLError, socket.gaierror) as e:
            msg = (
                f"Network/DNS error: {e}. "
                f"YouTube may be blocked in your network. "
                f"Set 'proxy_url' in task input (e.g. 'http://127.0.0.1:7890') "
                f"or configure environment variable HTTPS_PROXY."
            )
            logging.error(msg)
            self.populate_data("error", msg)
        except PytubeError as e:
            logging.error(f"YouTube download error: {str(e)}")
            self.populate_data("error", str(e))
        except Exception as e:
            logging.error(f"Unknown error during processing: {str(e)}")
            self.populate_data("error", str(e))

    # ------------------------------------------------------------------
    # Network helpers
    # ------------------------------------------------------------------

    def _configure_network(self, params: Dict[str, Any]) -> None:
        """Set up SSL bypass and optional proxy for all pytube urllib calls."""
        ssl._create_default_https_context = ssl._create_unverified_context

        proxy_url = (params.get('proxy_url') or '').strip()
        # Fall back to environment variables when not set in task params
        env_http  = (os.environ.get('HTTP_PROXY')  or os.environ.get('http_proxy')  or '').strip()
        env_https = (os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy') or '').strip()

        proxies = {
            'http':  proxy_url or env_http,
            'https': proxy_url or env_https,
        }
        proxies = {k: v for k, v in proxies.items() if v}
        self._proxies = proxies

        if proxies:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
            urllib.request.install_opener(opener)
            masked = {k: self._mask_proxy(v) for k, v in proxies.items()}
            logging.info(f"PYTUBE proxy enabled: {masked}")
        else:
            logging.info("PYTUBE proxy not configured; using direct network connection")

    @staticmethod
    def _mask_proxy(proxy_url: str) -> str:
        """Mask credentials in proxy URL for safe logging."""
        if '@' not in proxy_url:
            return proxy_url
        try:
            head, tail = proxy_url.rsplit('@', 1)
            scheme = head.split('://')[0] if '://' in head else ''
            return f"{scheme}://***@{tail}" if scheme else f"***@{tail}"
        except Exception:
            return '***'

    def _new_youtube(self, url: str, with_oauth: bool = False) -> YouTube:
        """Create a YouTube object, injecting proxy when configured."""
        kwargs: Dict[str, Any] = {
            'on_progress_callback': self._handle_progress,
            'on_complete_callback': self._handle_complete,
        }
        if with_oauth:
            kwargs['use_oauth'] = False
            kwargs['allow_oauth_cache'] = True
        if self._proxies:
            kwargs['proxies'] = self._proxies

        try:
            return YouTube(url, **kwargs)
        except TypeError:
            # Older pytube variants may not accept 'proxies' in constructor
            kwargs.pop('proxies', None)
            return YouTube(url, **kwargs)

    # ------------------------------------------------------------------
    # Parameter extraction
    # ------------------------------------------------------------------

    def _get_parameters(self) -> Dict[str, Any]:
        """Process and retrieve all parameters"""
        params = {
            'video_url':            self.expression2str(self.get_param('video_url'))            if self.has_param('video_url')            else None,
            'download_type':        self.expression2str(self.get_param('download_type'))        if self.has_param('download_type')        else 'video',
            'file_extension':       self.expression2str(self.get_param('file_extension'))       if self.has_param('file_extension')       else 'mp4',
            'download_folder':      self.expression2str(self.get_param('download_folder'))      if self.has_param('download_folder')      else 'download',
            'specific_file_name':   self.expression2str(self.get_param('specific_file_name'))   if self.has_param('specific_file_name')   else None,
            'file_prefix':          self.expression2str(self.get_param('file_prefix'))          if self.has_param('file_prefix')          else None,
            'quality':              self.expression2str(self.get_param('quality'))              if self.has_param('quality')              else 'highest',
            'resolution':           self.expression2str(self.get_param('resolution'))           if self.has_param('resolution')           else None,
            'audio_quality':        self.expression2str(self.get_param('audio_quality'))        if self.has_param('audio_quality')        else 'high',
            'download_captions':    self.has_param('download_captions') and "yes" == self.get_param('download_captions'),
            'caption_language':     self.expression2str(self.get_param('caption_language'))     if self.has_param('caption_language')     else 'en',
            'is_playlist':          self.has_param('is_playlist') and "yes" == self.get_param('is_playlist'),
            'proxy_url':            self.expression2str(self.get_param('proxy_url'))            if self.has_param('proxy_url')            else None,
            'file_download_path_key': self.expression2str(self.get_param('file_download_path_key')) if self.has_param('file_download_path_key') else None,
            'max_retries':          self.get_param('max_retries') if self.has_param('max_retries') else 3,
            'timeout':              self.get_param('timeout')     if self.has_param('timeout')     else 30,
        }
        os.makedirs(params['download_folder'], exist_ok=True)
        return params

    # ------------------------------------------------------------------
    # Download logic  (unchanged except YouTube() → _new_youtube())
    # ------------------------------------------------------------------

    def _download_single_video(self, params: Dict[str, Any]):
        """Download a single video"""
        logging.info(f"Starting download from {params['video_url']}")

        yt = self._new_youtube(params['video_url'], with_oauth=True)

        video_info = {
            'title':        yt.title,
            'author':       yt.author,
            'publish_date': str(yt.publish_date),
            'views':        yt.views,
            'length':       yt.length,
            'description':  yt.description,
        }
        self.populate_data("video_info", video_info)

        download_results = {}

        if params['download_type'] in ['video', 'both']:
            video_path = self._download_video(yt, params)
            if video_path:
                download_results['video_path'] = video_path

        if params['download_type'] in ['audio', 'both']:
            audio_path = self._download_audio(yt, params)
            if audio_path:
                download_results['audio_path'] = audio_path

        if params['download_captions']:
            caption_path = self._download_caption(yt, params)
            if caption_path:
                download_results['caption_path'] = caption_path

        if params['file_download_path_key']:
            self.populate_data(params['file_download_path_key'], download_results)

    def _download_playlist(self, params: Dict[str, Any]):
        """Download a playlist"""
        logging.info(f"Starting playlist download: {params['video_url']}")

        playlist = Playlist(params['video_url'])
        logging.info(f"Playlist title: {playlist.title}")
        logging.info(f"Contains {len(playlist.video_urls)} videos")

        self.populate_data("playlist_info", {
            'title':       playlist.title,
            'video_count': len(playlist.video_urls),
        })

        download_results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            for video_url in playlist.video_urls:
                video_params = params.copy()
                video_params['video_url'] = video_url
                video_params['is_playlist'] = False
                future = executor.submit(self._download_single_video_for_playlist, video_params)
                result = future.result()
                if result:
                    download_results.append(result)

        if params['file_download_path_key']:
            self.populate_data(params['file_download_path_key'], download_results)

    def _download_single_video_for_playlist(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Download a single video for a playlist and return result information"""
        try:
            yt = self._new_youtube(params['video_url'])
            result = {'title': yt.title, 'url': params['video_url']}

            if params['download_type'] in ['video', 'both']:
                video_path = self._download_video(yt, params)
                if video_path:
                    result['video_path'] = video_path

            if params['download_type'] in ['audio', 'both']:
                audio_path = self._download_audio(yt, params)
                if audio_path:
                    result['audio_path'] = audio_path

            return result
        except Exception as e:
            logging.error(f"Failed to download playlist video {params['video_url']}: {str(e)}")
            return None

    def _download_video(self, yt: YouTube, params: Dict[str, Any]) -> Optional[str]:
        """Download video component"""
        try:
            stream_query = yt.streams.filter(progressive=True, file_extension=params['file_extension'])

            if params['resolution']:
                res_streams = stream_query.filter(res=params['resolution'])
                if res_streams:
                    stream_query = res_streams

            if params['quality'] == 'highest':
                stream = stream_query.order_by('resolution').desc().first()
            elif params['quality'] == 'lowest':
                stream = stream_query.order_by('resolution').asc().first()
            else:
                streams = stream_query.order_by('resolution').desc().all()
                stream = streams[len(streams) // 2] if streams else None

            if not stream:
                logging.warning("No suitable video stream found, trying to get any available stream")
                stream = yt.streams.filter(file_extension=params['file_extension']).first()

            if not stream:
                logging.error("Cannot find any downloadable video stream")
                return None

            return stream.download(
                output_path=params['download_folder'],
                filename=params['specific_file_name'],
                filename_prefix=params['file_prefix'],
                max_retries=params['max_retries'],
                timeout=params['timeout'],
            )
        except Exception as e:
            logging.error(f"Video download failed: {str(e)}")
            return None

    def _download_audio(self, yt: YouTube, params: Dict[str, Any]) -> Optional[str]:
        """Download audio component"""
        try:
            stream_query = yt.streams.filter(only_audio=True)

            if params['audio_quality'] == 'high':
                stream = stream_query.order_by('abr').desc().first()
            elif params['audio_quality'] == 'low':
                stream = stream_query.order_by('abr').asc().first()
            else:
                streams = stream_query.order_by('abr').desc().all()
                stream = streams[len(streams) // 2] if streams else None

            if not stream:
                logging.error("Cannot find downloadable audio stream")
                return None

            audio_filename = f"{params['specific_file_name'] or yt.title}_audio"
            return stream.download(
                output_path=params['download_folder'],
                filename=audio_filename,
                filename_prefix=params['file_prefix'],
                max_retries=params['max_retries'],
                timeout=params['timeout'],
            )
        except Exception as e:
            logging.error(f"Audio download failed: {str(e)}")
            return None

    def _download_caption(self, yt: YouTube, params: Dict[str, Any]) -> Optional[str]:
        """Download captions"""
        try:
            caption_lang = params['caption_language']
            captions = yt.captions

            target_lang = caption_lang if caption_lang in captions else (list(captions.keys())[0] if captions else None)
            if not target_lang:
                logging.warning(f"No captions available for this video")
                return None

            if target_lang != caption_lang:
                logging.warning(f"Caption language '{caption_lang}' not found, using '{target_lang}' instead")

            caption = captions[target_lang]
            caption_filename = f"{params['specific_file_name'] or yt.title}_{target_lang}.srt"
            caption_path = os.path.join(params['download_folder'], caption_filename)
            with open(caption_path, 'w', encoding='utf-8') as f:
                f.write(caption.generate_srt_captions())
            return caption_path
        except Exception as e:
            logging.error(f"Caption download failed: {str(e)}")
            return None

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _handle_progress(self, stream, chunk, bytes_remaining):
        """Handle download progress callback"""
        try:
            file_size = stream.filesize
            bytes_downloaded = file_size - bytes_remaining
            percentage = (bytes_downloaded / file_size) * 100
            progress_info = {
                'percentage':  round(percentage, 2),
                'downloaded':  self._format_size(bytes_downloaded),
                'total':       self._format_size(file_size),
                'file_type':   'video' if stream.includes_video_track else 'audio',
                'resolution':  getattr(stream, 'resolution', 'N/A'),
            }
            self.populate_data("download_progress", progress_info)
            logging.info(f"Download progress: {progress_info['percentage']}% ({progress_info['downloaded']}/{progress_info['total']})")
        except Exception as e:
            logging.error(f"Error handling progress callback: {str(e)}")

    def _handle_complete(self, stream, file_path):
        """Handle download completion callback"""
        try:
            file_type = 'video' if stream.includes_video_track else 'audio'
            logging.info(f"{file_type} download completed: {file_path}")
            self.populate_data("download_complete", {
                'file_path':  file_path,
                'file_size':  self._format_size(os.path.getsize(file_path)),
                'file_type':  file_type,
                'itag':       stream.itag,
                'resolution': getattr(stream, 'resolution', 'N/A'),
            })
        except Exception as e:
            logging.error(f"Error handling completion callback: {str(e)}")

    def _format_size(self, bytes_size):
        """Format file size to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024 or unit == 'TB':
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024
