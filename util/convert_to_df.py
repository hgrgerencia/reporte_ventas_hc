import pandas as pd

def convert_docs_to_df(docs):
    all_data = list(docs)
    if not all_data:
        return [[],[]]
    df = pd.DataFrame(all_data)
    df = df.drop(columns=['_id'])
    return [all_data, df]
