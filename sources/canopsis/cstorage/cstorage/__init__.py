#!/usr/bin/env python
#--------------------------------
# Copyright (c) 2014 "Capensis" [http://www.capensis.com]
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

__version__ = "0.1"

__all__ = ('DataBase', 'Storage')

from cconfiguration import Configurable


class DataBase(Configurable):
	"""
	Abstract class which aims to manage access to a data base.

	Related to a configuration file, it can connects to a database
	depending on several parameters like.

	:param host: db host name
	:type host: basestring
	:param port: db port
	:type port: int
	:param db: db name
	:type db: basestring
	:param auto_connect: auto connect to database when initialised.
	:type auto_connect: bool
	:param backend: default backend to use.

	It provides a DataBaseError for internal errors
	"""

	class DataBaseError(Exception):
		"""
		Errors raised by the DataBase class.
		"""

		pass

	DATABASE = 'DATABASE'
	HOST = 'host'
	PORT = 'port'
	DB = 'db'
	AUTO_CONNECT = 'auto_connect'
	JOURNALING = 'journaling'
	SAFE = 'safe'
	WTIMEOUT = 'wtimeout'
	SSL = 'ssl'
	SSL_KEY = 'ssl_key'
	SSL_CERT = 'ssl_cert'
	USER = 'user'
	PWD = 'pwd'

	PARSING_RULES = {
			DATABASE: {
				HOST: str,
				PORT: int,
				DB: str,
				AUTO_CONNECT: bool,
				JOURNALING: str,
				SAFE: bool,
				WTIMEOUT: int,
				SSL: bool,
				SSL_KEY: str,
				SSL_CERT: str,
				USER: str,
				PWD: str
			}
		}

	ASC = 1  # ASC order
	DESC = -1  # DESC order

	MAX_ATTEMPTS = 3

	def __init__(self, host='localhost', port=0, db='canopsis', auto_connect=True,
		journaling=False, safe=False, wtimeout=100,
		ssl=False, ssl_key=None, ssl_cert=None, user=None, pwd=None,
		*args, **kwargs):
		"""
		:param host: db host name
		:param port: db port
		:param db: db name
		:param auto_connect: auto connect to database when initialised.
		:param backend: default backend to use.
		:param journaling: journaling mode enabling.
		:param safe: ensure writing data.
		:param wtimeout: writing time out in milliseconds.
		:param ssl: ssl mode
		:param ssl_key: ssl keys file.
		:param ssl_cert: ssl certification file.
		:param user: user
		:param pwd: password

		:type host: str
		:type port: int
		:type db: str
		:type auto_connect: bool
		:type backend: str
		:type journaling: bool
		:type safe: bool
		:param wtimeout: int
		:type ssl: bool
		:type ssl_key: str
		:type ssl_cert: str
		:type user: str
		:type pwd: str
		"""

		super(DataBase, self).__init__(*args, **kwargs)

		# initialize instance properties with default values
		self.host = host
		self.port = port
		self.db = db
		self.auto_connect = auto_connect
		self.journaling = journaling
		self.safe = safe
		self.wtimeout = wtimeout
		self.ssl = ssl
		self.ssl_key = ssl_key
		self.ssl_cert = ssl_cert
		self.user = user
		self.pwd = pwd

	def get_parsers_by_option_by_section(self, *args, **kwargs):

		result = super(DataBase, self).get_parsers_by_option_by_section(
			*args, **kwargs)

		result.append(DataBase.PARSING_RULES)

		return result

	def _set_parameters(self, parameters, error_parameters, *args, **kwargs):

		super(DataBase, self)._set_parameters(
			parameters=parameters, error_parameters=error_parameters,
			*args, **kwargs)

		reconnect = False

		host = parameters.get(DataBase.HOST)
		if host is not None:
			self.host = host
			reconnect = True

		port = parameters.get(DataBase.PORT)
		if port is not None:
			self.port = port
			reconnect = True

		db = parameters.get(DataBase.DB)
		if db is not None:
			self.db = db
			reconnect = True

		auto_connect = parameters.get(DataBase.AUTO_CONNECT)
		if auto_connect is not None:
			self.auto_connect = auto_connect
			reconnect = True

		journaling = parameters.get(DataBase.JOURNALING)
		if journaling is not None:
			self.journaling = journaling
			reconnect = True

		safe = parameters.get(DataBase.SAFE)
		if safe is not None:
			self.safe = safe
			reconnect = True

		wtimeout = parameters.get(DataBase.WTIMEOUT)
		if wtimeout is not None:
			self.wtimeout = wtimeout
			reconnect = True

		ssl = parameters.get(DataBase.SSL)
		if ssl is not None:
			self.ssl = ssl
			reconnect = True

		ssl_key = parameters.get(DataBase.SSL_KEY)
		if ssl_key is not None:
			self.ssl_key = ssl_key
			reconnect = True

		ssl_cert = parameters.get(DataBase.SSL_CERT)
		if ssl_cert is not None:
			self.ssl_cert = ssl_cert
			reconnect = True

		user = parameters.get(DataBase.USER)
		if user is not None:
			self.user = user
			reconnect = True

		pwd = parameters.get(DataBase.PWD)
		if pwd is not None:
			self.pwd = pwd
			reconnect = True

		if reconnect and self.auto_connect:
			self.disconnect()
			self.connect()

	def connect(self, *args, **kwargs):
		"""
		Connect this database.

		:raises: NotImplementedError

		.. seealso:: disconnect(self), connected(self)
		"""

		raise NotImplementedError()

	def disconnect(self, *args, **kwargs):
		"""
		Disconnect this database.

		:raises: NotImplementedError
		"""

		raise NotImplementedError()

	def connected(self, *args, **kwargs):
		"""
		:returns: True if this is connected.
		"""

		raise NotImplementedError()

	def get_element(self, id, backend=None, *args, **kwargs):
		"""
		:param id: id of the element to get.
		:type id: basestring

		:return: input id element.
		:rtype: dict

		:raises NotImplementedError:
		"""

		raise NotImplementedError()

	def delete_element(self, id, backend=None, *args, **kwargs):

		raise NotImplementedError()

	def update_element(self, id, element, backend=None, *args, **kwargs):

		raise NotImplementedError()

	def drop(self, backend=None, *args, **kwargs):

		raise NotImplementedError()

	def size(self, criteria=None, backend=None, *args, **kwargs):

		raise NotImplementedError()

