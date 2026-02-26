import pandas as pd

def make_assets(rows):
    return pd.DataFrame(rows)


def make_cablenod(link_ids):
    return pd.DataFrame({"LINK_ID": list(link_ids)})
