import sqlite3
import os

from queries import Query
from helpers.logger import Logger

class Database:
    def __init__(self, filename: str, log_file_path: str):
        self.__logger: Logger = Logger(log_file_path)
        self.__logger.log("Starting Database")
        self.__filename: str = os.path.abspath(filename)
        self.__connection: None | sqlite3.Connection = None
        self.__cursor: None | sqlite3.Cursor = None
        self.__connect()

    def __del__(self):
        self.__disconnect()
        self.__logger.log("Ending database")

    def __connect(self) -> None:
        self.__logger.log("Connecting to database")
        try:
            self.__connection = sqlite3.connect(self.__filename)
            self.__logger.log("SQLITE version: {}".format(sqlite3.sqlite_version))
        except sqlite3.Error as e:
            self.__logger.log("SQLITE ERROR: {}: {}".format(type(e).__name__, str(e)))

        if self.__connection is not None:
            try: 
                self.__connection.row_factory = sqlite3.Row
                self.__cursor = self.__connection.cursor()
            except sqlite3.Error as e:
                self.__logger.log("SQLITE ERROR: {}: {}".format(type(e).__name__, str(e)))

        if self.__connection is not None and self.__cursor is not None:
            self.__logger.log("Successfully connected to database")
        else:
            self.__logger.log("Failed to connect to database")

    def run_query(self, query: Query) -> list[sqlite3.Row]:
        assert (self.__connection is not None)
        assert (self.__cursor is not None)
        self.__logger.log("Running query:\n{query}".format(query = query))
        self.__cursor.execute(query)
        self.__connection.commit()
        self.__logger.log("Query executed, fetching results")
        results: list[sqlite3.Row] = self.__cursor.fetchall()
        if len(results) > 0:
            columns: list[str] = results[0].keys()
            self.__logger.log("Result columns:\n{columns}".format(columns = columns))
            results_string: str = str()
            for result in results:
                results_string += str(list(result))
                results_string += "\n"
            self.__logger.log("Results fetched:\n{results}".format(results = results_string))
        else:
            self.__logger.log("No results")

        return results

    def run_query_insert_blob(self, query: Query, blobs: tuple[bytes, ...]) -> list[sqlite3.Row]:
        assert (self.__connection is not None)
        assert (self.__cursor is not None)
        assert (isinstance(blobs, tuple))
        for blob in blobs:
            assert (isinstance(blob, bytes))
        self.__logger.log("Running blobs insert query:\n{query}".format(query = query))
        self.__cursor.execute(query, blobs)
        self.__connection.commit()
        self.__logger.log("Blobs insert query executed, fetching results")
        results: list[sqlite3.Row] = self.__cursor.fetchall()
        if len(results) > 0:
            columns: list[str] = results[0].keys()
            self.__logger.log("Result columns:\n{columns}".format(columns = columns))
            results_string: str = str()
            for result in results:
                results_string += str(list(result))
                results_string += "\n"
            self.__logger.log("Results fetched:\n{results}".format(results = results_string))
        else:
            self.__logger.log("No results")

        return results


    def get_last_row_id(self) -> int | None:
        assert (self.__connection is not None)
        assert (self.__cursor is not None)
        row_id: int | None = self.__cursor.lastrowid

        return row_id

    def __disconnect(self) -> None:
        self.__logger.log("Disconnecting from database")
        if self.__cursor is not None:
            self.__cursor.close()
        if self.__connection is not None:
            self.__connection.commit()
            self.__connection.close()
        self.__logger.log("Disconnected from database")
