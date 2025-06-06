# Local Video & Photo Compressor

An overly simple **offline** desktop app to compress videos & images locally. Just drag your folder full of videos and images and nested folders and hit "Start". A new folder with same structure will be created with your videos and photos greatly compressed.

## User Interface

### Start Phase

<img width="615" alt="start" src="screenshots/initial.png">

### In Progress

<img width="615" alt="Screenshot 2024-10-12 at 17 29 11" src="screenshots/in_progress.png">

### Paused

<img width="614" alt="Screenshot 2024-10-12 at 17 28 55" src="screenshots/paused.png">

## Overview

The **Local Video & Photo Compressor** is an open source lightweight tool designed to help users reduce the size of their video and image files without relying on pricey cloud storage solutions. It provides a simple drag-and-drop interface for compressing videos and images, making it accessible to users with **no technical expertise**.

## Features

- **Drag-and-Drop Interface**: Easily compress entire folders of videos and images.
- **Recursive Conversion**: Automatically processes subfolders and supported file types.
- **Cross-Format Support**: Works with a variety of video and image formats.
- **Local Processing**: No need for cloud compression SaaS; all processing is done locally on your machine.
- **Fail Safe Compression**: If the app crashes or your Laptop/PC shuts down unexpectedly you can still continue where you left off. (After each item is compressed, its marked as "compressed" in a "table".)

## Supported File Formats

The app currently supports the following file formats:

### Videos:

Popular video file types:

- `.mkv`
- `.mp4`
- `.avi`
- `.mov`
  and more from the range that ffmpeg [supports](https://en.wikipedia.org/wiki/FFmpeg#Muxers).

### Images:

- `.jpeg`
- `.jpg`
- `.png`
- `.gif`

All other file types not supported, are simply copied over to the new folder as is and not lost.

## Motivation

### The Problem:

Modern smartphones produce high-quality videos that take up significant storage space. Over time, this leads to full storage on your device, requiring you to transfer files to a PC or external storage. While cloud storage offers a solution, it often comes with recurring subscription costs and privacy concerns.

_Practically, if you can compress 100GB of video/images to 3GB you could delay having to buy a Cloud data subscription by many years saving quite a lot on unecessary monthly fees._

There's no reason why you can't fit ~5-10 years of images/videos in one device before having to buy cloud subscriptions. This can be achieved if your files are compressed.

### The Solution:

The **Local Video & Photo Compressor** provides a simple, free open-source solution. By compressing videos locally, you can:

- Save storage space.
- Avoid/Reduce recurring cloud storage fees.
- Maintain control over your personal data.
- Use a free open source tool that works **100% offline** and requires no weird online Video Compression SaaS with hidden junk fees & and non-privacy friendly T&C.

---

## How to Use

# Requirements

- Currently the app was built and tested for **MacOS** only
- Works with **Python 3.13.1** and above.
- Install pacakges through `requirements.txt` :

  `python3 -m pip install -r requirements.txt`

  or install separatey:
  `piexif` - for
  `Pillow` - for image compressions
  `PyQt6` - for the UI

- This app requires [ffmpeg](https://github.com/FFmpeg/FFmpeg) to be installed on your system for video compressions. Follow these steps to install it on **macOS**:

```
  brew install ffmpeg
```

# Start the App

1. Clone or download the repository.

2. Run the app using the following command:
   ```bash
   python3 macos/app/main.py
   ```

# App Idea & Future perspective:

The problem most of us face nowadays is that smartphones make videos which end up being very large in size. Sooner or later your phone is full and you have to transfer them to your PC or some other place to free up space.
Cloud Storage came to the rescue as the solution but not all can afford it or find it as a feasible solution long-term.

You pay to have your data saved and usually with a subscription. The irony is that your Storage Provider probably squeezed something in the T&C to allow them to use your personal pictures for training reasons. You are not getting paid for the usage of your pictures in training, so you are paying twice the price.

Proposed solution is to offer an User Interface, that is simple to use: Simply drag and drop a folder on the Desktop App, and the folder should contain all the videos you want to convert and subfolders with videos as you wish.

It then converts the videos and images it found to lower file size in a new folder with the same exact file structure. You only drag & drop the folder and the app should recursively convert everything it finds as supported file types for videos and images.

At the end, instead of 12 GB of cat videos, you end up with 100 MB maybe, sparing quite a lot of space for you.

You saved your memories longer and also saved some money, thats the goal.

## End Goal

Should be super simple and basic to use for people with no technical expertise. That means **1-click install** should be a must. Drag & Drop + 1 Click should be all that the users should do ideally. Advanced solutions already exist.

# Contributions

Contributions are more than welcome. Plenty of work is yet to be done. Simply pick an **Issue** and open a **PR**.
