from ffmpeg_quality_metrics import FfmpegQualityMetrics

def get_image_vmaf(compressed_path: str, reference_path: str):
    """
    Calculates the VMAF score between a compressed image and a reference image.
    
    Args:
        compressed_path (str): Path to the compressed image (.heic or .jpg).
        reference_path (str): Path to the original reference image (.tif).
        
    Returns:
        float: The VMAF score (0-100, where 100 is identical to the reference).
               Returns None if the calculation fails.
    """
    try:
        ## FfmpegQualityMetrics expects the distorted (compressed) file first, 
        ## followed by the reference file.
        ffqm = FfmpegQualityMetrics(compressed_path, reference_path, framerate = 1)
        
        ## Calculate only the VMAF metric to save processing time
        metrics = ffqm.calculate(["vmaf"])
        
        ## Extract the VMAF data. It returns a list of dictionaries per frame.
        vmaf_data = metrics.get("vmaf", [])
        
        if(not vmaf_data):
            print(f"Warning: No VMAF data returned for {compressed_path}")
            return None
            
        return vmaf_data[0]["vmaf"]
        
    except Exception as e:
        print(f"Error calculating VMAF for {compressed_path}: {e}")
        return None


if(__name__ == "__main__"):
    compressed = "DSC02435_03.heic"
    original = "DSC02435.tif"
    
    score = get_image_vmaf(compressed, original)
    
    if(score is not None):
        print(f"VMAF Score: {score}")
