# dcm2png

## 개발 환경

* python: 3.8
* conda
* poetry

```
$ conda create -n dcm2png python=3.8
```

## 개발

### 테스트

* `test` 디렉토리 내에 테스트용 dicom 파일이 있는 `dicom` 디렉토리가 필요
* 아래 명령을 실행하면 `result` 디렉토리에 조건별 다이콤에서 추출한 이미지 파일 생성

```
dcm2png/test $ python test.py
```

### 특이 사항

* `from pydicom.pixel_data_handlers`에서 제공하는 함수들 중 일부를 수정하여 로컬 사본 사용
* `imageio`에서 1-bit monochrome 픽셀을 jpg로 저장하지 못 함

## 사용법

`to_png(file_path: Union[str, BinaryIO], windowing: {"center": int, "width": int} = None) -> bytes`

```python
import dcm2png

with open("dicom.png", "wb") as f:
    f.write(dcm2png.to_png("dicom.dcm", {"center": 60, "width": 400}))
```
