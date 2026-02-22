import sys
import os

# Import the storage_layout_cli module from the task's tools dir without altering project config
tools_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "tasks", "S41-storage-layout", "repo", "tools"
    )
)
if tools_path not in sys.path:
    sys.path.insert(0, tools_path)


def _load_cli_module():
    import importlib.util

    cli_path = os.path.join(tools_path, "storage_layout_cli.py")
    spec = importlib.util.spec_from_file_location("storage_layout_cli", cli_path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[misc]
    spec.loader.exec_module(mod)  # type: ignore[arg-type]
    return mod


def test_extract_entries_and_table_and_packing_and_diff():
    slc = _load_cli_module()
    # Minimal representative storage layout JSON
    layout = {
        "entries": [
            {"slot": 0, "offset": 0, "name": "owner", "type": "address", "bytes": 20},
            {"slot": 0, "offset": 20, "name": "value", "type": "uint256", "bytes": 32},
        ]
    }

    entries = slc.extract_entries(layout)
    assert isinstance(entries, list)
    # We expect at least the two entries above to be detected
    assert any(e.get("name") == "owner" and e.get("type") == "address" for e in entries)
    assert any(e.get("name") == "value" and e.get("type") == "uint256" for e in entries)

    lines = slc.format_table(entries)
    assert isinstance(lines, list)
    assert len(lines) >= 3  # header + 2 data rows

    packing = slc.compute_packing(entries)
    # All entries are in slot 0; first ends at 20, second ends at 52 -> max 52
    assert 0 in packing
    assert packing[0] == 52

    # Diff: compare old (single entry) vs new (two entries)
    old_entries = [entries[0]]
    new_entries = entries
    diff_text = slc.layout_to_str(old_entries, new_entries)
    assert isinstance(diff_text, str)
    assert "Slot 0" in diff_text


def test_decode_value_basic_types():
    slc = _load_cli_module()
    # uint256 value 1
    hex_uint32 = "0x" + "00" * 31 + "01"  # last byte = 0x01
    assert slc.decode_value(hex_uint32, "uint256") == "1"

    # address decoding: a 20-byte value encoded in the last 20 bytes
    addr_bytes = "11" * 20  # 20 bytes of 0x11
    hex_addr = "0x" + ("00" * 12) + addr_bytes  # pad to 32 bytes total
    decoded_addr = slc.decode_value(hex_addr, "address")
    assert decoded_addr.lower() == "0x" + ("11" * 20)  # last 20 bytes verification

    # bool true
    hex_bool = "0x" + "00" * 31 + "01"
    assert slc.decode_value(hex_bool, "bool") == "True"
