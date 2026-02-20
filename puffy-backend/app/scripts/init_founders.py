import sys
import csv
from pytoniq_core import Address
from app.db import models, schemas, engine, SessionLocal
from pytoniq_core import Address


def read_founders(founder_csv):
    founders = []
    with open(founder_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        # Iterate through each row in the CSV file
        for row in reader:
            if row["Status"] != "Paid":
                print("row is not paid")
                continue
            if float(row["Amount"]) < 128:
                print("row is less than 128")
                continue
            founders.append(row)
    return founders


def is_valid_address(wallet_address: str) -> str:
    try:
        _ = Address(wallet_address)
        return True
    except Exception as err:
        return False


def add_founder(db, founder):
    print("add founder %s %s", founder.wallet_address_b64, founder.count)
    try:
        db.add(founder)
        db.commit()
    except Exception as err:
        db.rollback()
        print(err)


def write_founders(founders_dict):
    with SessionLocal() as db:
        for k, v in founders_dict.items():
            founder = models.Founder(
                wallet_address_b64=k,
                count=v,
                claimed=False,
            )
            add_founder(db, founder)


def init_founders(founder_csv):
    founders = read_founders(founder_csv)
    founders_dict = {}
    for f in founders:
        founder_count = f.get("final_address")
        parts = founder_count.split(' ')
        if len(parts) == 2:
            if is_valid_address(parts[0]):
                wallet, count = parts[0], int(parts[1])
                if founders_dict.get(wallet):
                    founders_dict[wallet] += count
                else:
                    founders_dict[wallet] = count
        elif len(parts) == 4:
            if is_valid_address(parts[0]):
                wallet, count = parts[0], int(parts[1])
                if founders_dict.get(wallet):
                    founders_dict[wallet] += count
                else:
                    founders_dict[wallet] = count
            if is_valid_address(parts[2]):
                wallet, count = parts[2], int(parts[3])
                if founders_dict.get(wallet):
                    founders_dict[wallet] += count
                else:
                    founders_dict[wallet] = count
    write_founders(founders_dict)


def init_wallet(wallet_file):
    founders = {}
    with open(wallet_file, "r") as f:
        for line in f:
            founders[line.stripe()] = 1
    write_founders(founders)


if __name__ == '__main__':
    if "csv" in sys.argv[1]:
        init_founders(sys.argv[1])
    else:
        init_wallet(sys.argv[1])
