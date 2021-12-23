import os 
import uuid 
import click 
from pathlib import Path 

import pandas as pd 


# ====
# Main 
# ====
@click.command() 
@click.option('--input-file', required=True, type=str)
@click.option('--output-file', required=True, type=str) 
def main (
    input_file :str,  
    output_file :str
): 
    # Check and init parameters 
    input_file = Path(input_file)
    assert(input_file.is_file())
    input_file = input_file.as_posix() 

    output_file = Path(output_file).as_posix() 
    assert(input_file != output_file)
    assert(output_file.endswith('.csv')), '[ERROR] only support .csv output for now...'

    # Load the dataframe 
    df = None 
    if (input_file.endswith('.xlsx')): 
        df = pd.read_excel(input_file) 
    elif (input_file.endswith('.csv')): 
        df = pd.read_csv(input_file)
    else: 
        assert(False), f'[ERROR] unsupported data format... {input_file}'
    assert(df is not None)

    df_len = len(df) 

    df['UUID'] = [uuid.uuid4() for i in range(df_len)]

    # Init the dataframe 
    def add_df_col (col :str, default_v=None): 
        assert(col not in df) 
        df[col] = [default_v] * df_len 

    add_df_col('Anti-China', -1.0)
    add_df_col('Anti-Japan', -1.0)
    add_df_col('Anti-US', -1.0)
    add_df_col('China-Fellow', -1.0)
    add_df_col('Japan-Fellow', -1.0)
    add_df_col('US-Fellow', -1.0)
    
    add_df_col('Anti-KMT', -1.0)
    add_df_col('KMT-Fellow', -1.0)
    add_df_col('Anti-DPP', -1.0)
    add_df_col('DPP-Fellow', -1.0)

    add_df_col('Anti-Taiwan-Gov', -1.0)
    add_df_col('Taiwan-Gov-Fellow', -1.0)
    
    # Write the initialized df 
    df.to_csv(output_file, index=False, encoding='utf-8') 


# ==== 
# Entry 
# ==== 
if __name__ == '__main__': 
    main() 