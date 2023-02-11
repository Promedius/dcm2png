import pydicom
from .util import apply_modality_lut, apply_voi_lut, apply_color_lut, convert_color_space, apply_windowing # pydicom에서 제공하는 것이 아닌 로컬 수정본 사용중
from pydicom.uid import ImplicitVRLittleEndian
import numpy as np
from typing import BinaryIO, Union, TypedDict, Optional

class Windowing(TypedDict):
    center: int
    width: int

def extract(file_path: Union[str, BinaryIO], windowing: Optional[Windowing]=None) -> "np.ndarray":
    ds = pydicom.dcmread(file_path, force=True)

    try:
        _ = ds.file_meta.TransferSyntaxUID
    except:
        ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian

    pixel_array = apply_bits_stored(ds.pixel_array, ds)
    
    if ds.PhotometricInterpretation == "MONOCHROME1" or ds.PhotometricInterpretation == "MONOCHROME2":
        pixel_array = apply_modality_lut(pixel_array, ds)

        if windowing is None:
            pixel_array, windowing_done = apply_voi_lut(pixel_array, ds)
        else:
            ds.WindowCenter = windowing["center"]
            ds.WindowWidth = windowing["width"]
            pixel_array = apply_windowing(pixel_array, ds)
            windowing_done= True

        pixel_array = normalize_to_8bit(pixel_array, ds, not windowing_done)
    else:
        # NOTE: https://github.com/cornerstonejs/cornerstoneWADOImageLoader/blob/5583aa52bd50d56358cd7c876feee789fa1f1145/src/imageLoader/convertColorSpace.js#L26-L44
        if ds.PhotometricInterpretation == "RGB":
            pass
        elif ds.PhotometricInterpretation == "PALETTE COLOR":
            pixel_array = apply_color_lut(pixel_array, ds)
        elif ds.PhotometricInterpretation in ["YBR_FULL", "YBR_FULL_422", "YBR_ICT", "YBR_RCT"]:
            if ds.PhotometricInterpretation in ["YBR_FULL", "YBR_FULL_422"]:
                pixel_array = convert_color_space(pixel_array, ds.PhotometricInterpretation, "RGB")
        else:
            raise Exception(f"unsupported PhotometricInterpretation: '{ds.PhotometricInterpretation}'")

        # NOTE: 8bit RGB로 변환
        pixel_array = to_8bit(pixel_array)

    if len(pixel_array.shape) == 4:
        pixel_array = pixel_array[0]

    return pixel_array

def apply_bits_stored(pixel_array: "np.ndarray", ds: pydicom.Dataset):
    if ds.PixelRepresentation == 1:
        old_type = pixel_array.dtype
        pixel_array = pixel_array.astype(np.int32)
        shift = 32 - ds.BitsStored
        pixel_array = (pixel_array << shift) >> shift
        pixel_array = pixel_array.astype(old_type)

    return pixel_array

def normalize_to_8bit(pixel_array: "np.ndarray", ds: pydicom.Dataset, auto_windowing: bool):
    if auto_windowing:
        pixel_min = pixel_array.min()
        pixel_max = pixel_array.max()
    else:
        if ds.PixelRepresentation == 1:
            pixel_min = -(2 ** (ds.BitsStored - 1))
            pixel_max = 2 ** (ds.BitsStored - 1) - 1
        else:
            pixel_min = 0
            pixel_max = 2 ** ds.BitsStored - 1

        if "RescaleSlope" in ds and "RescaleIntercept"in ds:
            pixel_min = pixel_min * ds.RescaleSlope + ds.RescaleIntercept
            pixel_max = pixel_max * ds.RescaleSlope + ds.RescaleIntercept

    pixel_range = pixel_max - pixel_min

    if ds.PhotometricInterpretation == "MONOCHROME1":
        if pixel_range == 0: # NOTE: 한가지 값으로만 구성된 경우 해당 값을 흰색으로 취급
            pixel_array = 255
        else:
            pixel_array = 255 - (pixel_array - pixel_min) / pixel_range * 255
    else:
        if pixel_range == 0: # NOTE: 한가지 값으로만 구성된 경우 해당 값을 검은색으로 취급
            pixel_array = 0
        else:
            pixel_array = (pixel_array - pixel_min) / pixel_range * 255

    return pixel_array.astype(np.uint8)

def to_8bit(pixel_array: "np.ndarray"):
    if pixel_array.itemsize != 1:
        pixel_max = 2 ** (8 * pixel_array.itemsize) - 1
        pixel_array = pixel_array / pixel_max * 255
        pixel_array = pixel_array.astype(np.uint8)

    return pixel_array