from utils import resolve_element


class Storage(DataBase):
	"""
	Manage different kind of storages by data_type.
	"""

	DATA_TYPE = 'data_type'

	def __init__(self, data_type, *args, **kwargs):

		super(Storage, self).__init__(_ready_to_conf=False, *args, **kwargs)

		self.data_type = data_type

		if self.auto_conf:
			self.apply_configuration()

	def get_parsers_by_option_by_section(self, *args, **kwargs):

		result = dict()

		# new parsing rules such as the union of base parsing rules options.
		parsing_rules = {Storage.DATA_TYPE: str}

		# fill it with base parsing rules options
		base_parsing_rules = super(Storage, self).get_parsers_by_option_by_section(
			*args, **kwargs)
		for parsing_rule in base_parsing_rules:
			for section, option_parsing_rules in parsing_rule.iteritems():
				parsing_rules.update(option_parsing_rules)

		# create a new section
		section = self._get_section()

		result = base_parsing_rules + [{section: parsing_rules}]

		return result

	def _get_section(self):

		result = '{0}_{1}'.format(
			self._get_storage_type().upper(), self.data_type.upper())

		return result

	def _get_collection_prefix(self):
		"""
		Protected method to override in order to get collection prefix.
		"""

		raise NotImplementedError()

	def _get_storage_type(self):

		raise NotImplementedError()

	@staticmethod
	def get_storage(storage_type, data_type, *args, **kwargs):

		if isinstance(storage_type, str):
			storage_type = resolve_element(storage_type)

		result = storage_type(data_type=data_type, *args, **kwargs)

		return result

import logging
import time
import sys
import os
import ConfigParser

