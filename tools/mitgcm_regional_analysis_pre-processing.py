# =============================================================================
# Pre-Processing MITgcm data for the Regional Analysis
# =============================================================================
#
# Description:
#   Slice the MITgcm data to extract the temperature, salinity, and 
#   velocity variables for the Regional Analysis. The script will read in the MITgcm 
#   output files, extract the necessary variables, and save them in netcdf format for 
#   further analysis.
#
# Author:
#   Luke Colosi
#
# Created:
#   2026-08-10
# =============================================================================

# Import python libraries 
import sys
from pathlib import Path
import numpy as np
from xmitgcm import open_mdsdataset
import xgcm
import warnings

# Set path to project root directory
ROOT = Path(__file__).resolve().parents[1]

# Set paths to project directories
PATH_tools = ROOT / "tools"

# Set path to access additional python functions
sys.path.append(str(PATH_tools))

# Import plotting toolbox
from plotting import status

# Suppress the interpolation warning message from xgcm
warnings.filterwarnings(
    "ignore",
    message=r"The return type of `Dataset\.dims` will be changed",
    category=FutureWarning,
)

status(f"Starting MITgcm pre-processing for the Regional Analysis")

# -----------------------------------------------------------------------------
# Set data parameters
# -----------------------------------------------------------------------------

# ------------# 
# --- Note ---# 
# ------------#
#
# - delta_t: Model time step in seconds (time increments of the diagnostics can differ).
# - depth: Depth level extracted for regional analysis(units: meters).
# - lat_bnds: Latitude bounds setting the region of interest.
# - lon_bnds: Longitude bounds setting the region of interest.
# - halo_cells : Number of data points to extend the boundaries to ensure data is
#                present at the boundaries the study doamin when plotting
#                with contourf.
# - encoding: Start time of the model run.
# - PATH_GRID: Directory containing the model grid.
# - PATH_OUTPUT: Directory containing model diagnostics.
# - PATH_nc: Directory where netCDF files are saved.
# - file_dim: Diagnostic file dimension (3D for T, S, drhodr, and velocity; 2D for etan).
#
# ------------# 

# Model parameters 
delta_t = 150  

# Set time and space parameters  
depth      = 100                                                         
lat_bnds   = [33.0, 35.0]                                          
lon_bnds   = [237.0, 240.0]
halo_cells = 3                                          
encoding   = {'time': {'units': 'seconds since 2015-12-01 2:00'}}  

# Set path to project directory
PATH_GRID   = '/data/SO2/SWOT/GRID/BIN/'                    
PATH_OUTPUT = '/data/SO2/SWOT/MARA/RUN4_LY/DIAGS_HRLY/'     
PATH_nc     = '/data/SO3/lcolosi/OceanScales/mitgcm/regional/'  
file_dim    = '3D'                                         

# -----------------------------------------------------------------------------
# Load the grid and diagnostics data into a python structure
# -----------------------------------------------------------------------------
status(f"Loading the grid and diagnostics data...")

# ------------ #  
# --- Note --- #
# ------------ # 
#
# - PATH_OUTPUT: Directory containing model output (.data and .meta files).
# - PATH_GRID: Directory containing the model grid.
# - iters: Load all available model iterations.
# - delta_t: Model time step in seconds.
# - ignore_unknown_vars: Do not ignore unrecognized variables.
# - prefix: Load diagnostics corresponding to the specified file dimension.
# - ref_date: Start time of the simulation, including model spin-up.
# - geometry: Model grid uses spherical-polar coordinates.
#
# ------------ # 

# Create dataset 
ds = open_mdsdataset(
    PATH_OUTPUT,                    
    PATH_GRID,                      
    iters='all',                    
    delta_t=delta_t, 
    ignore_unknown_vars=False,     
    prefix=['diags_' + file_dim],   
    ref_date="2015-01-01 02:00:00", 
    geometry='sphericalpolar'       
)

# Convert all variables and coordinates in the dataset to little-endian

# --- Variables --- #
for var in ds.data_vars:
    if ds[var].dtype.byteorder == '>' or (ds[var].dtype.byteorder == '=' and sys.byteorder == "big"):  
        ds[var] = ds[var].astype(ds[var].dtype.newbyteorder('<'))

# --- Coordinates --- # 
for coord in ds.coords:
    if ds[coord].dtype.byteorder == '>'or (ds[coord].dtype.byteorder == '=' and sys.byteorder == "big"):  
        ds[coord] = ds[coord].astype(ds[coord].dtype.newbyteorder('<'))

# -----------------------------------------------------------------------------
# Print model domain summary
# -----------------------------------------------------------------------------

# Spatial extent
lat_min = float(ds.YC.min().values)
lat_max = float(ds.YC.max().values)
lon_min = float(ds.XC.min().values)
lon_max = float(ds.XC.max().values)

# Vertical extent
depth_min = float(-ds.Z.max().values)
depth_max = float(-ds.Z.min().values)
n_depth   = ds.Z.size

# Temporal extent
time_start = ds.time.values[0]
time_end   = ds.time.values[-1]
n_time     = ds.time.size

# Horizontal grid dimensions
n_lat, n_lon = ds.XC.shape

# Print summary
print("\n--- MITgcm Model Domain Summary ---")
print(f"Latitude range   : {lat_min:.2f}°N to {lat_max:.2f}°N")
print(f"Longitude range  : {lon_min:.2f}°E to {lon_max:.2f}°E")
print(f"Grid dimensions  : {n_lat} × {n_lon}")
print(f"Depth range      : {depth_min:.2f} to {depth_max:.2f} m")
print(f"Depth levels     : {n_depth}")
print(f"Temporal extent  : {time_start} to {time_end}")
print(f"Time steps       : {n_time:,}")
print("-----------------------------------\n")


