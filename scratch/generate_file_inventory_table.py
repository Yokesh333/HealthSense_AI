import json
import pathlib

scratch_dir = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\scratch")
with open(scratch_dir / "inventory.json", "r") as f:
    inventory = json.load(f)

print(f"Loaded {len(inventory)} file inventory items.\n")

for i, item in enumerate(inventory, 1):
    print(f"--- File {i}: {item['filename']} ---")
    print(f"Path: {item['path']}")
    print(f"Rows: {item['num_rows']}, Cols: {item['num_cols']}")
    print(f"PATNO Col: {item['patno_col']}")
    print(f"Visit Cols: {item['visit_cols']}")
    print(f"Date Cols: {item['date_cols']}")
    print(f"Columns ({len(item['columns'])}): {item['columns'][:10]}... (truncated)")
    print()

