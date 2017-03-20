#    Copyright 2016 Geoscience Australia
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from __future__ import absolute_import, division

import sys
import six
import logging
import logstash
import socket

_REMOTE_LOG_FORMAT_STRING = '%(asctime)s {} %(process)d %(name)s %(levelname)s %(message)s'


class SerialExecutor(object):
    @staticmethod
    def submit(func, *args, **kwargs):
        return func, args, kwargs

    @staticmethod
    def map(func, iterable):
        return [SerialExecutor.submit(func, data) for data in iterable]

    @staticmethod
    def get_ready(futures):
        try:
            result = SerialExecutor.result(futures[0])
            return [(lambda x: x, [result], {})], [], futures[1:]
        except Exception:  # pylint: disable=broad-except
            exc_info = sys.exc_info()
            return [], [(six.reraise, exc_info, {})], futures[1:]

    @staticmethod
    def as_completed(futures):
        for future in futures:
            yield future

    @classmethod
    def next_completed(cls, futures, default):
        results = list(futures)
        if not results:
            return default, results
        result = next(cls.as_completed(results), default)
        results.remove(result)
        return result, results

    @staticmethod
    def results(futures):
        return [SerialExecutor.result(future) for future in futures]

    @staticmethod
    def result(future):
        func, args, kwargs = future
        return func(*args, **kwargs)

    @staticmethod
    def release(future):
        pass


def setup_stdout_logging(level=logging.WARN):
    def remote_function():
        hostname = socket.gethostname()
        log_format_string = _REMOTE_LOG_FORMAT_STRING.format(hostname)

        handler = logging.StreamHandler()
        handler.formatter = logging.Formatter(log_format_string)
        logging.root.handlers = [handler]
        logging.root.setLevel(level)
        if level <= logging.INFO:
            logging.getLogger('rasterio').setLevel(logging.INFO)
    return remote_function


class DatacubeFormatter(logstash.LogstashFormatterVersion1):
    def get_extra_fields(self, record):
        fields = super(DatacubeFormatter, self).get_extra_fields(record)
        if 'process' in record.__dict__:
            fields['process'] = record.__dict__['process']
        return fields


class DatacubeLogstashHandler(logstash.UDPLogstashHandler):
    def __init__(self, host, port=5959, message_type='logstash', tags=None, fqdn=False):
        super(DatacubeLogstashHandler, self).__init__(host, port)
        self.formatter = DatacubeFormatter(message_type, tags, fqdn)


def setup_logstash_logging(host, level=logging.DEBUG):
    local_hostname = socket.gethostname()
    log_format_string = _REMOTE_LOG_FORMAT_STRING.format(local_hostname)

    handler = logging.StreamHandler()
    handler.formatter = logging.Formatter(log_format_string)
    handler.setLevel(logging.WARN)

    logging.root.handlers = [handler, DatacubeLogstashHandler(host, 5959)]

    logging.root.setLevel(level)
    if level <= logging.INFO:
        logging.getLogger('rasterio').setLevel(logging.INFO)


def get_distributed_executor(scheduler):
    """
    :param scheduler: Address of a scheduler
    """
    try:
        import distributed
    except ImportError:
        return None

    class DistributedExecutor(object):
        def __init__(self, client, logging_address):
            """
            :type client: distributed.Client
            :return:
            """
            self._client = client
            self.logging_address = logging_address
            self.setup_logging()

        def setup_logging(self):
            self._client.run(setup_logstash_logging, self.logging_address)

        def submit(self, func, *args, **kwargs):
            return self._client.submit(func, *args, pure=False, **kwargs)

        def map(self, func, iterable):
            return self._client.map(func, iterable)

        @staticmethod
        def get_ready(futures):
            groups = {}
            for f in futures:
                groups.setdefault(f.status, []).append(f)
            return groups.get('finished', []), groups.get('error', []), groups.get('pending', [])

        @staticmethod
        def as_completed(futures):
            return distributed.as_completed(futures)

        @classmethod
        def next_completed(cls, futures, default):
            results = list(futures)
            if not results:
                return default, results
            result = next(cls.as_completed(results), default)
            results.remove(result)
            return result, results

        def results(self, futures):
            return self._client.gather(futures)

        @staticmethod
        def result(future):
            return future.result()

        @staticmethod
        def release(future):
            future.release()

    try:
        return DistributedExecutor(distributed.Client(scheduler), logging_address=scheduler.split(':')[0])
    except IOError:
        return None


def get_multiproc_executor(num_workers):
    try:
        from concurrent.futures import ProcessPoolExecutor, as_completed
    except ImportError:
        return None

    class MultiprocessingExecutor(object):
        def __init__(self, pool):
            self._pool = pool

        def submit(self, func, *args, **kwargs):
            return self._pool.submit(func, *args, **kwargs)

        def map(self, func, iterable):
            return [self.submit(func, data) for data in iterable]

        @staticmethod
        def get_ready(futures):
            completed = []
            failed = []
            pending = []
            for f in futures:
                if f.done():
                    if f.exception():
                        failed.append(f)
                    else:
                        completed.append(f)
                else:
                    pending.append(f)
            return completed, failed, pending

        @staticmethod
        def as_completed(futures):
            return as_completed(futures)

        @classmethod
        def next_completed(cls, futures, default):
            results = list(futures)
            if not results:
                return default, results
            result = next(cls.as_completed(results), default)
            results.remove(result)
            return result, results

        @staticmethod
        def results(futures):
            return [future.result() for future in futures]

        @staticmethod
        def result(future):
            return future.result()

        @staticmethod
        def release(future):
            pass

    return MultiprocessingExecutor(ProcessPoolExecutor(num_workers if num_workers > 0 else None))


EXECUTOR_TYPES = {
    'serial': lambda _: SerialExecutor(),
    'multiproc': get_multiproc_executor,
    'distributed': get_distributed_executor,
}


def list_executors():
    return EXECUTOR_TYPES.keys()


def get_executor(executor_type, executor_arg):
    return EXECUTOR_TYPES[executor_type](executor_arg)
