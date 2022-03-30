from datetime import datetime
from typing import List, Union
import ntpath
import magic
import os

class Episode:
    def __init__(self, data: dict, podcast, api):
        """
        Interact with a specific podcast episode

        :param data: JSON data for episode
        :type data: dict
        :param podcast: Podcast that the episode belongs to
        :type podcast: Podcast
        :param api: PocketCasts API object
        :type api: PocketCast
        """
        self._data = data
        self._podcast = podcast
        if not self._podcast:
            self._podcast = api.get_podcast_by_id(podcast_id=self.podcast_id)
        self._api = api

    @property
    def share_link(self) -> Union[str, None]:
        """
        Get share link for this episode

        :return: share link
        :rtype: str
        """
        endpoint = _get_endpoint("share")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        data = self._api._post_json(url=url,
                                    data={'episode': self.id,
                                          'podcast': self.podcast_id})
        if data:
            return data.get('url')
        return None

    @property
    def podcast(self):
        """
        Get episode's corresponding podcast

        :rtype: Podcast
        """
        if not self._podcast:
            self._podcast = self._api.get_podcast_by_id(podcast_id=self.podcast_id)
        return self._podcast

    @property
    def title(self) -> str:
        """
        Get episode title

        :rtype: str
        """
        return self._data.get('title')

    @property
    def id(self) -> str:
        """
        Get episode ID

        :rtype: str
        """
        return self._data.get('uuid')

    @property
    def duration(self) -> int:
        """
        Get episode duration

        :rtype: int
        """
        return self._data.get('duration')

    @property
    def published_date(self) -> Union[datetime, None]:
        """
        Get episode's publication date

        :rtype: datetime.datetime
        """
        try:
            return datetime.strptime(self._data.get('published'), 'YYYY-MM-DDTHH:mm:ssZ')
        except:
            return None

    @property
    def url(self) -> str:
        """
        Get episode url

        :rtype: str
        """
        return self._data.get('url')

    @property
    def playing(self) -> bool:
        """
        Get episode playing status

        :rtype: bool
        """
        return True if self._data.get('playing_status') > 0 else False

    @property
    def size(self) -> int:
        """
        Get episode size

        :rtype: int
        """
        return self._data.get('size')

    @property
    def file_type(self) -> str:
        """
        Get episode file type

        :rtype: str
        """
        return self._data.get('fileType')

    @property
    def type(self) -> str:
        """
        Get episode type

        :rtype: str
        """
        return self._data.get('episodeType')

    @property
    def season(self) -> int:
        """
        Get episode season

        :rtype: int
        """
        return self._data.get('episodeSeason')

    @property
    def number(self) -> int:
        """
        Get episode number

        :rtype: int
        """
        return self._data.get('episodeNumber')

    @property
    def current_position(self) -> int:
        """
        Get episode current position

        :rtype: int
        """
        return self._data.get('playedUpTo')

    @property
    def deleted(self) -> bool:
        """
        Get whether the episode is deleted

        :rtype: bool
        """
        return self._data.get('isDeleted')

    @property
    def starred(self) -> bool:
        """
        Get whether episode is starred

        :rtype: bool
        """
        return self._data.get('starred')

    @property
    def podcast_id(self) -> str:
        """
        Get ID of corresponding podcast

        :rtype: str
        """
        return self._data.get('podcastUuid') if self._data.get('podcastUuid') else self.podcast.id

    @property
    def podcast_title(self) -> str:
        """
        Get title of corresponding podcast

        :rtype: str
        """
        return self._data.get('podcastTitle')

    @property
    def show_notes(self) -> str:
        """
        Get the show notes for the episode

        :return: show notes
        :rtype: str
        """
        url = f"https://podcast-api.pocketcasts.com/episode/show_notes/{self.id}"
        print(url)
        data = self._api._get_json(url=url, include_token=True)
        return data.get('show_notes', "")

    def update_progress(self, progress: int) -> bool:
        """
        Update progress in this episode

        :param progress: Episode progress in seconds
        :type progress: int
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if progress > self.duration:
            raise Exception("Cannot update with progress longer than episode duration")
        endpoint = _get_endpoint("play_status")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.id,
                                 'podcast': self.podcast_id,
                                 'status': 2,
                                 'position': progress
                                 }
                           ):
            return True
        return False

    def mark_played(self) -> bool:
        """
        Mark this episode as played

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("play_status")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.id,
                                 'podcast': self.podcast_id,
                                 'status': 3
                                 }
                           ):
            return True
        return False

    def mark_unplayed(self) -> bool:
        """
        Mark this episode as unplayed

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("play_status")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.id,
                                 'podcast': self.podcast_id,
                                 'status': 1,
                                 'position': 0
                                 }
                           ):
            return True
        return False

    def add_star(self) -> bool:
        """
        Add a star to this episode

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("episode_star")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           json={"uuid": self.id,
                                 "podcast": self.podcast_id,
                                 "star": True}
                           ):
            return True
        return False

    def remove_star(self) -> bool:
        """
        Remove a star from this episode

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("episode_star")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           json={"uuid": self.id,
                                 "podcast": self.podcast_id,
                                 "star": False}
                           ):
            return True
        return False

    def archive(self) -> bool:
        """
        Archive this episode

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("episode_archive")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           data={'episodes': [
                               {'uuid': self.id,
                                'podcast': self.podcast_id
                                }
                           ],
                               'archive': True}):
            return True
        return False

    def unarchive(self) -> bool:
        """
        Unarchive this episode

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("episode_archive")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'episodes': [
                               {'uuid': self.id,
                                'podcast': self.podcast_id
                                }
                           ],
                               'archive': False}):
            return True
        return False

    def play_next(self) -> bool:
        """
        Add this episode to the front of the "Play Next" queue

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("play_next")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           data={'version': 2,
                                 'episode': {'uuid': self.id,
                                             'title': self.title,
                                             'url': self.url,
                                             'podcast': self.podcast_id,
                                             'published': self.published_date
                                             }
                                 }
                           ):
            return True
        return False

    def play_last(self) -> bool:
        """
        Add this episode to the end of the "Play Next" queue

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("play_last")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           data={'version': 2,
                                 'episode': {'uuid': self.id,
                                             'title': self.title,
                                             'url': self.url,
                                             'podcast': self.podcast_id,
                                             'published': self.published_date
                                             }
                                 }
                           ):
            return True
        return False