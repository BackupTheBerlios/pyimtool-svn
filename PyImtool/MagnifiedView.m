#import "MagnifiedView.h"

@interface MagnifiedView (Private)

- (void)updateMagnifiedViewIfNeeded;
- (void)updateMagnifiedView;
- (void)drawCrosshair;

- (PixMapHandle)screenshotOfDisplay: (CGDirectDisplayID)display usingRect: (NSRect)sourceRect destinationSize: (NSSize)destinationSize;

- (CGPoint)mousePosition;
- (CGDirectDisplayID)displayWithPoint: (CGPoint)point;

- (void)setUpdateTimer: (NSTimer *)newUpdateTimer;
- (void)setContext: (CGContextRef)context width: (float)width color: (NSColor *)color;

@end

@implementation MagnifiedView

- (id)initWithFrame: (NSRect)frameRect
{

    [super initWithFrame: frameRect];
    
    magnification = 2;
    
    crosshairSize = 10;
    
    updateInterval = 0.05;
    
    return self;

}

- (void)drawRect: (NSRect)rect
{

    if (updateTimer)
    {
    
        [self updateMagnifiedView];
        
        if (crosshairSize)
        {
        
            [self drawCrosshair];
        
        }
    
    }

}

- (void)dealloc
{

    [self stop];
    
    [super dealloc];

}

- (void)startWithMagnification: (int)newMagnification crosshairSize: (int)newCrosshairSize updateInterval: (NSTimeInterval)newUpdateInterval
{

    magnification = newMagnification;
    
    crosshairSize = newCrosshairSize;
    
    updateInterval = newUpdateInterval;
    
    [self start];

}

- (void)start
{

    if ((fmod([self bounds].size.width, 2) > 0 || fmod([self bounds].size.height, 2) > 0) || [self bounds].size.width != [self bounds].size.height)
    {
    
        NSLog(@"MagnifiedView Error: view size must be an even-number perfect square, for example, 64x64 or 128x128, not 65x65 or 128x123.");
        
        [self stop];
        
        return;
    
    }
    
    [self setUpdateTimer: [[NSTimer scheduledTimerWithTimeInterval: updateInterval target: self selector: @selector(updateMagnifiedViewIfNeeded) userInfo: nil repeats: YES] retain]];

}

- (void)stop
{

    [self setUpdateTimer: nil];

}

- (int)magnification
{

    return magnification;

}

- (int)crosshairSize
{

    return crosshairSize;

}

- (NSTimeInterval)updateInterval
{

    return updateInterval;

}

- (void)setMagnification: (int)newMagnification
{

    magnification = newMagnification;

}

- (void)setCrosshairSize: (int)newCrosshairSize
{

    crosshairSize = newCrosshairSize;

}

- (void)setUpdateInterval: (NSTimeInterval)newUpdateInterval
{

    if (updateInterval != newUpdateInterval)
    {
    
        updateInterval = newUpdateInterval;
        
        if (updateTimer)
        {
        
            [self start];
        
        }
    
    }

}

- (void)updateMagnifiedViewIfNeeded
{

    if (oldMousePosition.x != [self mousePosition].x || oldMousePosition.y != [self mousePosition].y)
    {
    
        /* We only want to update when the mouse moves... sure the display could update without the mouse moving, shh. */
        
        [self setNeedsDisplay: YES];
        
        oldMousePosition = [self mousePosition];
    
    }

}

- (void)updateMagnifiedView
{

    CGDirectDisplayID currentDisplay = [self displayWithPoint: [self mousePosition]];
    
    NSSize destinationSize = NSMakeSize([self bounds].size.width, [self bounds].size.height);
    
    NSRect sourceRect;
    
    PixMapHandle magnifiedScreenPixMap;
    
    Ptr pixBaseAddress;
    
    NSBitmapImageRep *bitmapRep;
    
    int x = [self mousePosition].x - (([self bounds].size.width / magnification) / 2),
    y = [self mousePosition].y - (([self bounds].size.height / magnification) / 2);
    
    if (x < CGDisplayBounds(currentDisplay).origin.x)
    {
    
        x = CGDisplayBounds(currentDisplay).origin.x;
    
    }
    
    else if (x + ([self bounds].size.width / magnification) > CGDisplayBounds(currentDisplay).origin.x + CGDisplayPixelsWide(currentDisplay))
    {
    
        x = (CGDisplayBounds(currentDisplay).origin.x + CGDisplayPixelsWide(currentDisplay)) - floor([self bounds].size.width / magnification);
    
    }
    
    if (y < CGDisplayBounds(currentDisplay).origin.y)
    {
    
        y = CGDisplayBounds(currentDisplay).origin.y;
    
    }
    
    else if (y + ([self bounds].size.height / magnification) > CGDisplayBounds(currentDisplay).origin.y + CGDisplayPixelsHigh(currentDisplay))
    {
    
        y = (CGDisplayBounds(currentDisplay).origin.y + CGDisplayPixelsHigh(currentDisplay)) - floor([self bounds].size.height / magnification);
    
    }
    
    sourceRect = NSMakeRect(x, y, [self bounds].size.width / magnification, [self bounds].size.height / magnification);
    
    magnifiedScreenPixMap = [self screenshotOfDisplay: currentDisplay usingRect: sourceRect destinationSize: destinationSize];
    
    pixBaseAddress = GetPixBaseAddr(magnifiedScreenPixMap) + 1;
    
    bitmapRep = [[NSBitmapImageRep alloc] initWithBitmapDataPlanes: (unsigned char **)&pixBaseAddress
    pixelsWide: destinationSize.width pixelsHigh: destinationSize.height bitsPerSample: 8 samplesPerPixel: 3
    hasAlpha: NO isPlanar: NO colorSpaceName: NSDeviceRGBColorSpace bytesPerRow: (destinationSize.width * CGDisplayBitsPerPixel(currentDisplay)) / 8
    bitsPerPixel: CGDisplayBitsPerPixel(currentDisplay)];
    
    [self lockFocus];
    
    [bitmapRep draw];
    
    [self unlockFocus];
    
    LockPixels(magnifiedScreenPixMap);
    
    DisposePtr((*magnifiedScreenPixMap)->baseAddr);
    
    UnlockPixels(magnifiedScreenPixMap);
    
    DisposePixMap(magnifiedScreenPixMap);
    
    [bitmapRep release];

}

