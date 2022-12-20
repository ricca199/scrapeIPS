import pandas as pd
import numpy as np
import os,sys
from pathlib import Path
from datetime import datetime


if __name__ == '__main__':
    cwd = Path.cwd()
    _loc = [i.name for i in list(Path.cwd().glob("*.csv"))]
    _df = pd.DataFrame()
    for f in _loc:
        if f.__contains__('$'):
            continue
        data = pd.read_csv(cwd / f, index_col=None).iloc[:,1:]
        print(data)
        _df = pd.concat([_df,data], ignore_index=True)
        print(f)
        
    empty_cols = [col for col in data.columns if data[col].isnull().all()]
    data.drop(empty_cols,
            axis=1,
            inplace=True)
    #time_to_append = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    #filename = "table_urls_final" + time_to_append + '.csv'
    #_df.to_csv(cwd / filename)