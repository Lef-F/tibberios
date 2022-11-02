from .core import Config, Database, TibberConnector
from .visualization import GenerateViz
from datetime import datetime
from pprint import pprint


def setup(config_path: str, db_path: str, verbose: bool = False) -> Config:
    config = Config(filepath=config_path)

    if db_path:
        config.database_path = db_path

    print(f"Starting at {datetime.now().isoformat()}")
    if verbose:
        print(f"The database path is: {db_path}")
        print(f"The config path is: {config_path}")
    return config


async def main(
    db_path: str,
    config_path: str,
    resolution: str,
    records: int,
    verbose: bool,
) -> None:

    config = setup(config_path=config_path, db_path=db_path, verbose=verbose)

    if verbose:
        print(f"Fetching {records} in {resolution} resolution")

    db = Database(config.database_path)
    tib = TibberConnector(config.tibber_api_key)
    price_data = await tib.get_price_data(resolution=resolution, records=records)

    tbl_name = "consumption"
    columns = {
        "start_time": "DATE PRIMARY KEY",
        "unit_price": "REAL",
        "total_cost": "REAL",
        "cost": "REAL",
        "consumption": "REAL",
    }
    pk = "start_time"

    db.create_table(name=tbl_name, cols_n_types=columns)
    if verbose:
        print("Consumption table created")
    db.upsert_table(
        name=tbl_name, columns=columns.keys(), values=price_data.price_table, pk=pk
    )
    if verbose:
        print("Cleaning rows with NULL or empty time values")
    db.delete_null_rows(name=tbl_name, pk=pk)
    if verbose:
        print("Consumption values upserted")
        print("Latest 10 consumption values:")
        pprint(db.get_latest_data(name=tbl_name, order="start_time"))

    db.close()

    print(f"Ended at {datetime.now().isoformat()}")


def generate_vis(args) -> None:
    config = setup(
        config_path=args.config_path, db_path=args.db_path, verbose=args.verbose
    )
    db = Database(config.database_path)

    print(f"Generating visualization at {args.output}")
    gv = GenerateViz(db)
    # TODO: allow user to set comparison
    # 4kWh ~ the cost of showering for 10 minutes at 40C
    gv.create_visualization(filepath=args.output, comparison_kwh=4, decimals=0)

    db.close()
    print(f"Ended at {datetime.now().isoformat()}")


def update_display(args) -> None:
    print(f"Started at {datetime.now().isoformat()}")
    if update_display:
        from .display import update

        update(args.file)
    print(f"Ended at {datetime.now().isoformat()}")


def run() -> None:
    from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
    from asyncio import run as async_run
    from sys import exit

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config-path",
        type=str,
        required=True,
        help="The path to the JSON configuration file for Tibberios",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        required=False,
        help="The path where the SQLite database file is/will be stored. Can be set in DATABASE_PATH key in your config file.",
    )
    parser.add_argument(
        "--resolution",
        type=str,
        required=False,
        default="HOURLY",
        help="The resolution to fetch records from the Tibber API. (HOURLY, DAILY, WEEKLY, MONTHLY)",
    )
    parser.add_argument(
        "--records",
        type=int,
        required=False,
        default=24 * 2,
        help="The number of latest records to fetch from now to the past from the Tibber API.",
    )
    parser.add_argument(
        "--verbose",
        required=False,
        default=False,
        action="store_true",
        help="Show more information from the process.",
    )

    subparsers = parser.add_subparsers(
        title="Visualize",
        description="Commands to visualize and display electricity prices.",
    )
    vis_parser = subparsers.add_parser(
        name="vis", help="Generate visualization of prices for today and tomorrow."
    )
    vis_parser.add_argument(
        "output",
        type=str,
        help="Image file output path.",
    )
    vis_parser.set_defaults(func=generate_vis)

    display_parser = subparsers.add_parser(
        name="display",
        help="Update the external display. Currently only the Waveshare 7.5 inch V2 e-Paper Display is supported.",
    )
    display_parser.add_argument(
        "file",
        type=str,
        help="Path to image file to display.",
    )
    display_parser.set_defaults(func=update_display)

    args = parser.parse_args()

    if hasattr(args, "func"):
        # run requested subcommand
        args.func(args)
    else:
        # run tibber API data update
        async_run(
            main(
                db_path=args.db_path,
                config_path=args.config_path,
                resolution=args.resolution,
                records=args.records,
                verbose=args.verbose,
            )
        )
    exit(0)


if __name__ == "__main__":
    run()
