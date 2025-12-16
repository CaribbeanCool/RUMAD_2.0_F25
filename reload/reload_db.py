import argparse
from drop_tables import drop_all_tables
from load_tables import load_data


def reload_database(
    action: str = "both",
    yes: bool = False,
    sql_filepath: str = "create_tables.sql",
):
    """
    Unified function to drop and/or load database tables.

    :param action: Action to perform - 'drop', 'load', or 'both'
    :param yes: Skip confirmation prompts
    :param sql_filepath: Path to SQL schema file
    """
    if action in ("drop", "both"):
        print("\n=== DROPPING TABLES ===")
        drop_all_tables(yes=yes)

    if action in ("load", "both"):
        print("\n=== LOADING DATA ===")
        load_data(sql_filepath=sql_filepath)
        print("Data loaded successfully!")

    if action == "both":
        print("\n=== DATABASE RELOAD COMPLETE ===")


def main():
    parser = argparse.ArgumentParser(description="Drop and/or load database tables")
    parser.add_argument(
        "--action",
        "-a",
        choices=["drop", "load", "both"],
        default="both",
        help="Action to perform: drop tables, load data, or both (default: both)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompts",
    )
    parser.add_argument(
        "--sql",
        default="create_tables.sql",
        help="Path to SQL schema file to execute (default: create_tables.sql)",
    )

    args = parser.parse_args()
    reload_database(
        action=args.action,
        yes=args.yes,
        sql_filepath=args.sql,
    )


if __name__ == "__main__":
    main()
