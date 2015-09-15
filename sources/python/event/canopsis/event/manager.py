# -*- coding: utf-8 -*-

from canopsis.configuration.configurable.decorator import (
    conf_paths, add_category)
from canopsis.middleware.registry import MiddlewareRegistry

CONF_PATH = 'event/event.conf'
CATEGORY = 'EVENT'


@conf_paths(CONF_PATH)
@add_category(CATEGORY)
class EventManager(MiddlewareRegistry):

    EVENT_STORAGE = 'event_storage'
    """
    Manage events in Canopsis
    """

    def __init__(self, *args, **kwargs):

        super(EventManager, self).__init__(*args, **kwargs)

    @staticmethod
    def get_rk(event):
        rk = '{0}.{1}.{2}.{3}.{4}'.format(
            event['connector'],
            event['connector_name'],
            event['event_type'],
            event['source_type'],
            event['component']
        )

        if event['source_type'] == 'resource':
            rk = '{0}.{1}'.format(rk, event['resource'])

        return rk

    def get(self, rk):

        return self[EventManager.EVENT_STORAGE].get_elements(ids=rk)

    def find(
            self,
            limit=None,
            skip=None,
            ids=None,
            sort=None,
            with_count=False,
            query=None,
            projection=None
    ):

        """
        Retrieve information from data sources

        :param ids: an id list for document to search
        :param limit: maximum record fetched at once
        :param skip: ordinal number where selection should start
        :param with_count: compute selection count when True
        """

        result = self[EventManager.EVENT_STORAGE].get_elements(
            ids=ids,
            skip=skip,
            sort=sort,
            limit=limit,
            query=query,
            with_count=with_count,
            projection=projection
        )
        return result

    def put_event(self, event, rk=None):
        """Put input event in database.

        :param dict event: event to put/update.
        :param str rk: event rk to use. Calculated by default.
        """

        if rk is None:
            rk = self.get_rk(event)

        self[EventManager.EVENT_STORAGE].put_element(element=event, _id=rk)

    def update_event(self, content, event):
        """Update input event with content.

        :param dict content: content to update in the event.
        :param dict event: event query.
        """

        self[EventManager.EVENT_STORAGE].update_elements(
            data=content, query=event, multi=False
        )

    def remove(self, _filter=None):
        """Remove events corresponding to input filter.

        :param dict filter: deletion filter. Remove all events if None.
        """

        self[EventManager.EVENT_STORAGE].remove_elements(_filter=_filter)
