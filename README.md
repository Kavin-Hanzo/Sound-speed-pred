# Sound-speed-pred
Estimation of Under water Sound speed profiles.

## Process and Flow:-

1. Collection from different sources (WOCE - ctd(diff regions))
2. Extraction of actual records from Data (filtering CSVs with comments and other documentated values)
3. Combining records, feature conversion and creations
4. Cleaning, EDA
5. Train,Test,Predict


## Data Creation Pipeline

python Aggregator.py --zip_folder "path_to_zip_folder" --processed_folder "processed_data" --aggregated_csv "aggregated.csv" --final_csv "Train_data.csv"


