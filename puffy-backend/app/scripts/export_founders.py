import sys
import csv
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


def write_founders(founders, output_file):
    field_names = founders[0].keys()
    with open(output_file, 'w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=field_names)
        writer.writeheader()
        for p in founders:
            writer.writerow(p)


def is_valid_address(wallet_address: str) -> bool:
    try:
        _ = Address(wallet_address)
        return True
    except Exception as err:
        try:
            _ = Address(format_address(wallet_address))
            return True
        except Exception as err:
            return False


def format_address(addr: str) -> str:
    addr_prefix = "ton://transfer/"
    if addr_prefix in addr:
        return addr.replace(addr_prefix, "")
    return addr


def pick_address(founder_dict):
    final_address = ""
    purchase_count = int((float(founder_dict["Amount"])-30) / 98)
    if purchase_count == 1:
        possible_fields = [
            "TON Wallet (metadata)",
            "TON Wallet  (metadata)",
            "TON Wallet 1 (metadata)",
            "TON Wallet 2 (metadata)",
            "Checkout Custom Field 1 Value",
        ]
        for p in possible_fields:
            print(p)
            print(founder_dict.get(p))
            if is_valid_address(founder_dict.get(p)):
                print("is valid")
                final_address = founder_dict.get(p) + " 1"
                break
    elif purchase_count >= 2:
        possible_fields = [
            "TON Wallet  (metadata)",
            "TON Wallet (metadata)",
            "TON Wallet 1 (metadata)",
            "TON Wallet 2 (metadata)",
            "Checkout Custom Field 1 Value",
        ]
        if is_valid_address(founder_dict.get(possible_fields[0])):
            final_address = founder_dict.get(
                possible_fields[0]) + " " + str(purchase_count)
        elif is_valid_address(founder_dict.get(possible_fields[1])):
            final_address = founder_dict.get(
                possible_fields[1]) + " " + str(purchase_count)
        elif (is_valid_address(founder_dict.get(possible_fields[2]))
              and is_valid_address(founder_dict.get(possible_fields[3]))):
            addr1 = founder_dict.get(possible_fields[2])
            addr2 = founder_dict.get(possible_fields[3])
            final_address = f"{addr1} 1 {addr2} {purchase_count - 1}"
        elif (is_valid_address(founder_dict.get(possible_fields[2]))):
            final_address = founder_dict.get(
                possible_fields[2]) + " " + str(purchase_count)
        elif (is_valid_address(founder_dict.get(possible_fields[3]))):
            final_address = founder_dict.get(
                possible_fields[3]) + " " + str(purchase_count)
        else:
            final_address = f"{founder_dict.get(possible_fields[4])} {purchase_count}"
    founder_dict["purchase_count"] = purchase_count
    founder_dict["final_address"] = format_address(final_address)


def export_founders(founder_csv):
    founders = read_founders(founder_csv)
    for f in founders:
        pick_address(f)
    write_founders(founders, "new_payment2.csv")


if __name__ == '__main__':
    export_founders(sys.argv[1])
