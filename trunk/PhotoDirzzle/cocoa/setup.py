"""
Script for building the example.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app

import glob
images = glob.glob('Images/*.tiff')
icons = glob.glob('Icons/*.icns')

plist = dict(
    CFBundleShortVersionString='PhotoDrizzle v0.1',
    CFBundleIconFile='PhotoDrizzle.icns',
    CFBundleGetInfoString='PhotoDrizzle v0.1',
    CFBundleIdentifier='org.fpierfed.PhotoDrizzle',
    CFBundleName='PhotoDrizzle',
)

setup(
    app=["main.py"],
    data_files=["English.lproj" ] + images + icons,
    options=dict(py2app=dict(plist=plist)),
)
