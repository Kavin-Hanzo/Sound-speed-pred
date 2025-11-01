import numpy as np
import gsw

def compute_depth(pressure_dbar, latitude):
    """
    Convert pressure (dbar) to depth (m) using TEOS-10.
    Inputs:
        pressure_dbar : array-like, pressure in decibar
        latitude      : array-like or scalar, latitude in decimal degrees
    Returns:
        depth_m : array, depth in meters (positive down)
    """
    # gsw.z_from_p returns negative depth (z, meters)
    z = gsw.z_from_p(np.asarray(pressure_dbar), np.asarray(latitude))
    depth_m = -z
    return depth_m


def compute_sound_speed(pressure_dbar, temperature_in_situ, salinity_sp, lon, lat):
    """
    Compute sound speed (m/s) from CTD measurements using TEOS-10.
    Inputs:
        pressure_dbar     : array-like, pressure in dbar
        temperature_in_situ: array-like, in-situ temperature in °C
        salinity_sp       : array-like, Practical Salinity (PSU)
        lon, lat          : array-like or scalar, longitude and latitude
    Returns:
        sound_speed : array, sound speed in m/s
    """
    p = np.asarray(pressure_dbar)
    t = np.asarray(temperature_in_situ)
    SP = np.asarray(salinity_sp)
    lon = np.asarray(lon)
    lat = np.asarray(lat)

    # 1. Convert SP -> Absolute Salinity (SA)
    SA = gsw.SA_from_SP(SP, p, lon, lat)

    # 2. Convert in-situ T -> Conservative Temperature (CT)
    CT = gsw.CT_from_t(SA, t, p)

    # 3. Compute sound speed
    c = gsw.sound_speed(SA, CT, p)

    return c

def apply_teos10(df,
                 pressure_col="CTDPRS",
                 temp_col="CTDTMP",
                 sal_col="CTDSAL",
                 lat_col="LATITUDE",
                 lon_col="LONGITUDE"):
    """
    Apply TEOS-10 conversions to a DataFrame of CTD values.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Must contain columns:
        - pressure (dbar), e.g. 'CTDPRS'
        - temperature (°C), e.g. 'CTDTMP'
        - salinity (PSU), e.g. 'CTDSAL'
        - latitude (deg)
        - longitude (deg)
    pressure_col, temp_col, sal_col, lat_col, lon_col : str
        Column names for each variable.
    
    Returns
    -------
    df_out : pandas.DataFrame
        Original DataFrame with new columns:
        - depth_m
        - SA (Absolute Salinity)
        - CT (Conservative Temperature)
        - sound_speed (m/s)
    """
    # Remove rows with missing or obviously invalid values
    invalids = [-999, -9999, 9999, 99999]
    for col in ["CTDPRS", "CTDTMP", "CTDSAL", "LATITUDE", "LONGITUDE"]:
        df = df[~df[col].isin(invalids)]
    df = df.dropna(subset=["CTDPRS", "CTDTMP", "CTDSAL", "LATITUDE", "LONGITUDE"])
    
    p = df[pressure_col].to_numpy()
    t = df[temp_col].to_numpy()
    SP = df[sal_col].to_numpy()
    lat = df[lat_col].to_numpy()
    lon = df[lon_col].to_numpy()

    # Depth from pressure (z is negative)
    z = gsw.z_from_p(p, lat)
    depth_m = -z

    # Absolute Salinity
    SA = gsw.SA_from_SP(SP, p, lon, lat)

    # Conservative Temperature
    CT = gsw.CT_from_t(SA, t, p)

    # Sound speed
    c = gsw.sound_speed(SA, CT, p)

    # Add to DataFrame
    df = df.copy()
    df["depth_m"] = depth_m
    df["SA"] = SA
    df["CT"] = CT
    df["sound_speed"] = c

    return df

if __name__ == "__main__":
    import pandas as pd
    import sys
    import argparse
    parser = argparse.ArgumentParser(description="Apply TEOS-10 features to a CSV file.")
    parser.add_argument('input_csv', type=str, help='Input CSV file')
    parser.add_argument('output_csv', type=str, nargs='?', default=None, help='Output CSV file (optional)')
    args = parser.parse_args()
    csv_path = args.input_csv
    out_path = args.output_csv if args.output_csv else csv_path.replace('.csv', '_teos10.csv')
    df = pd.read_csv(csv_path)
    df_teos = apply_teos10(df)
    df_teos.to_csv(out_path, index=False)
    print(f"TEOS-10 features added and saved to {out_path}")



