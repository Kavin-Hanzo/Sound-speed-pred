import argparse
import os
import sys
import subprocess
from pathlib import Path
import pandas as pd
import glob

# Import functions from other scripts if possible, else use subprocess

def run_zipstrippor(data_folder, output_folder):
    """Run ZipStrippor.py as a subprocess."""
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), 'ZipStrippor.py'),
           '--data_folder', data_folder, '--output_folder', output_folder]
    result = subprocess.run(cmd, check=True)
    print(f"ZipStrippor finished. Output folder: {output_folder}")


def run_aggregator(input_folder, output_csv):
    """Aggregate processed CSVs into one file."""
    main_rows = []
    csv_files = glob.glob(os.path.join(input_folder, '*.csv'))
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        # Group by unique latitude, calculate mean of CTDPRS, CTDTMP, CTDSAL
        grouped = df.groupby('LATITUDE').agg({
            'LONGITUDE': 'first',
            'CTDPRS': 'mean',
            'CTDTMP': 'mean',
            'CTDSAL': 'mean'
        }).reset_index()
        grouped = grouped[['LATITUDE', 'LONGITUDE', 'CTDPRS', 'CTDTMP', 'CTDSAL']]
        main_rows.append(grouped)
    if main_rows:
        main_df = pd.concat(main_rows, ignore_index=True)
        main_df.to_csv(output_csv, index=False)
        print(f"Aggregator finished. Output CSV: {output_csv}")
    else:
        print("No CSV files found or processed.")


def run_conversion_functions(input_csv, output_csv):
    """Run conversion_functions.py as a subprocess."""
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), 'conversion_functions.py'),
           input_csv, output_csv]
    result = subprocess.run(cmd, check=True)
    print(f"Conversion finished. Output CSV: {output_csv}")


def main():
    parser = argparse.ArgumentParser(description="DataCreation Pipeline: Zip -> Aggregate -> TEOS-10 Conversion")
    parser.add_argument('--zip_folder', type=str, required=True, help='Folder containing zip files')
    parser.add_argument('--processed_folder', type=str, default='processed_data', help='Folder to store processed CSVs')
    parser.add_argument('--aggregated_csv', type=str, default='aggregated.csv', help='Path for aggregated CSV')
    parser.add_argument('--final_csv', type=str, default='Train_data.csv', help='Path for final output CSV')
    args = parser.parse_args()

    # Step 1: Unzip and process
    run_zipstrippor(args.zip_folder, args.processed_folder)
    # Step 2: Aggregate
    run_aggregator(args.processed_folder, args.aggregated_csv)
    # Step 3: TEOS-10 conversion
    run_conversion_functions(args.aggregated_csv, args.final_csv)
    print("\nPipeline complete! Final data at:", args.final_csv)

if __name__ == "__main__":
    main()
