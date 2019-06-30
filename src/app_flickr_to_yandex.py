import asyncio
import logging
import os
import random
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep
from urllib.parse import urlparse
from xml.etree.ElementTree import Element

import flickrapi
import yadisk

logger = logging.getLogger(__name__)


class App:

    def __init__(self, flickr_key=None, flickr_secret=None,
                 yandex_id=None, yandex_secret=None, yandex_oauth=None) -> None:
        super().__init__()
        self.flickr = flickrapi.FlickrAPI(flickr_key, flickr_secret)
        self.yadisk = yadisk.YaDisk(yandex_id, yandex_secret, yandex_oauth)
        self.executor = ThreadPoolExecutor(4)

    async def run(self):
        self.flickr.authenticate_console()
        if self.flickr.token_valid():
            res = self.flickr.walk_photosets()
            for folder in res:
                completed = await self.process_folder(folder)
                logger.info(f"Completed {completed} tasks in folder {folder.findtext('title')}")

    async def authorize_oob(self):
        self.flickr.get_request_token(oauth_callback='oob')
        authorize_url = self.flickr.auth_url(perms='read')
        print(authorize_url)
        verifier = str(input('Verifier code: '))
        # Trade the request token for an access token
        self.flickr.get_access_token(verifier)

    async def process_folder(self, folder: Element):
        flickr_photoset_title, flickr_photoset_id = folder.findtext('title'), folder.get('id')
        logger.debug(f"Folder #{flickr_photoset_id} {folder} = {flickr_photoset_title}")

        # In case you're using Yandex Services and you're not Russian, maybe it will have another name.
        camera_folder = os.environ.get("YANDEX_PHOTOCAMERA", "Фотокамера")
        yandex_folder = f"disk:/{camera_folder}/{flickr_photoset_title}"
        try:
            self.yadisk.get_meta(yandex_folder)
        except yadisk.exceptions.PathNotFoundError:
            self.yadisk.mkdir(yandex_folder)
        res = self.flickr.walk_set(flickr_photoset_id, 50, extras="url_o")
        loop = asyncio.get_running_loop()
        blocking_tasks = [
            loop.run_in_executor(self.executor, self.process_photo, photo, yandex_folder)
            for photo in res
        ]
        logger.info(f"Waiting for {len(blocking_tasks)} executor tasks")
        completed, pending = await asyncio.wait(blocking_tasks)
        return len(completed)

    def process_photo(self, photo: Element, yandex_folder: str, t=0):
        """
        Process a single photo.

        Use Yandex feature to asynchronously load the photo from external URL.
        In case photo title is missing, a new name will be autogenerated from CDN path.

        Attributes of photo you may want to use if you're going to extend the app:

        - id (str) -- photo id in Flickr
        - url_o (str) -- Full CDN url of the image in original qualitys
        - title (str) -- Image title
        - ispublic (str) -- '0' or '1'
        - isfriend (str) -- '0' or '1'
        - isfamily (str) -- '0' or '1'
        - isprimary (str) -- '0' or '1'
        - secret (str)
        - server (str) -- probably flickr internal server id
        - farm (str)

        :param t: try #
        :param photo: Photo metadata.
        :param yandex_folder: Yandex Disk folder path
        :return:
        """
        id, url_o, title = photo.get('id'), photo.get('url_o'), photo.get('title')
        if url_o is None:
            logger.warning(f"Image {id}: CDN path is Empty. Skipping {photo.attrib}")
            return

        parsed = urlparse(url_o)
        path, ext = os.path.splitext(parsed.path)

        # If we do not know image title or filename, use the autogenreated name from Flickr CDN
        if title == '':
            title = path.replace('/', '')
            logger.warning(f"Image {id}: title was empty, new title is {title} (built from CDN path {url_o}")

        yandex_full_path = f"{yandex_folder}/{title}{ext}"

        if t > 5:
            logger.warn(f"Failed to process {yandex_full_path}, giving up")
            return

        try:
            # First, let's check whether the file already exists. We don't want to abuse Yandex or make clones
            self.yadisk.get_meta(yandex_full_path)
            logger.info(f"Skipping {yandex_full_path}, it's already there")
        except yadisk.exceptions.PathNotFoundError:
            try:
                # This method returns immediately, yandex disk will fetch the photo asynchronously
                self.yadisk.upload_url(url_o, yandex_full_path)
            except yadisk.exceptions.FieldValidationError as fve:
                logger.exception(f"Something went wrong when trying to upload {url_o} to {yandex_full_path}", fve)
            except yadisk.exceptions.TooManyRequestsError as tme:
                logger.warning(f"Too many requests when trying to upload {url_o} to {yandex_full_path} #{t}")
                sleep(random.random())
                return self.process_photo(photo, yandex_folder, t + 1)


if __name__ == '__main__':
    app = App('24e321effac5a2bab1d495941800e2fe', 'a83ab8f70a937508',
              '5bfb4e55ee8d420782c01a7f9c513eaa', '7012d30f061640da8b0e68fa91a2dc60',
              yandex_oauth=os.environ.get('YANDEX_OAUTH'))
    logging.basicConfig(
        level=logging.WARN,
        format='%(threadName)25s %(name)18s: %(message)s',
        stream=sys.stderr,
    )
    asyncio.run(app.run())
