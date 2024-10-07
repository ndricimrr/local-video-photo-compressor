# Local Video Compressor

## User Interface

### In Progress
<img width="617" alt="Screenshot 2024-10-06 at 20 19 26" src="https://github.com/user-attachments/assets/bb7e5e90-7c72-47cb-9e9c-5bd8f2cc5618">

### Paused
<img width="614" alt="Screenshot 2024-10-06 at 20 19 36" src="https://github.com/user-attachments/assets/1d827d59-2d0e-4b25-b355-f801cd542d3d">

A simple app to convert videos locally to lower sized ones.

Can be used when needing to save on space with unnecessary large videos that you have in your hard disk or external one.

Files supported so far:

- _.mkv_
- _.mp4_
- _.avi_
- _.mov_

# App Idea & Future perspective:

The problem most of us face nowadays is that smartphones make videos which end up being very large in size. Sooner or later your phone is full and you have to transfer them to your PC or some other place to free up space.
Cloud Storage came to the rescue as the solution but not all can afford it or find it as a feasible solution.
You pay to have your data saved and usually with a subscription and not a single time payment. The irony is that your Storage Provider probably squeezed something in the T&C to allow them to use your personal pictures for training reasons. You are not getting paid for the usage of your pictures in training, so you are paying twice the price.

Current implementation is CMD only, proposed solution is to offer an User Interface, that is simple to use: Simply drag and drop a folder on the Desktop App, and the folder should contains all the videos you want to convert and subfolders with videos as you wish.

It then converts the videos it found to lower file size in place. You only drag & drop the folder and the app should recursively convert everything it finds as supported file types for videos.

At the end instead of 12 GB of cat videos, you end up with 100 MB maybe, sparing quite a lot of space for you.

You saved your memories and also saved some money, thats the goal.

# How to Run

```
python convert.py
```

# Requirements

- Currently runs on Windows only
- Make sure to have the latest version of python
- Install wmi :
  `pip install WMI`
