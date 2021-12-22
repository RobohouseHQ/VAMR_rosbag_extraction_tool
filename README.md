# Rosbag extraction tool for VAMR project
Python scripts used to extract data from rosbags.

* This tool expects rosbags that have been recorded by the Versavis setup and have at least the following two topics:
    * ```/versavis/cam0/image_raw```
    * ```/versavis/imu```

## How to run
* Drop the bag files you want to extract data from in the same directory as this script
* Run the script
```bash
python extract_data.py 
```
* The script will:
    * create a new directory with the same name as your bagfile
    * save a copy of the initial bag file in this new directory
    * save a separate ```.csv``` file for every non-image topic found in the rosbag
    * create an ```images``` subfolder
    * extract all the images in the image topic in this subfolder, as ```.png``` files with the following naming:
    ``` image_<image number>_<ros timestamp>.png```

> Note: the timestamp helps match the images with the corresponding IMU message as the two are synced using the ```versavis``` package