- (void)drawCrosshair
{

    CGContextRef context = (CGContextRef)[[NSGraphicsContext currentContext] graphicsPort];
    
    [self setContext: context width: 2 color: [NSColor blackColor]];
    
    CGContextSaveGState(context);
    
    CGContextMoveToPoint(context, ([self bounds].size.width / 2) - (crosshairSize / 2), [self bounds].size.height / 2);
    
    CGContextAddLineToPoint(context, ([self bounds].size.width / 2) + (crosshairSize / 2), [self bounds].size.height / 2);
    
    CGContextStrokePath(context);
    
    CGContextMoveToPoint(context, [self bounds].size.width / 2, ([self bounds].size.height / 2) - (crosshairSize / 2));
    
    CGContextAddLineToPoint(context, [self bounds].size.width / 2, ([self bounds].size.height / 2) + (crosshairSize / 2));
    
    CGContextStrokePath(context);
    
    CGContextRestoreGState(context);

}

- (PixMapHandle)screenshotOfDisplay: (CGDirectDisplayID)display usingRect: (NSRect)sourceRect destinationSize: (NSSize)destinationSize
{

    Rect displayBounds, sourceBounds, destinationBounds;
    
    PixMapHandle screenshotPixMap = NewPixMap();
    
    BitMap displayBitmap;
    
    /* Setup rectangles */
    
    SetRect(&displayBounds, CGDisplayBounds(display).origin.x, CGDisplayBounds(display).origin.y,
    CGDisplayBounds(display).origin.x + CGDisplayBounds(display).size.width,
    CGDisplayBounds(display).origin.y + CGDisplayBounds(display).size.height);
    
    SetRect(&sourceBounds, sourceRect.origin.x, sourceRect.origin.y,
    sourceRect.origin.x + sourceRect.size.width, sourceRect.origin.y + sourceRect.size.height);
    
    SetRect(&destinationBounds, 0, 0, destinationSize.width, destinationSize.height);
    
    /* Setup display and final-product BitMaps */
    
    displayBitmap.baseAddr = CGDisplayBaseAddress(display);
    
    displayBitmap.rowBytes = (CGDisplayPixelsWide(display) * CGDisplayBitsPerPixel(display)) / 8;
    
    displayBitmap.bounds = displayBounds;
    
    (*screenshotPixMap)->baseAddr = NewPtr((unsigned long)((destinationSize.width * CGDisplayBitsPerPixel(display)) / 8) * destinationSize.height);
    
    (*screenshotPixMap)->rowBytes = (short)((destinationSize.width * CGDisplayBitsPerPixel(display)) / 8) | 0x8000;
    
    (*screenshotPixMap)->bounds = destinationBounds;
    
    /* Finally copy the pixels from the display into the screenshotBitmap variable */
    
    LockPixels(screenshotPixMap);
    
    CopyBits(&displayBitmap, (BitMap *)*screenshotPixMap, &sourceBounds, &destinationBounds, srcCopy, NULL);
    
    UnlockPixels(screenshotPixMap);
    
    return screenshotPixMap;

}

- (CGPoint)mousePosition
{

    return CGPointMake([NSEvent mouseLocation].x, CGDisplayPixelsHigh(CGMainDisplayID()) - [NSEvent mouseLocation].y);

}

- (CGDirectDisplayID)displayWithPoint: (CGPoint)point
{

    CGDirectDisplayID displayWithPoint;
    
    CGDisplayCount displayCount = 0;
    
    CGGetDisplaysWithPoint(point, 1, &displayWithPoint, &displayCount);
    
    return displayWithPoint;

}

- (void)setUpdateTimer: (NSTimer *)newUpdateTimer
{

    if (updateTimer)
    {
    
        [updateTimer invalidate];
        
        [updateTimer release];
    
    }
    
    updateTimer = newUpdateTimer;

}

- (void)setContext: (CGContextRef)context width: (float)width color: (NSColor *)color
{

    NSColor *calibratedColor = [color colorUsingColorSpaceName: NSDeviceRGBColorSpace];
    
    CGContextSetLineWidth(context, width);
    
    CGContextSetRGBStrokeColor(context, [calibratedColor redComponent], [calibratedColor greenComponent], [calibratedColor blueComponent], 1.0);
    
    [[NSGraphicsContext currentContext] setShouldAntialias: NO];

}

@end