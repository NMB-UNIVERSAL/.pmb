# PMB Image Converter

A React application that converts any image file to the custom PMB file format.

## What is PMB?

PMB is a custom image file format that stores:
- The image name on the first line
- Width and height dimensions on the second line
- RGB pixel data for each pixel with an "N" marking the end of each row

## Features

- Convert any image format (PNG, JPG, JPEG, etc.) to PMB format
- Client-side only processing (no server required)
- Simple and intuitive user interface
- Instant conversion and download

## How to Install and Run

1. Convert images from any type to .pmb by visiting this site, "https://pmb-converter.netlify.app/"

2. Once installed install the latest release of the .pmb viewer form the releases page, and extract it and palce it anyhwere

3. Within the zip you downloaded double click the pmb_association.reg

4. Once all is done and you converted a pciture you cna open it by double clicking


## Technical Details

The conversion process works by:
1. Loading the image into a canvas element
2. Reading the pixel data from the canvas
3. Formatting the data according to the PMB specification
4. Creating a downloadable text file with the PMB content

All processing is done client-side in the browser using JavaScript, without any backend server requirements.

## License

MIT 