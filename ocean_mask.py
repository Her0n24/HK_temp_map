import numpy as np
from shapely.geometry import shape, Point, Polygon
from tqdm import tqdm
import os

def generate_ocean_mask(gdf,X, Y, Z, mask_file_path):
    """
    Generates a mask for ocean areas based on the provided GeoDataFrame and saves it to a file for subsequent use.

    Parameters:
    gdf (GeoDataFrame): The GeoDataFrame containing the polygons representing land areas.
    X (numpy.ndarray): The x-coordinates of the grid points.
    Y (numpy.ndarray): The y-coordinates of the grid points.
    Z (numpy.ndarray): The z-coordinates of the grid points.
    mask_file_path (str): The path where the mask file will be saved.

    Returns:
    numpy.ndarray: A mask array where ocean areas are marked with 1 and land areas with 0.
    """
    if not os.path.exists(mask_file_path):
        print("Ocean mask file does not exist. Generating a new one.")
        ocean_mask = np.ones_like(Z)
        total_iterations = len(gdf) * Z.shape[0] * Z.shape[1]
        
        with tqdm(total=total_iterations) as pbar:
            for _, row in gdf.iterrows():
                polygon = row['geometry']
                for i in range(Z.shape[0]):
                    for j in range(Z.shape[1]):
                        point = Point(X[i, j], Y[i, j])
                        if polygon.contains(point):
                            ocean_mask[i, j] = 0
                        pbar.update(1)
        
        np.save(mask_file_path, ocean_mask)
        print(f"Ocean mask saved to {mask_file_path}")
        return ocean_mask
    else:
        print(f"Ocean mask already exists at {mask_file_path}. Loading from file.")
        ocean_mask = np.load(mask_file_path)
        return ocean_mask

def load_ocean_mask(mask_file_path):
    """
    Loads the created ocean mask from a file.

    Parameters:
    mask_file_path (str): The path to the mask file.

    Returns:
    numpy.ndarray: The loaded ocean mask.
    """
    if os.path.exists(mask_file_path):
        print(f"Loading ocean mask from {mask_file_path}")
        return np.load(mask_file_path)
    else:
        raise FileNotFoundError(f"Ocean mask file not found at {mask_file_path}")