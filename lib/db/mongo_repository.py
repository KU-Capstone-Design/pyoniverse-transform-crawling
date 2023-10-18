import os
from typing import Any, List, Mapping, Optional

from overrides import override
from pymongo import MongoClient, ReadPreference
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

from lib.interface.repository_ifs import RepositoryIfs


class MongoRepository(RepositoryIfs):
    @override
    def _connect(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: MongoClient
        """
        self.logger.info("Connecting...")
        try:
            client: MongoClient = MongoClient(os.getenv("MONGO_URI"))
            client.admin.command("ping")
        except ConnectionFailure:
            self.logger.error("Can't connect to Server")
            exit(1)  # 종료
        else:
            self.logger.info("Connect to Mongo Client")
            return client

    @property
    def read_db(self) -> Database:
        return self._client.get_database(
            self._db_name, read_preference=ReadPreference.SECONDARY_PREFERRED
        )

    @override
    def find_one(
        self,
        rel_name: str,
        filter: Mapping[str, Any] = None,
        project: Mapping[str, bool] = None,
        hint: Mapping[str, int] = None,
        *args,
        **kwargs,
    ) -> Optional[Mapping[str, Any]]:
        if hint:
            hint = [(k, v) for k, v in hint.items()]
        data = self.read_db[rel_name].find_one(
            filter=filter, projection=project, hint=hint
        )
        if not data:
            self.logger.debug(f"{rel_name}: {filter} Not Found")
        return data

    @override
    def find(
        self,
        rel_name: str,
        filter: Mapping[str, Any] = None,
        project: Mapping[str, bool] = None,
        hint: Mapping[str, int] = None,
        order_by: Mapping[str, int] = None,
        limit: int = None,
        *args,
        **kwargs,
    ) -> List[Mapping[str, Any]]:
        if hint:
            hint = [(k, v) for k, v in hint.items()]
        if order_by:
            order_by = [(k, v) for k, v in hint.items()]
        data = list(
            self.read_db[rel_name]
            .find(filter=filter, projection=project)
            .sort(order_by)
            .limit(limit)
            .hint(hint)
        )
        if not data:
            self.logger.debug(f"{rel_name}: {filter} Not Found")
        return data

    @override
    def distinct(
        self,
        rel_name: str,
        attr_name: str,
        filter: Mapping[str, Any] = None,
        *args,
        **kwargs,
    ) -> List[Any]:
        data = self.read_db[rel_name].distinct(key=attr_name, filter=filter)
        if not data:
            self.logger.debug(f"{rel_name}: {filter} Not Found")
        return data
