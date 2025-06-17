#=======================
# Copyright 2025 Esri
#=======================

def zip_county_highways(full_fc_path, output_folder, county):
    '''
    This function creates a zip file containing a file geodatabase with 
    a feature class containing only the highways for a specific county.

    Parameters:
        full_fc_path (str): The full path to the input feature class
        output_folder (str): The path to the output folder
        county (str): The name of the county to extract highways for

    Returns:
        str: The path to the zipped file geodatabase
    '''
    
    # remove spaces from county name
    county_no_spaces = county.replace(" ", "_")
    
    # create a file geodatabase
    fgdb = arcpy.management.CreateFileGDB(
        out_folder_path = output_folder,
        out_name = f"{county_no_spaces}_Output"
    )

    # Create a feature class
    output_fc = arcpy.conversion.ExportFeatures(
        in_features = full_fc_path,
        out_features = os.path.join(fgdb[0], 
                                    f"{county_no_spaces}_Highways"),
        where_clause = f"NAMELSAD = '{county}'"
    )
    
    source_fgdb_path = pathlib.Path(fgdb[0])

    # The name of the folder to place the File Geodatabase in
    fgdb_folder_name = source_fgdb_path.stem
    # The location of the folder to place the File Geodatabase in
    fgdb_folder_location = source_fgdb_path.parent
    # The path to the folder to place the File Geodatabase in
    fgdb_folder_path = fgdb_folder_location.joinpath(fgdb_folder_name)
    # The path of our copied File Geodatabase
    fgdb_path = fgdb_folder_path.joinpath(source_fgdb_path.name)

    # copy the file geodatabase into a temp folder
    shutil.copytree(
        source_fgdb_path, 
        fgdb_path, 
        ignore=shutil.ignore_patterns('*.lock')
    )

    # Zip the File Geodatabase
    zipped_fgdb = shutil.make_archive(
        base_name=fgdb_folder_path,  # The name of the archive, not including the file extension
        format="zip",  # The archive format
        root_dir=fgdb_folder_path,  # The directory to archive
    ) 

    # delete the file geodatabase
    arcpy.management.Delete(fgdb)

    # remove the temp folder
    shutil.rmtree(fgdb_folder_path)
    
    # return the zip file path
    return zipped_fgdb

# package imports
import arcpy
import os
import shutil
import pathlib
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

#=============================== INPUTS ===================================
# input file geodatabase path
input_fgdb = r".\Chapter 10.gdb"

# input feature class name
input_fc_name = "Highways_intersect"

# output folder
output_folder = r".\zipped_outputs"
#==========================================================================

if __name__ == '__main__':
    # get the full feature class path
    full_fc_path = os.path.join(
        input_fgdb, input_fc_name
    )

    # get the county for each feature
    counties = [r[0] for r in arcpy.da.SearchCursor(full_fc_path, ['NAMELSAD'])]

    # narrow the counties down to unique counties
    counties = list(set(counties))
    counties.sort()

    # create the output folder
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # get your cpu count for multiprocessing
    process_count = multiprocessing.cpu_count()

    
    # set up the process pool executor
    with ProcessPoolExecutor(max_workers=process_count) as executor:
        
        # set up a list to contain all the future objects
        futures_list = []
        
        # submit each job to the executor
        for county in counties:
            futures_list.append(executor.submit(zip_county_highways, full_fc_path, output_folder, county))

        # iterate through the futures to see when they're completed
        for future in as_completed(futures_list):
            print(future.result())