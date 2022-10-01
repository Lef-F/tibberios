#!/bin/python3
import tibber
from dataclasses import dataclass
from typing import Iterable


@dataclass
class Config:
    filepath: str  # Path to configuration file

    def __post_init__(self) -> None:
        from json import load

        # TODO: Allow for fetching from environment variables
        with open(self.filepath, "r") as f:
            self.config = load(f)
        self.tibber_api_key = self.config["TIBBER_API_KEY"]
        self.database_path = self.config["DATABASE_PATH"]


@dataclass
class History:
    data: Iterable  # Historical tibber API data

    def values(self) -> Iterable[tuple]:
        return [tuple(row.values()) for row in self.data]


class TibberConnector:
    def __init__(self, tibber_api_key: str) -> None:
        self._access_token = tibber_api_key
        self._connection = tibber.Tibber(self._access_token)

    async def get_history(self, resolution: str, records: int) -> Iterable[dict]:
        # TODO: Allow for multiple homes
        async with self._connection.update_info() as info:
            self.home = info.get_homes()[0]
        async with self.home.get_historic_data(
            n_data=records,
            resolution=resolution,
        ) as data:
            history = data
        async with self._connection.close_connection() as closed:
            closed

        print(f"Got {len(history)} records with resolution: {resolution}")
        return history


class Database:
    def __init__(self, filename: str) -> None:
        from sqlite3 import connect

        self._database_path = filename
        self.connection = connect(database=self._database_path)

    def create_table(self) -> None:
        # TODO: Make generic
        create_table = """
            CREATE TABLE IF NOT EXISTS consumption(
                start_time DATE PRIMARY KEY,
                unit_price REAL,
                total_cost REAL,
                cost REAL,
                consumption REAL
            );
        """
        self.connection.execute(create_table)

    def upsert_table(self, values: Iterable[tuple]) -> None:
        # TODO: Make generic
        upsert_table = """
            INSERT INTO consumption(
                start_time
                , unit_price
                , total_cost
                , cost
                , consumption
            )
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(start_time) DO UPDATE SET
                unit_price = excluded.unit_price
                , total_cost = excluded.total_cost
                , cost = excluded.cost
                , consumption = excluded.consumption;
        """

        self.connection.executemany(upsert_table, values)


def main(db_path: str, config_path: str, resolution: str, records: int) -> None:
    print(db_path, config_path, resolution, records)
    config = Config(filepath=config_path)

    if db_path:
        pass
    else:
        db_path = config.database_path
    db = Database(db_path)
    tib = TibberConnector(config.tibber_api_key)
    history = tib.get_history(resolution=resolution, records=records).close()
    data = History(data=history)

    db.create_table()
    db.upsert_table(values=data.values())


if __name__ == "__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    from os import getcwd, path

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--db-path",
        nargs=1,
        required=False,
        help="The path where the SQLite database file is/will be stored. Can be set in DATABASE_PATH key in your config file.",
    )
    parser.add_argument(
        "--config-path",
        nargs=1,
        required=False,
        help="The path to the JSON configuration file for Tibberios",
        default=path.join(getcwd(), "config.json"),
    )
    parser.add_argument(
        "--resolution",
        nargs=1,
        required=False,
        default="HOURLY",
        help="The resolution to fetch records from the Tibber API. (HOURLY, DAILY, WEEKLY, MONTHLY)",
    )
    parser.add_argument(
        "--records",
        nargs=1,
        required=False,
        type=int,
        default=24 * 2,
        help="The number of latest records to fetch from now to the past from the Tibber API.",
    )
    args = parser.parse_args()

    main(
        db_path=args.db_path,
        config_path=args.config_path,
        resolution=args.resolution,
        records=args.records,
    )
