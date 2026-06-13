import pandas as pd
import glob
import os

# GDELT Event Headers
HEADERS = [
    "GlobalEventID", "Day", "MonthYear", "Year", "FractionDate",
    "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode", "Actor1EthnicCode", 
    "Actor1Religion1Code", "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
    "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode", "Actor2EthnicCode", 
    "Actor2Religion1Code", "Actor2Religion2Code", "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode", "QuadClass", 
    "GoldsteinScale", "NumMentions", "NumSources", "NumArticles", "AvgTone",
    "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode", "Actor1Geo_ADM1Code", 
    "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",
    "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode", "Actor2Geo_ADM1Code", 
    "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID",
    "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode", "ActionGeo_ADM1Code", 
    "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID",
    "DATEADDED", "SOURCEURL"
]

# Economic specific CAMEO Root Codes
# 08: Material Cooperation (Aid, Money)
# 10: Demand (Economic demands)
# 12: Reject (Boycotts)
# 16: Exhibit Force (Sanctions)
ECONOMIC_ROOT_CODES = ['08', '10', '12', '16']

# Keywords to search in SOURCEURL for better relevance
ECON_KEYWORDS = ['economy', 'finance', 'market', 'inflation', 'gdp', 'trade', 'tax', 'price']

def process_gdelt():
    input_pattern = "DataSet/*.export.CSV"
    output_dir = "cleaned_data"
    output_pool = []

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = glob.glob(input_pattern)
    print(f"Found {len(files)} GDELT files.")

    for file in files:
        print(f"Processing {file}...")
        try:
            # GDELT is tab-separated
            df = pd.read_csv(file, sep='\t', names=HEADERS, low_memory=False)
            
            # 1. Filter by Economic Event Root Codes
            df['EventRootCode'] = df['EventRootCode'].astype(str).str.zfill(2)
            mask_code = df['EventRootCode'].isin(ECONOMIC_ROOT_CODES)
            
            # 2. Filter by Keywords in URL (Case Insensitive)
            df['SOURCEURL'] = df['SOURCEURL'].astype(str).str.lower()
            mask_url = df['SOURCEURL'].str.contains('|'.join(ECON_KEYWORDS), na=False)
            
            # Combine filters: Root code OR relative keyword
            filtered_df = df[mask_code | mask_url].copy()
            
            # Select relevant columns to keep the file small
            keep_cols = [
                'GlobalEventID', 'Day', 'Year', 'Actor1Name', 'Actor2Name', 
                'EventCode', 'GoldsteinScale', 'AvgTone', 'ActionGeo_FullName', 
                'ActionGeo_CountryCode', 'SOURCEURL'
            ]
            filtered_df = filtered_df[keep_cols]
            
            output_pool.append(filtered_df)
            print(f"  - Extracted {len(filtered_df)} economic events.")
            
        except Exception as e:
            print(f"  - Error processing {file}: {e}")

    if output_pool:
        final_df = pd.concat(output_pool, ignore_index=True)
        output_path = os.path.join(output_dir, "news_cleaned.csv")
        final_df.to_csv(output_path, index=False)
        print(f"\nSaved {len(final_df)} events to {output_path}")
    else:
        print("No economic events found.")

if __name__ == "__main__":
    process_gdelt()
