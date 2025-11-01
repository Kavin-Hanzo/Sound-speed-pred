import os
import zipfile
import pandas as pd
import tempfile
import shutil
from pathlib import Path
import argparse

def stripping(filepath):
    """
    Reads a WOCE CTD csv file, filters comments and metadata, extracts latitude/longitude,
    parses header and data, and returns a DataFrame with LATITUDE, LONGITUDE, and data columns.
    """
    import pandas as pd
    lat = None
    lon = None
    header = None
    data_lines = []
    found_lat = False
    found_header = False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip comment lines and metadata
        if not found_lat:
            if line.startswith('LATITUDE'):
                lat = float(line.split('=')[1].strip(','))
                # Next line should be LONGITUDE
                i += 1
                lon_line = lines[i].strip()
                if lon_line.startswith('LONGITUDE'):
                    lon = float(lon_line.split('=')[1].strip(','))
                found_lat = True
        elif not found_header:
            if line.startswith('CTDPRS'):
                header = line.split(',')
                # Add LATITUDE and LONGITUDE to header
                header = ['LATITUDE', 'LONGITUDE'] + header
                found_header = True
                i += 1  # skip the next line (usually units)
        elif found_header:
            # Stop at END_DATA
            if line.startswith('END_DATA'):
                break
            # Only process non-empty, non-comment lines
            if line and not line.startswith('#'):
                values = line.split(',')
                # Prepend lat/lon to each row
                row = [lat, lon] + [float(v) if v else None for v in values]
                data_lines.append(row)
        i += 1
    
    # Create DataFrame
    df = pd.DataFrame(data_lines, columns=header)
    return df

def process_zip_files(data_folder="data", output_folder="processed_data"):
    """
    Process all zip files in the data folder, extract and process CSV files,
    and save concatenated results for each zip file.
    """
    # Columns to keep in final dataframe
    columns_to_keep = ["LATITUDE", "LONGITUDE", "CTDPRS", "CTDTMP", "CTDSAL"]
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all zip files in the data folder
    data_path = Path(data_folder)
    zip_files = list(data_path.glob("*.zip"))
    
    if not zip_files:
        print(f"No zip files found in {data_folder}")
        return
    
    print(f"Found {len(zip_files)} zip files to process")
    
    for zip_file in zip_files:
        print(f"\nProcessing: {zip_file.name}")
        
        # Create temporary directory for extracting files
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Extract zip file
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find all CSV files in extracted content
                temp_path = Path(temp_dir)
                csv_files = list(temp_path.rglob("*.csv"))
                
                if not csv_files:
                    print(f"  No CSV files found in {zip_file.name}")
                    continue
                
                print(f"  Found {len(csv_files)} CSV files")
                
                # Process each CSV file and collect dataframes
                dataframes = []
                successful_files = 0
                
                for csv_file in csv_files:
                    try:
                        df = stripping(str(csv_file))
                        
                        # Filter to keep only required columns (if they exist)
                        available_columns = [col for col in columns_to_keep if col in df.columns]
                        if available_columns:
                            df_filtered = df[available_columns].copy()
                            dataframes.append(df_filtered)
                            successful_files += 1
                        else:
                            print(f"    Warning: No required columns found in {csv_file.name}")
                            
                    except Exception as e:
                        print(f"    Error processing {csv_file.name}: {str(e)}")
                
                # Concatenate all dataframes if any were successfully processed
                if dataframes:
                    combined_df = pd.concat(dataframes, ignore_index=True)
                    
                    # Remove rows with all NaN values (except lat/lon)
                    combined_df = combined_df.dropna(subset=[col for col in combined_df.columns 
                                                           if col not in ['LATITUDE', 'LONGITUDE']], 
                                                    how='all')
                    
                    # Save to CSV with zip file name
                    output_filename = f"{zip_file.stem}_processed.csv"
                    output_path = Path(output_folder) / output_filename
                    combined_df.to_csv(output_path, index=False)
                    
                    print(f"  Successfully processed {successful_files} files")
                    print(f"  Combined dataframe shape: {combined_df.shape}")
                    print(f"  Saved as: {output_filename}")
                else:
                    print(f"  No valid data found in {zip_file.name}")
                    
            except Exception as e:
                print(f"  Error processing zip file {zip_file.name}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Process zip files to extract and process CSVs.")
    parser.add_argument('--data_folder', type=str, default="D:/DS & ML/MLE/dataset/ewoce/data", help='Folder containing zip files')
    parser.add_argument('--output_folder', type=str, default="processed_data", help='Folder to store processed CSVs')
    args = parser.parse_args()
    process_zip_files(data_folder=args.data_folder, output_folder=args.output_folder)
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()