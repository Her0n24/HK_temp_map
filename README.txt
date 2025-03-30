To run the Main Script:
python main.py 

Expected Output:
The script will generate a temperature map and save it in the output/ directory.
Example output file: output/HK_temp_map_newcolor_2025033012.png.

Structure:
HK_temp_map/
├── main.py                # Main script to run the project
├── constants.py           # Contains project constants
├── data_loader.py         # Handles data loading and downloading
├── ocean_mask.py          # Generates and loads ocean masks
├── plotter.py             # Handles plotting and visualization
├── input/                 # Input files (e.g., shapefiles, CSVs)
├── output/                # Output files (e.g., generated maps)
├── requirements.txt       # Python dependencies
└── [README.txt](http://_vscodecontentref_/0)             # Project documentation