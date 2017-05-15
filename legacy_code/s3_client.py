# -*- coding: utf-8 -*-
"""
"""
import struct
import gevent
import gevent.monkey
from boto3.session import Session
from utils import timer


gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()
DEFAULT_TIMEOUT = 2


@timer(times=50)
def get_by_offset(client, start, end):
    response = client.get_object(
        Bucket='bytedance-root',
        Range='bytes=%s-%s' % (start, end),
        Key='user/wudi/event_param_test_4_20170101_compact6.sort.bin'
    )
    group_id, index = struct.unpack("QI", response['Body'].read())
    return group_id


class S3ObjectSequence(object):

    def __init__(self, bucket, key, row_length, timeout=DEFAULT_TIMEOUT):
        self._row_length = row_length
        self._client = Session().client('s3')
        self._bucket = bucket
        self._key = key
        self._cache = {}
        self._timeout = timeout

    def clear_cache(self):
        self._cache = {}

    def _get_range(self, start, end):
        key = ':'.join([str(start), str(end)])
        result = self._cache.get(key)
        if key not in self._cache:
            response = self._client.get_object(
                Bucket=self._bucket,
                Range='bytes=%s-%s' % (start, end),
                Key=self._key
            )
            result = []
            read_buffer = response['Body'].read()
            for i in range((end - start) / self._row_length + 1):
                group_id, index = struct.unpack("QI", read_buffer[i * self._row_length:(i + 1) * self._row_length])
                result.append(group_id)
        return key, result

    def prepare(self, indexes):
        results = []
        for index in indexes:
            results.append(gevent.spawn(
                self._get_range, index * self._row_length, (index + 1) * self._row_length - 1))
        gevent.joinall(results, timeout=self._timeout)
        for result in results:
            cache_key, cache_value = result.get()
            self._cache[cache_key] = cache_value

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start
            stop = item.stop
        elif isinstance(item, int):
            start = item
            stop = item + 1
        else:
            raise
        result = self._get_range(start * self._row_length, stop * self._row_length - 1)[1]
        if isinstance(item, int):
            result = result[0]
        return result

    def __len__(self):
        response = self._client.head_object(
            Bucket=self._bucket,
            Key=self._key
        )
        return response['ContentLength'] / 12


def main():
    client = Session().client('s3')
    for i in range(10):
        print get_by_offset(client, (i + 9999) * 12, (i + 10000) * 12 - 1)


if __name__ == '__main__':
    main()
