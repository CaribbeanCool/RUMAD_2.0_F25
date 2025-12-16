import argparse
from db import DB


DROP_ORDER = [
    "syllabus",
    "db_user",
    "section",
    "requisite",
    "meeting",
    "room",
    "class",
]


def drop_all_tables(yes: bool = False):
    if not yes:
        resp = input(
            "This will DROP ALL project tables (syllabus, section, requisite, meeting, room, class). Continue? [y/N]: "
        )
        if resp.lower() not in ("y", "yes"):
            print("Aborted by user.")
            return

    print("\n--- Dropping tables ---")
    db = DB()
    try:
        for t in DROP_ORDER:
            sql = f"DROP TABLE IF EXISTS {t} CASCADE"
            print(f"Dropping {t} ...")
            db.query(sql)
        print("All listed tables dropped (if they existed).")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Drop project tables")
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )
    args = parser.parse_args()
    drop_all_tables(yes=args.yes)


if __name__ == "__main__":
    main()