import gridfs

from pymongo import Connection
from bson import objectid

from pymongo import ASCENDING
from pymongo import DESCENDING

from caccount import caccount
from crecord import crecord
from cfile import cfile

from operator import itemgetter

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read(os.path.expanduser('~/etc/cstorage.conf'))


class cstorage(object):
	def __init__(self, account, namespace='object', logging_level=logging.ERROR,
		mongo_host="127.0.0.1", mongo_port=27017, mongo_db='canopsis',
		mongo_autoconnect=True, groups=[], mongo_safe=True):

		try:
			self.mongo_host = CONFIG.get("master", "host")
		except:
			self.mongo_host = mongo_host

		try:
			self.mongo_port = CONFIG.getint("master", "port")
		except:
			self.mongo_port = mongo_port

		try:
			self.mongo_db = CONFIG.get("master", "db")
		except:
			self.mongo_db = mongo_db

		self.mongo_safe = mongo_safe

		self.account = account
		self.root_account = caccount(user="root", group="root")

		self.namespace = namespace
		self.backend = None

		self.logger = logging.getLogger('cstorage')
		self.logger.setLevel(logging_level)

		self.gridfs_namespace = "binaries"

		self.logger.debug("Object initialised.")

		self.backend = {}
		self.connected = False

		if mongo_autoconnect:
			self.connect()

	def clean_id(self, _id):
		try:
			int(_id, 16)
			return objectid.ObjectId(_id)
		except:
			return _id

	def make_mongofilter(self, account):
		Read_mfilter = {}
		Write_mfilter = {}

		if account._id != "account.root" and account.group != "group.CPS_root" \
			and not 'group.CPS_root' in account.groups:
			Read_mfilter = {'$or': [
				{'aaa_owner': account._id, 'aaa_access_owner': 'r'},
				{'aaa_group': account.group, 'aaa_access_group': 'r'},
				{'aaa_group': {'$in': account.groups}, 'aaa_access_group': 'r'},
				{'aaa_admin_group': account.group},
				{'aaa_admin_group': {'$in': account.groups}},
				{'aaa_access_unauth': 'r'}
			]}

			Write_mfilter = {'$or': [
				{'aaa_owner': account._id, 'aaa_access_owner': 'w'},
				{'aaa_group': account.group, 'aaa_access_group': 'w'},
				{'aaa_group': {'$in': account.groups}, 'aaa_access_group': 'w'},
				{'aaa_admin_group': account.group},
				{'aaa_admin_group': {'$in': account.groups}},
				{'aaa_access_unauth': 'w'}
			]}

			if account.user != "anonymous":
				Read_mfilter['$or'].append({'aaa_access_other': 'r'})
				Write_mfilter['$or'].append({'aaa_access_other': 'w'})

		return (Read_mfilter, Write_mfilter)

	def connect(self):
		if self.connected:
			return True

		self.conn = Connection(self.mongo_host, self.mongo_port, safe=True)
		self.db = self.conn[self.mongo_db]

		try:
			self.gridfs_namespace = CONFIG.get("master", "gridfs_namespace")
		except:
			pass

		self.fs = gridfs.GridFS(self.db, self.gridfs_namespace)

		self.connected = True

		self.logger.debug("Connected %s" % id(self))

	def disconnect(self):
		if self.connected:
			self.conn.fsync()
			del self.conn
			self.connected = False

	def check_connected(self):
		"""
		Check if self is connected to db.
		"""
		if not self.connected:
			raise Exception("CSTORAGE is not connected %s" % id(self))

	def get_backend(self, namespace=None):
		self.check_connected()

		if not namespace:
			namespace = self.namespace

		try:
			backend = self.backend[namespace]
			self.logger.debug("Use %s collection" % namespace)

			return backend
		except:
			self.backend[namespace] = self.db[namespace]
			self.logger.debug("Connected to %s collection." % namespace)
			return self.backend[namespace]

	def update(self, _id, data, namespace=None, account=None):
		self.check_connected()

		if not isinstance(data, dict):
			raise Exception('Invalid data, must be a dict ...')

		data['crecord_write_time'] = int(time.time())

		# Check if record exist
		count = self.count(
			{'_id': _id}, namespace=namespace, account=account, for_write=True)
		if count:
			backend = self.get_backend(namespace)
			backend.update(
				{'_id': self.clean_id(_id)}, {"$set": data}, safe=True, w=1)
		else:
			raise KeyError("'%s' not found ..." % _id)

	def put(self, _record_or_records, account=None, namespace=None, mset=False):
		self.check_connected()

		if not account:
			account = self.account

		records = []
		return_ids = []

		if isinstance(_record_or_records, crecord):
			records = [_record_or_records]
		elif isinstance(_record_or_records, list):
			records = _record_or_records
		else:
			self.logger.error("Invalid record type")

		backend = self.get_backend(namespace)

		self.logger.debug("Put %s record(s) ..." % len(records))
		for record in records:
			_id = record._id

			if not record.owner:
				record.chown(account.user)

			if not record.group:
				record.chgrp(account.group)

			access = False

			new_record = True
			oldrecord = None
			if _id:
				try:
					oldrecord = self.get(_id, namespace=namespace, account=self.root_account)
					new_record = False
				except:
					pass

			if not new_record:
				self.logger.debug("Check rights of %s" % _id)
				if account.user == 'root':
					access = True
				else:
					access = oldrecord.check_write(account)
			else:
				## New record
				## Todo: check if account have right to create record ...
				access = True

			if not access:
				self.logger.error("Puts: Access denied ...")
				raise ValueError("Access denied")

			if new_record:
				## Insert new record
				self.logger.debug("Insert new record")

				try:
					## Check if record have binary and store in grid fs
					if record.binary:
						record.data['binary_id'] = self.put_binary(
							record.binary, record.data['file_name'], record.data['content_type'])

					record.write_time = int(time.time())
					data = record.dump()
					data['crecord_creation_time'] = record.write_time

					## Del it if 'None'
					if not data['_id']:
						del data['_id']

					if not _id:
						backend.insert(data, safe=self.mongo_safe, w=1)
					else:
						backend.update(
							{'_id': _id}, data, safe=self.mongo_safe, upsert=True, w=1)

					self.logger.debug("Successfully inserted (_id: '%s')" % _id)

				except Exception as err:
					self.logger.error("Impossible to store !\nReason: %s" % err)
					self.logger.debug("Record dump:\n%s" % record.dump())
					raise ValueError("Impossible to insert (%s)" % err)

				record._id = _id
				return_ids.append(_id)
			else:
				## Update record
				self.logger.debug("Update record '%s'" % _id)

				try:
					## Check if record have binary and store in grid fs
					if record.binary:
						record.data['binary_id'] = self.put_binary(
							record.binary, record.data['file_name'], record.data['content_type'])

					record.write_time = int(time.time())
					data = record.dump()

					del data['_id']
					_id = self.clean_id(_id)

					if mset:
						ret = backend.update(
							{'_id': _id}, {"$set": data}, upsert=True, safe=self.mongo_safe, w=1)
					else:
						ret = backend.update(
							{'_id': _id}, data, upsert=True, safe=self.mongo_safe, w=1)

					if self.mongo_safe:
						if ret['updatedExisting']:
							self.logger.debug("Successfully updated (_id: '%s')" % _id)
						else:
							self.logger.debug("Successfully saved (_id: '%s')" % _id)

				except Exception as err:
					self.logger.error("Impossible to store !\nReason: %s" % err)
					self.logger.debug("Record dump:\n%s" % record.dump())
					raise ValueError("Impossible to store (%s)" % err)

				record._id = _id
				return_ids.append(_id)

		if len(return_ids) == 1:
			return return_ids[0]
		else:
			return return_ids
	'''
	#warning : not tested
	def recursive_put(self, record,depth=0, account=None, namespace=None):
		depth += 1

		children_ids = []

		for child in record.children:
			self.recursive_put(child,depth,account=account,namespace=namespace)
			children_ids.append(child._id)

		record.children = children_ids
		self.put(record,account=None, namespace=None)
	'''

	def find_one(self, *args, **kargs):
		return self.find(one=True, *args, **kargs)

	def count(self, *args, **kargs):
		return self.find(count=True, *args, **kargs)

	def find(self,
		mfilter={}, mfields=None, account=None, namespace=None, one=False,
		count=False, sort=None, limit=0, offset=0, for_write=False,
		ignore_bin=True, raw=False, with_total=False):
		self.check_connected()

		if not account:
			account = self.account

		if isinstance(sort, basestring):
			sort = [(sort, 1)]

		# Clean Id
		if mfilter.get('_id', None):
			mfilter['_id'] = self.clean_id(mfilter['_id'])

		if one:
			sort = [('timestamp', -1)]

		self.logger.debug("Find records from mfilter")

		(Read_mfilter, Write_mfilter) = self.make_mongofilter(account)

		if for_write:
			if Write_mfilter:
				mfilter = {'$and': [mfilter, Write_mfilter]}
		else:
			if Read_mfilter:
				mfilter = {'$and': [mfilter, Read_mfilter]}

		self.logger.debug(" + fields : %s" % mfields)
		self.logger.debug(" + mfilter: %s" % mfilter)

		backend = self.get_backend(namespace)

		if one:
			raw_records = backend.find_one(
				mfilter, fields=mfields, safe=self.mongo_safe)
			if raw_records:
				raw_records = [raw_records]
			else:
				raw_records = []
		else:
			if sort is None:
				raw_records = backend.find(
					mfilter, fields=mfields, safe=self.mongo_safe, start=offset, limit=limit)
			else:
				raw_records = backend.find(mfilter, fields=mfields, safe=self.mongo_safe)

			total = raw_records.count()

			# process limit, offset and sort independently of pymongo
			# because sort does not use index
			if count:
				return total

			raw_records = list(raw_records)

			if sort is not None:
				for s in sort:
					key = s[0]
					desc = s[1] == -1
					raw_records = sorted(raw_records, key=itemgetter(key), reverse=desc)

				# and get a sub list of raw_records
				if limit != 0 and offset != 0:
					raw_records = raw_records[offset: offset + limit]
				elif limit != 0:
					raw_records = raw_records[:limit]
				elif offset != 0:
					raw_records = raw_records[offset:]

		records = []

		if not mfields:
			for raw_record in raw_records:
				try:
					# Remove binary (base64)
					if ignore_bin and raw_record.get('media_bin', None):
						del raw_record['media_bin']

					if not raw:
						records.append(crecord(raw_record=raw_record))
					else:
						records.append(raw_record)

				except Exception as err:
					## Not record format ..
					self.logger.error("Impossible parse record ('%s') !" % err)
		else:
			records = raw_records

		self.logger.debug("Found %s record(s)" % len(records))

		if one:
			if len(records) > 0:
				return records[0]
			else:
				return None
		else:
			if with_total:  # returns the couple of records, total
				return records, total

			return records

	def get(self,
		_id_or_ids, account=None, namespace=None, mfields=None, ignore_bin=True):
		self.check_connected()

		if not account:
			account = self.account

		dolist = False
		if isinstance(_id_or_ids, list):
			_ids = _id_or_ids
			dolist = True
		else:
			_ids = [_id_or_ids]

		backend = self.get_backend(namespace)

		self.logger.debug(" + Get record(s) '%s'" % _ids)
		if not len(_ids):
			self.logger.debug("   + No ids")
			return []

		self.logger.debug("   + fields : %s" % mfields)

		self.logger.debug("   + Clean ids")
		_ids = [self.clean_id(_id) for _id in _ids]

		#Build basic filter
		(Read_mfilter, Write_mfilter) = self.make_mongofilter(account)

		if len(_ids) == 1:
			mfilter = {'_id': _ids[0]}
		else:
			mfilter = {'_id': {'$in': _ids}}

		mfilter = {'$and': [mfilter, Read_mfilter]}

		#self.logger.debug("   + mfilter: %s" % mfilter)
		records = []
		try:
			if len(_ids) == 1:
				raw_record = backend.find_one(
					mfilter, fields=mfields, safe=self.mongo_safe)

				# Remove binary (base64)
				if ignore_bin and raw_record and raw_record.get('media_bin', None):
					del raw_record['media_bin']

				if raw_record and mfields:
					records.append(raw_record)
				elif raw_record:
					records.append(crecord(raw_record=raw_record))
			else:
				raw_records = backend.find(mfilter, fields=mfields, safe=self.mongo_safe)

				if mfields:
					records = [raw_record for raw_record in raw_records]
				else:
					for raw_record in raw_records:
						# Remove binary (base64)
						if ignore_bin and raw_record.get('media_bin', None):
							del raw_record['media_bin']

						records.append(crecord(raw_record=raw_record))

		except Exception as err:
			self.logger.error("Impossible get record '%s' !\nReason: %s" % (_ids, err))

		self.logger.debug(" + Found %s records" % len(records))
		if not len(records):
			raise KeyError("'%s' not found ..." % _ids)

		if len(_ids) == 1 and not dolist:
			return records[0]
		else:
			return records

	def remove(self, _id_or_ids, account=None, namespace=None):
		self.check_connected()

		if not account:
			account = self.account

		_ids = []

		if isinstance(_id_or_ids, crecord):
			_ids = [_id_or_ids._id]
		elif isinstance(_id_or_ids, list):
			if len(_id_or_ids) > 0:
				if isinstance(_id_or_ids[0], crecord):
					for record in _id_or_ids:
						_ids.append(record._id)
				else:
					_ids = _id_or_ids
		else:
			_ids = [_id_or_ids]

		backend = self.get_backend(namespace)

		self.logger.debug("Remove %s record(s) ..." % len(_ids))
		for _id in _ids:
			self.logger.debug(" + Remove record '%s'" % _id)

			oid = self.clean_id(_id)
			if account.user == 'root':
				access = True
			else:
				try:
					oldrecord = self.get(oid, account=account)
				except Exception as err:
					raise ValueError("Access denied or id not found")

				access = oldrecord.check_write(account)

			if access:
				try:
					backend.remove({'_id': oid}, safe=self.mongo_safe)
				except Exception as err:
					self.logger.error(
						"Impossible remove record '%s' !\nReason: %s" % (_id, err))

				self.logger.debug(" + Success removed")
			else:
				self.logger.error("Remove: Access denied ...")
				raise ValueError("Access denied ...")

	def map_reduce(
		self, mfilter_or_ids, mmap, mreduce, account=None, namespace=None):
		self.check_connected()

		if not account:
			account = self.account

		if isinstance(mfilter_or_ids, dict):
			# mfilter
			mfilter = mfilter_or_ids
		elif isinstance(mfilter_or_ids, list):
			#ids
			mfilter = {'_id': {'$in': mfilter_or_ids}}
		else:
				self.logger.error("Invalid filter")
				raise ValueError("Invalid filter")

		backend = self.get_backend(namespace)

		(Read_mfilter, Write_mfilter) = self.make_mongofilter(account)
		#mfilter = dict(mfilter.items() + Read_mfilter.items())
		if Read_mfilter != {}:
			mfilter = {'$and': [mfilter, Read_mfilter]}

		output = {}
		if backend.find(mfilter).count() > 0:
			result = backend.map_reduce(mmap, mreduce, "mapreduce", query=mfilter)
			for doc in result.find():
				output[doc['_id']] = doc['value']
		else:
			self.logger.debug("Nor record matching filter")

		return output

	def drop_namespace(self, namespace):
		self.check_connected()

		self.db.drop_collection(namespace)

	def get_namespace_size(self, namespace=None):
		self.check_connected()

		if not namespace:
			namespace = self.namespace

		try:
			return self.db.command("collstats", namespace)['size']
		except:
			return 0

	def recursive_get(self, record, depth=0, account=None, namespace=None):
		self.check_connected()

		depth += 1
		childs = record.children
		if len(childs) == 0:
			return

		record.children = []

		for child in childs:
			# HACK: fix root_directory in UI !!!
			try:
				rec = self.get(child, account=account, namespace=namespace)
				self.recursive_get(rec, depth, account=account, namespace=namespace)
				record.children.append(rec)
			except Exception as err:
				self.logger.debug(err)

	def get_record_childs(self, record, account=None, namespace=None):
		self.check_connected()

		child_ids = record.children
		if len(child_ids) == 0:
			return []

		records = []
		for _id in child_ids:
			records.append(self.get(str(_id), account=account, namespace=namespace))

		return records

	def print_record_tree(self, record, depth=0):
		self.check_connected()

		depth += 1

		childs = record.children_record
		if len(childs) == 0:
			return

		if depth == 1:
			print("|-> " + str(record.name))

		for child in childs:

			prefix = ""
			for i in range(depth):
				prefix += "  "
			prefix += "|"
			for i in range(depth):
				prefix += "--"
			print(prefix + "> " + str(child.name))

			self.print_record_tree(child, depth)

	def get_childs_of_parent(self, record_or_id, rtype=None, account=None):
		self.check_connected()

		if isinstance(record_or_id, crecord):
			_id = record_or_id._id
		else:
			_id = record_or_id

		mfilter = {'parent': _id}

		if rtype:
			mfilter['crecord_type'] = rtype

		return self.find(mfilter, account=account)

	def get_parents_of_child(self, record_or_id, rtype=None, account=None):
		self.check_connected()

		if isinstance(record_or_id, crecord):
			_id = record_or_id._id
		else:
			_id = record_or_id

		mfilter = {'child': _id}

		if rtype:
			mfilter['crecord_type'] = rtype

		return self.find(mfilter, account=account)
	'''
	def add_children(self, parent_record, child_record, autosave=True):
		_id = child_record._id

		if autosave:
			if not _id:
				child_record.save()
			if not parent_record._id:
				parent_record.save()

		if not _id or not parent_record._id:
			raise ValueError("You must save all records before this operation ...")

		if str(_id) not in parent_record.children:
			parent_record.children.append(str(_id))
			child_record.parent.append(str(parent_record._id))
			if autosave:
				parent_record.save()
				child_record.save()

	def remove_children(self, parent_record, child_record, autosave=True):
		_id = child_record._id

		if autosave:
			if not _id:
				child_record.save()
			if not parent_record._id:
				parent_record.save()

		if not _id or not parent_record._id:
			raise ValueError("You must save all records before this operation ...")

		if str(_id) in parent_record.children:
			parent_record.children.remove(str(_id))
			child_record.parent.remove(str(parent_record._id))
			if autosave:
				parent_record.save()
				child_record.save()
	'''
	def is_parent(self, parent_record, child_record):
		self.check_connected()

		if str(child_record._id) in parent_record.children:
			return True
		else:
			return False

	def put_binary(self, data, file_name, content_type):
		self.check_connected()

		bin_id = self.fs.put(data, filename=file_name, content_type=content_type)
		return bin_id

	def get_binary(self, _id):

		self.check_connected()

		cursor = self.fs.get(_id)

		return cursor.read()

	def remove_binary(self, _id):
		self.check_connected()

		try:
			self.fs.delete(_id)
		except Exception, err:
			self.logger.error('Error when remove binarie', err)

	def check_binary(self, _id):
		self.check_connected()

		return self.fs.exists(_id)

	def __del__(self):
		self.logger.debug("Object deleted. (namespace: %s)" % self.namespace)

#####
#       docs = doc_or_docs
#        return_one = False
#        if isinstance(docs, dict):
#            return_one = True
#            docs = [docs]
##################

## Cache storage
STORAGES = {}


def get_storage(namespace='object', account=None, logging_level=logging.INFO):
	global STORAGES
	try:
		return STORAGES[namespace]

	except KeyError:
		if not account:
			account = caccount()

		STORAGES[namespace] = cstorage(
			account, namespace=namespace, logging_level=logging_level)
		return STORAGES[namespace]