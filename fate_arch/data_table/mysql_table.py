#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import typing

import pymysql

from arch.api.utils.conf_utils import get_base_config
from fate_arch.common.profile import log_elapsed
from fate_arch.data_table.base import Table
from fate_arch.data_table.store_type import StoreEngine
from fate_arch.common import WorkMode


# noinspection SpellCheckingInspection,PyProtectedMember,PyPep8Naming
class MysqlTable(Table):
    def __init__(self,
                 mode: typing.Union[int, WorkMode] = get_base_config('work_mode', 0),
                 persistent_engine: str = StoreEngine.MYSQL,
                 partitions: int = 1,
                 name: str = None,
                 namespace: str = None,
                 address=None,
                 **kwargs):
        self._partitions = partitions
        self._storage_engine = persistent_engine
        self._address = address
        self._name = name
        self._namespace = namespace
        self._mode = mode
        '''
        database_config
        {
            'user': 'root',
            'passwd': 'fate_dev',
            'host': '127.0.0.1',
            'port': 3306
        }
        '''
        try:
            self.con = pymysql.connect(host=self._address.host,
                                       user=self._address.user,
                                       passwd=self._address.passwd,
                                       port=self._address.port,
                                       db=self._address.db)
            self.cur = self.con.cursor()
        except:
            raise Exception("DataBase connect error,please check the db config:host {}, user {}, passwd {}, port {}, db {}".format(self._address.host, self._address.user, self._address.passwd, self._address.port, self._address.db))

    def execute(self, sql, select=True):
        self.cur.execute(sql)
        if select:
            while True:
                result = self.cur.fetchone()
                if result:
                    yield result
                else:
                    break
        else:
            result = self.cur.fetchall()
            return result

    def get_partitions(self):
        return self._partitions

    def get_name(self):
        return self._name

    def get_namespace(self):
        return self._namespace

    def get_storage_engine(self):
        return self._storage_engine

    def get_address(self):
        return self._address

    @log_elapsed
    def collect(self, **kwargs) -> list:
        sql = 'select * from {}'.format(self._name)
        data = self.execute(sql)
        return data

    def save_as(self, name, namespace, partition=None, schema_data=None, **kwargs):
        pass

    def put_all(self, kv_list, **kwargs):
        pass

    def destroy(self):
        super().destroy()
        sql = 'drop table {}'.format(self._name)
        return self.execute(sql)

    @log_elapsed
    def count(self, **kwargs):
        return self.get_schema(_type='count')

    def close(self):
        self.con.close()
