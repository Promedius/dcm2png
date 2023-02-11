from dcm2png import extract
import imageio.v3 as iio
import io
from typing import BinaryIO, Union

def to_png(file_path: Union[str, BinaryIO], windowing: extract.Windowing = None) -> bytes:
    buf = io.BytesIO()

    iio.imwrite(buf, extract.extract(file_path, windowing), extension=".png")

    return buf.getbuffer().tobytes()