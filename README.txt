# Reproject to WGS84 (EPSG:4326)
gdf = gdf.to_crs("EPSG:4326")
print("Reprojected CRS:", gdf.crs)

# Save reprojected shapefile for future use
gdf.to_file("reprojected_HKDistrict18.shp", driver="ESRI Shapefile")
---

Explanation of Auxiliary Files
.shp: Contains the geometric data (e.g., points, lines, polygons).
.cpg: Stores the character encoding of the attribute data.
.dbf: Contains the attribute data in tabular form.
.shx: Index of the geometry.
.prj: Describes the CRS (Coordinate Reference System).
When you reproject the shapefile using geopandas, it updates:

Geometries (in .shp and .shx).
CRS definition (in .prj).
The .dbf and .cpg files are unaffected by reprojection since they only store attribute data.

How Geopandas Handles Reprojection
When you run gdf.to_crs("EPSG:4326") and save the reprojected file with gdf.to_file(), geopandas:

Writes updated geometries to the .shp and .shx files.
Updates the CRS information in the .prj file.
Retains the existing .dbf and .cpg files without modification.
Reproject Entire Shapefile
When you reproject and save the shapefile using geopandas, all these components are automatically re-created. For example:

python
Copy
Edit
gdf.to_file("reprojected_HKDistrict18.shp", driver="ESRI Shapefile")
The command saves all necessary files (.shp, .shx, .dbf, .cpg, .prj) into the same directory, with updated CRS information and geometries.