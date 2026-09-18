# Load packages 
import arcpy
import os
arcpy.env.overwriteOutput = True

# Set file path for exports to be saved to
out_kmz_file=r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\08_Data_Development\CVIN Bio Query Outputs"
out_gdb_path=r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb"

# Retrieves user inputted parameters
Segment = arcpy.GetParameter(1)
Subsegment= arcpy.GetParameter(0)
InputLayer = arcpy.GetParameter(2)
SearchDistance = arcpy.GetParameterAsText(3)
FederalClip = arcpy.GetParameter(4)
LandAgency = arcpy.GetParameterAsText(5)

Dist = SearchDistance.replace(" ", "")
FileNameDist = Dist.replace(".","pt")
OutputGDB = f"{out_gdb_path}\\Segment{Segment}"

# Define your input layers to run Select by Location tool on 
input_layers = {r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\NHD_Area": "NHDArea",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\NHDFlowline": "NHDFlowline",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\NWI_Wetlands": "NWIWetlands",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\BioDatabaseLayers\USFWS_CriticalHabitat_CA": "USFWSCriticalHabitat",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\BioDatabaseLayers\CNDDB_CA": "CNDDB",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\BioDatabaseLayers\NMFS_CriticalHabitat_Poly_CA": "NMFSCriticalHabitatPoly",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\BioDatabaseLayers\NMFS_CriticalHabitatLine_CA": "NMFSCriticalHabitatLine", 
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\BioDatabaseLayers\NOAA_EssentialFishHabitat_CA": "EssentialFishHabitat",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\BioDatabaseLayers\NOAA_EssentialFishHabitat_WestCoast": "EFH_WestCoast",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\BioDatabaseLayers\NOAA_EssentialFishHabitat_HMS": "EFH_WestCoast_HMS",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\BioDatabaseLayers\NOAA_EssentialFishHabitat_Groundfish": "EFH_Groundfish",
                r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb\BioDatabaseLayers\NOAA_EssentialFishHabitat_Salmonid": "EFH_Salmonid"}    
selection_layers = {}

# Federal lands clipping option enabled:
if FederalClip:
    federal_lands_url = r"https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/USA_Federal_Lands_2025/FeatureServer/0"
    federal_lands_layer = "federal_lands_layer"
    agency_sql = f"Agency = '{LandAgency}'"

    arcpy.management.MakeFeatureLayer(
        federal_lands_url,
        federal_lands_layer,
        agency_sql
        )
    
    federal_lands_local = r"memory\federal_lands"
    
    arcpy.management.CopyFeatures(
        federal_lands_layer,
        federal_lands_local
        )

    clipped_lines = rf"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\08_Data_Development\CVIN Bio Query Outputs\SHP\Seg{Segment}_FederalClip.shp"

    arcpy.analysis.Clip(
        in_features=InputLayer,
        clip_features=federal_lands_local,
        out_feature_class=clipped_lines
    )

    ClippedLayer = f"Seg{Segment}_FederalClip"
    
    arcpy.management.MakeFeatureLayer(
        clipped_lines,
        ClippedLayer
        )

    OutputKMZ = os.path.join(r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\07_KMZ\In", f"Seg{Subsegment}_FederalLands" + ".kmz")
    arcpy.conversion.LayerToKML(
        layer=ClippedLayer,
        out_kmz_file=OutputKMZ,
        layer_output_scale=0,
        is_composite="NO_COMPOSITE",
        image_size=1024,
        dpi_of_client=96,
        ignore_zvalue="CLAMPED_TO_GROUND"
        )
    
    for layer in input_layers:
        # Create a new selection layer
        selection_layer = f"{layer}_selection"
        arcpy.management.MakeFeatureLayer(layer, selection_layer)

        # Run Select By Location
        arcpy.management.SelectLayerByLocation(selection_layer,
                                               "INTERSECT",
                                               select_features=ClippedLayer,
                                               search_distance=SearchDistance,
                                               selection_type="NEW_SELECTION",
                                               invert_spatial_relationship="NOT_INVERT")

        # Check if there are selected features
        count = int(arcpy.management.GetCount(selection_layer).getOutput(0))
        if count > 0:
            selection_layers[layer] = selection_layer
        else:
            arcpy.management.Delete(selection_layer)

    # Exports selected records from input layers into feature class
    projectGDB = r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb"
    featureDataset = f"{projectGDB}\{Segment}"

    if not arcpy.Exists(featureDataset):
        arcpy.management.CreateFeatureDataset(
            out_dataset_path=projectGDB,
            out_name=f"Segment{Segment}",
            spatial_reference='PROJCS["NAD_1983_California_Teale_Albers",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",-4000000.0],PARAMETER["Central_Meridian",-120.0],PARAMETER["Standard_Parallel_1",34.0],PARAMETER["Standard_Parallel_2",40.5],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]];-16909700 -8597000 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision'
            )

    for layer, selection_layer in selection_layers.items():
        output_name = input_layers[layer]
        output_path = f"{OutputGDB}\\Seg{Subsegment}_{FileNameDist}_FederalClip_{output_name}"

        arcpy.management.CopyFeatures(selection_layer, output_path)
        layer_name = f"{output_name}_layer"

        arcpy.MakeFeatureLayer_management(output_path, layer_name)
        output_kmz = os.path.join(f"{out_kmz_file}", f"Seg{Subsegment}_{FileNameDist}_FederalClip_{output_name}" + ".kml")

        arcpy.conversion.LayerToKML(
            layer_name,
            output_kmz,
            layer_output_scale=0,
            is_composite="NO_COMPOSITE",
            dpi_of_client=96,
            ignore_zvalue="CLAMPED_TO_GROUND"
            )
        arcpy.Delete_management(layer_name)

# Federal Lands clipping option not enabled:
else:
    OutputKMZ = os.path.join(r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\07_KMZ\In", f"Seg{Subsegment}" + ".kmz")
    arcpy.conversion.LayerToKML(
        layer=InputLayer,
        out_kmz_file=OutputKMZ,
        layer_output_scale=0,
        is_composite="NO_COMPOSITE",
        image_size=1024,
        dpi_of_client=96,
        ignore_zvalue="CLAMPED_TO_GROUND"
        )

    for layer in input_layers:
        # Create a new selection layer
        selection_layer = f"{layer}_selection"
        arcpy.management.MakeFeatureLayer(layer, selection_layer)

        # Run Select By Location
        arcpy.management.SelectLayerByLocation(selection_layer,
                                               "INTERSECT",
                                               select_features=InputLayer,
                                               search_distance=SearchDistance,
                                               selection_type="NEW_SELECTION",
                                               invert_spatial_relationship="NOT_INVERT")

        # Check if there are selected features
        count = int(arcpy.management.GetCount(selection_layer).getOutput(0))
        if count > 0:
            selection_layers[layer] = selection_layer
        else:
            arcpy.management.Delete(selection_layer)
            
    # Exports selected records from input layers into feature class and then into KML
    projectGDB = r"\\na.aecomnet.com\lfs\AMER\SanDiego-USSDG1\DCS\GIS\Projects\60736282_CVIN\01_data\ProjectGDB.gdb"
    featureDataset = f"{projectGDB}\{Segment}"

    if not arcpy.Exists(featureDataset):
        arcpy.management.CreateFeatureDataset(
            out_dataset_path=projectGDB,
            out_name=f"Segment{Segment}",
            spatial_reference='PROJCS["NAD_1983_California_Teale_Albers",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",-4000000.0],PARAMETER["Central_Meridian",-120.0],PARAMETER["Standard_Parallel_1",34.0],PARAMETER["Standard_Parallel_2",40.5],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]];-16909700 -8597000 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision'
            )

    for layer, selection_layer in selection_layers.items():
        output_name = input_layers[layer]
        output_path = f"{OutputGDB}\\Seg{Subsegment}_{FileNameDist}_{output_name}"

        arcpy.management.CopyFeatures(selection_layer, output_path)
        layer_name = f"{output_name}_layer"

        arcpy.MakeFeatureLayer_management(output_path, layer_name)
        output_kmz = os.path.join(f"{out_kmz_file}", f"Seg{Subsegment}_{FileNameDist}_{output_name}" + ".kml")

        arcpy.conversion.LayerToKML(
            layer_name,
            output_kmz,
            layer_output_scale=0,
            is_composite="NO_COMPOSITE",
            dpi_of_client=96,
            ignore_zvalue="CLAMPED_TO_GROUND"
            )
        arcpy.Delete_management(layer_name)
