#!/usr/bin/env python
# 
# This code is the optimization of SeDDaRA Algorithm.
# 
# Yating Chuang, Laboratory of RF-MW Photonics
# Department of Physics, National Cheng Kung University
#

from scipy import *
import sys


# Load the input image and resize it to 300x300
f1=imread('saturn.jpg', flatten=1)
f=toimage(imresize(f1, size=(300, 300)).astype(Float))

# Blur the image with a 11x11 kernel
[m,n]=f.size
point=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
h1=zeros((11, 11), Float)
for i in point:
    for j in point:
        h1[i,j]=1./(pi*(float(i+1)**2 + float(j+1)**2))
f = fromimage(f)
g=signal.convolve2d(f,h1).astype(UInt8)

# Remove the extra padding from g
g = g[0:300, 0:300]

toimage(g).save('g.tiff')

# Extend h1 to the right and to the top
h = zeros((300, 300), Float)
h[0:11,0:11] = h1.astype(Float)

# Do a Fourier transfor of the original image, the smoothed one and the 
# "extended" kernel.
G=fft2(g.astype(Float))
F=fft2(f.astype(Float64))
D=fft2(h.astype(Float))

print (G[1, 1])
print (g[1, 1])

# Compute the power spectrum
SG=abs(G)**2/(m*n)
SF=abs(F)**2/(m*n)
KD=0.14711
a=0.19955
D1=KD*(abs(SG)**(a/2))

F1=G/D1
SF1=abs(F1)**2/(m*n)
f2=ifft2(F1)

imshow(F.real.astype(UInt8))

# imshow(f)
# imshow(g)
# imshow(f2.astype(UInt8))




























