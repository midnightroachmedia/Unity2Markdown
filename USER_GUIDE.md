# Unity2Markdown User Guide

Unity2Markdown is an application designed to convert Unity documentation from HTML format to Markdown. This guide will walk you through the process of using the application effectively.

## Table of Contents

1. [Starting the Application](#starting-the-application)
2. [Selecting Input Files](#selecting-input-files)
3. [Choosing the Output Directory](#choosing-the-output-directory)
4. [Conversion Options](#conversion-options)
5. [Starting the Conversion](#starting-the-conversion)
6. [Monitoring Progress](#monitoring-progress)
7. [Completing the Conversion](#completing-the-conversion)
8. [Troubleshooting](#troubleshooting)

## Starting the Application

To start Unity2Markdown, open a terminal or command prompt, navigate to the directory containing the `unity2markdown.py` file, and run:

```
python unity2markdown.py
```

The application window will appear, displaying the user interface.

## Selecting Input Files

1. Click the "Select HTML Files" button.
2. In the file dialog that appears, navigate to the directory containing your Unity HTML documentation files.
3. Select one or multiple HTML files you wish to convert.
4. Click "Open" to confirm your selection.

The status label will update to show how many files you've selected.

## Choosing the Output Directory

1. Click the "Select Output Directory" button.
2. In the directory dialog that appears, choose or create a directory where you want the converted Markdown files to be saved.
3. Click "Select Folder" to confirm your choice.

The status label will update to show the selected output directory.

## Conversion Options

Unity2Markdown offers two conversion options:

1. **Create separate files**: This option will create one Markdown file for each input HTML file.
2. **Merge into single file**: This option will combine all input HTML files into a single Markdown file.

Select the radio button next to your preferred option.

## Starting the Conversion

Once you've selected your input files, output directory, and conversion option, click the "Convert" button to begin the conversion process.

## Monitoring Progress

During the conversion:

- The progress bar will fill up to indicate the overall progress.
- The file counter will show which file is currently being processed and the total number of files.
- The status label will display "Converting..."

You can click the "Cancel" button at any time to stop the conversion process.

## Completing the Conversion

When the conversion is complete:

- If you selected "Create separate files", a popup will inform you that the conversion is complete.
- If you selected "Merge into single file", a popup will ask you to enter a name for the merged file. Enter a name and click OK to save the file, or click Cancel to discard the merged content.

After the conversion is complete, the application will reset, allowing you to perform another conversion if desired.

## Troubleshooting

If you encounter any errors during the conversion process:

- Check that you have selected valid Unity HTML documentation files.
- Ensure you have write permissions for the selected output directory.
- Verify that you have a stable internet connection if the HTML files contain external resources.

If problems persist, please check the console output for any error messages and report the issue to the developers.

Remember that the converted Markdown files will not contain any links, images, or complex HTML elements. The conversion focuses on preserving the textual content and basic structure of the documentation.
