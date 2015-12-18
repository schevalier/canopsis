# -*- coding: utf-8 -*-
# --------------------------------
# Copyright (c) 2015 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------

from canopsis.middleware.registry import MiddlewareRegistry
from canopsis.configuration.configurable.decorator import conf_paths
from canopsis.configuration.configurable.decorator import add_category
from canopsis.configuration.model import Parameter

from canopsis.check.base import Check
from canopsis.task import get_task

from time import time, sleep
from itertools import cycle
import multiprocessing


CONF_PATH = 'engine/base.conf'
CATEGORY = 'ENGINE'
CONTENT = [
    Parameter('event_processing'),
    Parameter('beat_processing'),
    Parameter('beat_interval', int),
    Parameter('chain_to', Parameter.array()),
    Parameter('balanced_chaining', Parameter.bool),
    Parameter('beat_warn_time', int),
    Parameter('beat_crit_time', int),
    Parameter('work_warn_time', int),
    Parameter('work_crit_time', int)
]


@conf_paths(CONF_PATH)
@add_category(CATEGORY, content=CONTENT)
class Engine(MiddlewareRegistry):

    MOM = 'mom'

    DEFAULT_BEAT_INTERVAL = 60
    DEFAULT_BALANCED_CHAINING = False

    DEFAULT_BEAT_WARN_TIME = 5
    DEFAULT_BEAT_CRIT_TIME = 10

    DEFAULT_WORK_WARN_TIME = 3
    DEFAULT_WORK_CRIT_TIME = 5

    class DropMessage(Exception):
        pass

    @property
    def beat_interval(self):
        if not hasattr(self, '_beat_interval'):
            self.beat_interval = None

        return self._beat_interval

    @beat_interval.setter
    def beat_interval(self, value):
        if value is None:
            value = Engine.DEFAULT_BEAT_INTERVAL

        self._beat_interval = value

    @property
    def chain_to(self):
        if not hasattr(self, '_chain_to'):
            self.chain_to = None

        return self._chain_to

    @chain_to.setter
    def chain_to(self, value):
        if value is None:
            value = []

        self._chain_to = value
        self.next_in_chain = cycle(self._chain_to)

    @property
    def balanced_chaining(self):
        if not hasattr(self, '_balanced_chaining'):
            self.balanced_chaining = None

        return self._balanced_chaining

    @balanced_chaining.setter
    def balanced_chaining(self, value):
        if value is None:
            value = Engine.DEFAULT_BALANCED_CHAINING

        self._balanced_chaining = value

    @property
    def beat_warn_time(self):
        if not hasattr(self, '_beat_warn_time'):
            self.beat_warn_time = None

        return self._beat_warn_time

    @beat_warn_time.setter
    def beat_warn_time(self, value):
        if value is None:
            value = Engine.DEFAULT_BEAT_WARN_TIME

        self._beat_warn_time = value

    @property
    def beat_crit_time(self):
        if not hasattr(self, '_beat_crit_time'):
            self.beat_crit_time = None

        return self._beat_crit_time

    @beat_crit_time.setter
    def beat_crit_time(self, value):
        if value is None:
            value = Engine.DEFAULT_BEAT_CRIT_TIME

        self._beat_crit_time = value

    @property
    def work_warn_time(self):
        if not hasattr(self, '_work_warn_time'):
            self.work_warn_time = None

        return self._work_warn_time

    @work_warn_time.setter
    def work_warn_time(self, value):
        if value is None:
            value = Engine.DEFAULT_WORK_WARN_TIME

        self._work_warn_time = value

    @property
    def work_crit_time(self):
        if not hasattr(self, '_work_crit_time'):
            self.work_crit_time = None

        return self._work_crit_time

    @work_crit_time.setter
    def work_crit_time(self, value):
        if value is None:
            value = Engine.DEFAULT_WORK_CRIT_TIME

        self._work_crit_time = value

    @property
    def event_processing(self):
        """
        Event processing event_processing executed in the work
        """

        return self._event_processing

    @event_processing.setter
    def event_processing(self, value):
        """
        Change of event_processing.

        :param value: new event_processing to use. If None or wrong value,
            event_processing is used
        :type value: NoneType, str or function
        """

        # by default, load default message processing
        if value is None:
            value = event_processing

        # if str, load the related function
        elif isinstance(value, basestring):
            try:
                value = get_task(value)

            except ImportError:
                self.logger.error('Impossible to load %s' % value)
                value = event_processing

        # set _event_processing and work
        self._event_processing = value

    @property
    def beat_processing(self):
        """
        Task executed in the beat
        """

        return self._beat_processing

    @beat_processing.setter
    def beat_processing(self, value):
        """
        Change of beat_processing.

        :param value: new beat_processing to use. If None or wrong value,
            beat_processing is used
        :type value: NoneType, str or function
        """

        # by default, load default beat processing
        if value is None:
            value = beat_processing

        # if str, load the related function
        elif isinstance(value, basestring):
            try:
                value = get_task(value)

            except ImportError:
                self.logger.error('Impossible to load %s' % value)
                value = beat_processing

        # set _beat_processing and work
        self._beat_processing = value

    def __new__(cls, *args, **kwargs):
        if cls is Engine:
            raise TypeError('Engine may not be instantiated')

        return MiddlewareRegistry.__new__(cls, *args, **kwargs)

    def __init__(
        self,
        name,
        worker=0,
        event_processing=None,
        beat_processing=None,
        beat_interval=None,
        chain_to=None,
        balanced_chaining=None,
        beat_warn_time=None,
        beat_crit_time=None,
        work_warn_time=None,
        work_crit_time=None,
        *args, **kwargs
    ):
        super(Engine, self).__init__(*args, **kwargs)

        self.name = name
        self.worker = worker

        if event_processing is not None:
            self.event_processing = event_processing

        if beat_processing is not None:
            self.beat_processing = beat_processing

        if beat_interval is not None:
            self.beat_interval = beat_interval

        if chain_to is not None:
            self.chain_to = chain_to

        if balanced_chaining is not None:
            self.balanced_chaining = balanced_chaining

        if beat_warn_time is not None:
            self.beat_warn_time = beat_warn_time

        if beat_crit_time is not None:
            self.beat_crit_time = beat_crit_time

        if work_warn_time is not None:
            self.work_warn_time = work_warn_time

        if work_crit_time is not None:
            self.work_crit_time = work_crit_time

        self.running = multiprocessing.Event()
        self.last_beat = 0
        self.counter = {
            'total': 0,
            'passed': 0,
            'dropped': 0,
            'errored': 0,
            'beattime': 0,
            'worktime': 0
        }

    def beat(self, *args, **kwargs):
        start = time()

        if self.beat_interval:
            now = time()
            timestep = now - (self.last_beat + self.beat_interval)

            if timestep:
                self.beat_processing(
                    engine=self,
                    logger=self.logger,
                    timestep=timestep,
                    *args, **kwargs
                )

                self.send_stats()

                self.last_beat = now

        elapsed = time() - start
        self.counter['beattime'] += elapsed

        # Log elapsed time
        logmethod = self.logger.debug

        if elapsed > self.beat_crit_time:
            logmethod = self.logger.error

        elif elapsed > self.beat_warn_time:
            logmethod = self.logger.warning

        logmethod('Beat lasted %.02f seconds', elapsed)

        return elapsed

    def send_stats(self):
        evt_per_sec = float(self.counter['total']) / self.beat_interval
        sec_per_evt = self.counter['worktime'] / self.counter['total']
        state = Check.OK

        if sec_per_evt > self.work_crit_time:
            state = Check.MAJOR

        elif sec_per_evt > self.work_warn_time:
            state = Check.MINOR

        elif self.counter['errored']:
            state = Check.CRITICAL

        output = '{0} evt/sec, {1} sec/evt'.format(evt_per_sec, sec_per_evt)
        long_output = '{0} passed, ' \
            '{1} dropped, ' \
            '{2} errored, ' \
            '{3}s in work, ' \
            '{4}s in beat'.format(
                self.counter['passed'],
                self.counter['dropped'],
                self.counter['errored'],
                self.counter['worktime'],
                self.counter['beattime']
            )

        event = Check.create(
            connector_name='engine',
            source_type='resource',
            component=self.name,
            resource=self.worker,
            state=state,
            output=output,
            long_output=long_output,
            metrics=[
                {
                    'metric': 'evt_per_sec',
                    'value': evt_per_sec,
                    'type': 'GAUGE',
                    'unit': 'evt/s'
                }, {
                    'metric': 'sec_per_evt',
                    'value': sec_per_evt,
                    'type': 'GAUGE',
                    'unit': 's',
                    'warn': self.work_warn_time,
                    'crit': self.work_crit_time
                }, {
                    'metric': 'worktime',
                    'value': self.counter['worktime'],
                    'type': 'GAUGE',
                    'unit': 's',
                    'warn': self.work_warn_time,
                    'crit': self.work_crit_time
                }, {
                    'metric': 'beattime',
                    'value': self.counter['beattime'],
                    'type': 'GAUGE',
                    'unit': 's',
                    'warn': self.beat_warn_time,
                    'crit': self.beat_crit_time
                }, {
                    'metric': 'evt_passed',
                    'value': self.counter['passed'],
                    'type': 'COUNTER',
                    'unit': 'evt'
                }, {
                    'metric': 'evt_dropped',
                    'value': self.counter['dropped'],
                    'type': 'COUNTER',
                    'unit': 'evt'
                }, {
                    'metric': 'evt_errored',
                    'value': self.counter['errored'],
                    'type': 'COUNTER',
                    'unit': 'evt'
                }
            ]
        )

        publisher = self[Engine.MOM].get_publisher()
        publisher(event)

        for key in self.counter:
            self.counter[key] = 0

    def work(self, message, *args, **kwargs):
        start = time()

        try:
            result = self.event_processing(
                engine=self,
                logger=self.logger,
                message=message,
                *args, **kwargs
            )

        except Engine.DropMessage:
            self.logger.debug('Message dropped')
            self.counter['dropped'] += 1

        except Exception:
            self.logger.error('Worker raised exception', exc_info=True)
            self.counter['errored'] += 1

        else:
            if result is None:
                result = message

            self.chain_message(result)
            self.counter['passed'] += 1

        finally:
            self.counter['total'] += 1

        elapsed = time() - start
        self.counter['worktime'] += elapsed

        # Log elapsed time
        logmethod = self.logger.debug

        if elapsed > self.work_crit_time:
            logmethod = self.logger.error

        elif elapsed > self.work_warn_time:
            logmethod = self.logger.warning

        logmethod('Worker lasted %.02f seconds', elapsed)

    def chain_message(self, message):
        mom = self[Engine.MOM]

        def publish(msg, dest):
            publisher = mom.get_publisher(dest)
            publisher(msg)

        map(
            lambda dest: publish(message, dest),
            [self.next_in_chain.next()]
            if self.balanced_chaining
            else self.chain_to
        )

    def run(self):
        mom = self[Engine.MOM]

        consumer = mom.get_consumer(self.work)
        consumer.start()

        self.running.set()

        while self.running.is_set():
            try:
                elapsed = self.beat()

            except Exception:
                self.logger.error('Beat raised exception', exc_info=True)
                elapsed = 0

            if elapsed < 1:
                sleep(1 - elapsed)

        consumer.stop()

    def stop(self):
        self.running.clear()

    @classmethod
    def load(cls, name, worker=0, *args, **kwargs):
        """Load a new engine in adding a specific conf_path.

        :param str name: engine name.
        :param int worker: worker instance number.
        :param tuple args: used in new engine initialization such as varargs.
        :param dict kwargs: used in new engine initialization such as keywords.
        """

        decorator = conf_paths('engines/{0}.conf'.format(name))
        engine = decorator(type(name, (cls,), {}))

        return engine(name=name, worker=worker, *args, **kwargs)


def event_processing(engine, event, **params):
    """
    Event processing signature to respect in order to process a event.

    A condition may returns a boolean value.

    :param Engine engine: engine which process the event.
    :param dict event: event to process.
    :param dict params: event processing additional parameters.
    """

    return event


def beat_processing(engine, timestep, **params):
    """
    Beat processing signature to respect in order to execute a periodic task.

    :param Engine engine: engine which executes the beat.
    :param float timestep: time in seconds since last beat.
    :param dict params: beat processing additional parameters.
    """

    pass
