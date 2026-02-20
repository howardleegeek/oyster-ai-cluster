import sys
import csv
from pytoniq_core import Address
from app.db import crud, models, schemas, engine, SessionLocal
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


def has_been_claimed(address):
    with SessionLocal() as db:
        founder = crud.get_founder(db, address)
        if founder and founder.claimed:
            return True
        else:
            return False


def has_overlap(address):
    with SessionLocal() as db:
        founder = crud.get_founder(db, address)
        if founder:
            return True, founder.claimed
        return False, None


def format_a(addr):
    if " " in addr:
        return addr.split(" ")[0]


def dry_run_update_founders(founder_csv):
    founders = read_founders(founder_csv)
    for f in founders:
        if f.get("same") != "FALSE":
            continue
        old_address = format_a(f.get("final_address_1"))
        new_address = format_a(f.get("final_address_2"))
        old_claimed = has_been_claimed(old_address)
        new_overlap = has_overlap(new_address)[0]
        print("old address ", old_address, " claimed: ", old_claimed)
        print("new address ", new_address, " overlapped: ", new_overlap)


def update_founder_and_balance(new_address, new_count):
    with SessionLocal() as db:
        try:
            db.query(models.Founder).filter(
                models.Founder.wallet_address_b64 == new_address
            ).update({
                "count": models.Founder.count + new_count,
            })
            user = db.query(models.User).filter(
                models.User.wallet_address_b64 == new_address
            ).first()
            if user:
                db.query(models.Balance).filter(
                    models.Balance.user_id == user.id
                ).update({
                    "founder_pass": models.Balance.founder_pass + new_count,
                    "upoints": models.Balance.upoints + new_count * 10,
                })
            db.commit()
            return "succ"
        except Exception as err:
            db.rollback()
            return "fail"


def update_founder(new_address, new_count):
    with SessionLocal() as db:
        try:
            db.query(models.Founder).filter(
                models.Founder.wallet_address_b64 == new_address
            ).update({
                "count": models.Founder.count + new_count,
            })
            db.commit()
            return "succ"
        except Exception as err:
            db.rollback()
            return "fail"


def insert_founder(new_address, new_count):
    with SessionLocal() as db:
        founder = models.Founder(
            wallet_address_b64=new_address,
            count=new_count,
            claimed=False,
        )
        return add_founder(db, founder)


def add_founder(db, founder):
    print("add founder %s %s", founder.wallet_address_b64, founder.count)
    try:
        db.add(founder)
        db.commit()
        return "succ"
    except Exception as err:
        db.rollback()
        print(err)
        return "fail"


def update_founders(founder_csv):
    founders = read_founders(founder_csv)
    for f in founders:
        if f.get("same") != "FALSE":
            continue
        old_address = format_a(f.get("final_address_1"))
        new_address, new_count = f.get("final_address_2").split(" ")
        old_claimed = has_been_claimed(old_address)
        new_overlap, claimed = has_overlap(new_address)
        print("old address ", old_address, " claimed: ", old_claimed)
        print("new address ", new_address, " overlapped: ",
              new_overlap, " claimed: ", claimed)
        if new_overlap and claimed is True:
            # update founder and balance
            print("address overlap and claimed, change founder and balance")
            status = update_founder_and_balance(new_address, new_count)
        elif new_overlap and claimed is False:
            print("address overlap and not claimed, change founder")
            status = update_founder(new_address, new_count)
        else:
            # insert founder
            print("address not founder, insert founder")
            status = insert_founder(new_address, new_count)
        print(f, " with status ", status)


if __name__ == '__main__':
    if "--dry-run" in sys.argv:
        dry_run_update_founders(sys.argv[1])
        exit(0)
    if "csv" in sys.argv[1]:
        update_founders(sys.argv[1])
        exit(0)
