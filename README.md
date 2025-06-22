# PMB Image Viewer & Web Converter

This is a custom image viewer and web-based converter for the .pmb file format.

## Setup

Run the setup script to prepare your environment:

```
python setup.py
```

This will:
1. Create necessary directories
2. Generate a PMB file icon
3. Check and install Flask if needed
4. Check and install PyInstaller if needed

## Web Converter

The web converter allows you to upload images through a browser interface and convert them to PMB format.

### Running the Web Converter

**Option 1: Run directly with Python**
1. Double-click `run_web_converter.bat`
2. Open your browser and go to http://localhost:5000

**Option 2: Run packaged executable**
1. Build the web converter: Double-click `build_web_converter.bat`
2. Once built, run with `launch_web_converter.bat`
3. Your browser will automatically open to http://localhost:5000

With either option:
1. Upload any image (PNG, JPG, JPEG, etc.)
2. Download the converted PMB file

## PMB Viewer Setup

To enable double-clicking PMB files to open them:

1. Build the standalone viewer: `pyinstaller --onefile --noconsole --name pmb_viewer main.py`
2. Double-click the `pmb_association.reg` file to add the PMB file association to your Windows Registry
3. Click "Yes" when Windows asks for confirmation
4. Now you can double-click any .pmb file to open it with the viewer

## Custom Icon

The setup process creates a custom icon for .pmb files. After applying the registry settings, your .pmb files should display with this icon in Windows Explorer.

## Manual Usage

If you prefer not to use the registry association, you can run the viewer from the command line:
```
python main.py your_file.pmb
```
Or with the executable:
```
dist\pmb_viewer.exe your_file.pmb
```

## Troubleshooting

If the file association doesn't work:

1. Make sure the path to the executable in the registry file matches where PyInstaller created it
2. Verify that the icon file exists at the specified path
3. You might need to restart your file explorer or computer for the changes to take effect

For web converter issues:
1. Make sure the templates folder is in the same directory as the executable
2. Check that ports aren't blocked by your firewall or antivirus
3. The uploads and pmb_files folders will be created in the same directory as the executable 