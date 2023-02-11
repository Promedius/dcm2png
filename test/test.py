import dcm2png
import os
import shutil
import traceback

if os.path.exists("result"):
    shutil.rmtree("result")

os.mkdir("result")
print(">> --- without custom windowing ---")
os.mkdir("result/without-custom-windowing")

for x in os.listdir("dicom"):
    print(f">> {x}")

    try:
        with open(f"result/without-custom-windowing/{x}.jpg", "wb") as f:
            f.write(dcm2png.to_png(f"dicom/{x}"))
    except:
        traceback.print_exc()

    print(f"<< {x}\n")

print("<< --- without custom windowing ---\n")
print(">> --- with custom windowing ---")
os.mkdir("result/with-custom-windowing")

for x in os.listdir("dicom"):
    print(f">> {x}")

    try:
        with open(f"result/with-custom-windowing/{x}.jpg", "wb") as f:
            f.write(dcm2png.to_png(f"dicom/{x}", {"center": 60, "width": 400}))
    except:
        traceback.print_exc()

    print(f"<< {x}\n")

print("<< --- with custom windowing ---")