---
layout: default
title: Video Demo
description: Video demonstrations of the Financial Data Extractor application
nav_order: 6
---

# Video Demonstrations

This page contains video demonstrations of the Financial Data Extractor application in action. Watch these videos to see the complete workflow from document discovery to compiled financial statements.

## Introduction Video

This video provides an overview of the Financial Data Extractor platform, including the main features and user interface.

<div class="video-container">
    <video controls preload="metadata" playsinline webkit-playsinline>
        <source src="{{ '/assets/video/intro.mp4' | relative_url }}" type="video/mp4">
        <p>Your browser does not support the video tag. <a href="{{ '/assets/video/intro.mp4' | relative_url }}">Download the video</a> instead.</p>
    </video>
</div>

<p class="text-small text-grey-dk-000 mb-0"><em>Note: The introduction video is large (371MB). Please allow time for buffering. If playback issues occur, try refreshing the page or downloading the video directly.</em></p>

## Results Video

This video showcases the results and output of the financial data extraction process, demonstrating the compiled financial statements and data visualization features.

<div class="video-container">
    <video controls preload="metadata" playsinline webkit-playsinline>
        <source src="{{ '/assets/video/results.mp4' | relative_url }}" type="video/mp4">
        <p>Your browser does not support the video tag. <a href="{{ '/assets/video/results.mp4' | relative_url }}">Download the video</a> instead.</p>
    </video>
</div>

## Video Features

### Introduction Video Covers

- Platform overview and architecture
- User interface navigation
- Company selection and management
- Document discovery workflow
- Extraction process initiation

### Results Video Covers

- Compiled financial statements visualization
- Income Statement, Balance Sheet, and Cash Flow views
- Multi-year data compilation
- Data normalization features
- Interactive data exploration

## Troubleshooting Video Playback

If you're experiencing issues playing the videos:

### Common Issues

1. **Large File Size**: The introduction video is 371MB. Your browser may need time to buffer before playback starts.

   - Wait a few moments after clicking play
   - Check your internet connection speed
   - Try right-clicking the video and selecting "Save video as..." to download

2. **Browser Compatibility**: Ensure you're using a modern browser with HTML5 video support:

   - Chrome/Edge (Chromium) - Recommended
   - Firefox
   - Safari
   - Opera

3. **Local Development Server**: If viewing locally with Jekyll:

   - Ensure the Jekyll server is running: `bundle exec jekyll serve`
   - Videos should be accessible at `/financial-data-extractor/assets/video/`
   - Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

4. **Browser Console Errors**: Open browser developer tools (F12) and check the Console tab for any error messages.

5. **Alternative**: If videos won't play, you can download them directly:
   - [Download Introduction Video]({{ '/assets/video/intro.mp4' | relative_url }})
   - [Download Results Video]({{ '/assets/video/results.mp4' | relative_url }})

### GitHub Pages Deployment

When deployed to GitHub Pages, videos should work automatically. If issues persist:

- Verify the video files are committed to the repository
- Check that the file paths are correct
- Ensure GitHub Pages has processed the site (may take a few minutes after push)

## Related Documentation

To get started with the application after watching these videos:

1. **[Installation Guide](getting-started/installation.html)** - Set up your local environment
2. **[First Steps](getting-started/first-steps.html)** - Tutorial for your first extraction
3. **[Results Page](results.html)** - View static screenshots of the application
4. **[API Reference](api/reference.html)** - Explore programmatic access
