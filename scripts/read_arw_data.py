import rawpy
import exifread
import numpy as np

filename = "DSC02435.ARW"

print("=== RAW DATA ===")

with rawpy.imread(filename) as raw:

    raw_pixels = raw.raw_image
    print("Sensor array shape:", raw_pixels.shape)
    print("Data type:", raw_pixels.dtype)

    print("\nFirst 10x10 pixels:")
    print(raw_pixels[:10, :10])

    print("\nWhite level:", raw.white_level)
    print("Black level:", raw.black_level_per_channel)

    print("\nColor filter pattern:")
    print(raw.raw_pattern)

    print("\nVisible image size:")
    print(raw.sizes)

    print("\nCamera white balance:")
    print(raw.camera_whitebalance)

    print("\nDaylight white balance:")
    print(raw.daylight_whitebalance)

    print("\nColor matrix:")
    print(raw.color_matrix)

    print("\nRAW pixel statistics:")
    print("min:", np.min(raw_pixels))
    print("max:", np.max(raw_pixels))
    print("mean:", np.mean(raw_pixels))


print("\n=== EXIF METADATA ===")

with open(filename, "rb") as f:

    tags = exifread.process_file(f)

    for tag in tags.keys():
        if(tag == 'JPEGThumbnail'):
            continue
        print(f"{tag}: {tags[tag]}")


print("\n=== EMBEDDED JPEG PREVIEW ===")

with rawpy.imread(filename) as raw:

    try:
        thumb = raw.extract_thumb()

        if thumb.format == rawpy.ThumbFormat.JPEG:
            out = "embedded_preview.jpg"

            with open(out, "wb") as f:
                f.write(thumb.data)

            print("Saved:", out)

        elif thumb.format == rawpy.ThumbFormat.BITMAP:
            out = "embedded_preview.ppm"

            with open(out, "wb") as f:
                f.write(thumb.data)

            print("Saved:", out)

    except rawpy.LibRawNoThumbnailError:
        print("No embedded preview found")


print("\n=== RAW FILE SUMMARY ===")

with open(filename, "rb") as f:
    tags = exifread.process_file(f)
    print("Camera:", tags.get('Image Make'), tags.get('Image Model'))
    print("ISO:", tags.get('EXIF ISOSpeedRatings'))
    print("Shutter:", tags.get('EXIF ExposureTime'))
    print("Aperture:", tags.get('EXIF FNumber'))
    print("Focal length:", tags.get('EXIF FocalLength'))
    print("Timestamp:", tags.get('EXIF DateTimeOriginal'))

