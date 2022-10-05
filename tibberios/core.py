from dataclasses import dataclass
from pprint import pprint
from collections import Counter

import tibber
from aiohttp import ClientSession


@dataclass
class Config:
    filepath: str  # Path to configuration file

    def __post_init__(self) -> None:
        from json import load

        # TODO: Allow for fetching from environment variables
        with open(self.filepath, "r") as f:
            self.config = load(f)
        self.tibber_api_key = self._try_fetch_config_key("TIBBER_API_KEY")
        self.database_path = self._try_fetch_config_key("DATABASE_PATH")

    def _try_fetch_config_key(self, key_name: str) -> str:
        try:
            return self.config[key_name]
        except:
            return None


@dataclass
class PriceData:
    historical_data: list[dict]  # Historical tibber API data
    current_data: dict[str, float]  # Today, current and tomorrow tibber API price data

    def __post_init__(self) -> None:
        self.price_table = self._convert_values()

    def _convert_values(self) -> list[tuple]:
        # assuming that historical values have the following schema:
        # (start_time, unit_price, total_cost, cost, consumption)
        # we model current values to be (start_time, unit_price, None, None, None)
        converted_current_data = []
        for start_time, unit_price in self.current_data.items():
            converted_current_data.append(
                (
                    start_time,
                    unit_price,
                    None,
                    None,
                    None,
                )
            )

        converted_historical_data = [
            tuple(row.values()) for row in self.historical_data
        ]
        converted_data = converted_current_data + converted_historical_data
        return self._keep_richest_duplicates(converted_data)

    def _keep_richest_duplicates(self, data: list[tuple]) -> list[tuple]:
        # extract start_times
        start_times = [row[0] for row in data]
        # get a count of occurrences to identify duplicates
        count_occurrences = dict(Counter(start_times))
        # filter to keep only duplicates
        duplicates = {
            start_time: {"missing_data": -1, "row": None}
            for start_time, occurrences in count_occurrences.items()
            if occurrences > 1
        }

        # find the row indices with duplicates with the fewest missing data points
        duplicates_tracker = {}
        row_num = 0
        for row in data:
            if row[0] in duplicates:
                missing_data = len([True for value in row if not value is None])
                if row[0] in duplicates_tracker.keys():
                    if duplicates_tracker[row[0]]["missing_data"] > missing_data:
                        duplicates_tracker[row[0]]["missing_data"] = missing_data
                        duplicates_tracker[row[0]]["row"] = row_num
                else:
                    duplicates_tracker[row[0]] = {
                        "missing_data": missing_data,
                        "row": row_num,
                    }

            row_num += 1

        # collect the richest rows from the duplicate data
        rich_data = []
        for _, info in duplicates_tracker.items():
            rich_data.append(data[info["row"]])

        # consolidate the rest of the data that were not duplicates
        non_duplicates = set(start_times) - set(duplicates.keys())
        for row in data:
            if row[0] in non_duplicates:
                rich_data.append(row)
        return rich_data


class TibberConnector:
    def __init__(self, tibber_api_key: str) -> None:
        self._access_token = tibber_api_key

    async def get_price_data(self, resolution: str, records: int) -> PriceData:
        # TODO: Allow for multiple homes
        async with ClientSession() as session:
            tibber_connection = tibber.Tibber(self._access_token, websession=session)
            await tibber_connection.update_info()
            home = tibber_connection.get_homes()[0]

            self.history = await home.get_historic_data(
                n_data=records,
                resolution=resolution,
            )

            await home.update_price_info()
            self.current_prices = home.price_total
        print(
            f"Got {len(self.history)} past records and {len(self.current_prices)} records of current prices with resolution: {resolution}"
        )
        self.price_data = PriceData(
            historical_data=self.history, current_data=self.current_prices
        )
        return self.price_data


class Database:
    def __init__(self, filename: str) -> None:
        from sqlite3 import connect

        self._database_path = filename
        self.connection = connect(database=self._database_path)

    def __del__(self) -> None:
        if hasattr(self, "connection") and self.connection:
            self.close()

    def create_table(self) -> None:
        # TODO: Make generic
        query = """
            CREATE TABLE IF NOT EXISTS consumption(
                start_time DATE PRIMARY KEY,
                unit_price REAL,
                total_cost REAL,
                cost REAL,
                consumption REAL
            );
        """
        cursor = self.connection
        cursor = cursor.execute(query)
        self.connection.commit()

    def show_latest_data(self, limit: int = 10) -> None:
        # TODO: Make generic
        query = f"""
            SELECT *
            FROM consumption
            ORDER BY start_time DESC
            LIMIT {limit};
        """
        cursor = self.connection
        cursor = cursor.execute(query)
        pprint(cursor.fetchall())

    def upsert_table(self, values: list[tuple]) -> None:
        # TODO: Make generic
        query = """
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

        cursor = self.connection
        cursor.executemany(query, values)
        self.connection.commit()

    def delete_null_rows(self) -> None:
        # TODO: Make generic
        query = """
            DELETE
            FROM consumption
            WHERE start_time IS NULL
                OR trim(start_time) = '';
        """
        cursor = self.connection
        cursor.execute(query)
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
