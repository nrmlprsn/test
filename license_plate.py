import numpy as np
import cv2
from easyocr import Reader


def detect_license_plate(img_path: str):
    """
    img_path: 이미지 파일 경로
    """

    img = cv2.imread(img_path)  # 이미지 파일 불러와 인코딩
    if img is None:
        return 'Failed to load image file.'

    # 이미지 전처리
    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 그레이스케일로 변환
    # Adaptive Thresholding
    binary = cv2.adaptiveThreshold(grayscale, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # 이미지 출력
    # show_images(['grayscale image', 'binary image'], [grayscale, binary])

    license_plates = []  # 차량번호들을 저장할 리스트
    reader = Reader(lang_list=['ko', 'en'], gpu=False)  # EasyOCR 객체 생성

    # 컨투어 찾기
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        # 컨투어의 근사치 구하기 -> 덜 굴곡진 단순한(직선에 가까운) 형태로 만들기
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 근사치의 꼭지점이 4개일 때만 사각형으로 판단
        if len(approx) == 4:  # approx 리스트에 포함된 점의 수가 4개인지 확인
            # contour에서 사각형 정보 얻기
            x, y, w, h = cv2.boundingRect(contour)

            # 너비와 높이 비율을 통해 번호판인지 판단(번호판의 가로는 세로보다 4.5배 길다)
            ratio = w / h
            if 3 < ratio < 5:
                if w * h > 1000:  # 넓이와 높이가 아주작은 사각형 제외
                    # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 이미지 위에 사각형 표시

                    # EasyOCR로 이미지에서 자동차 번호가 인식되는 경우만 처리
                    cropped_image = img[y:y + h, x:x + w]  # 사각형 좌표에 해당하는 이미지 crop
                    readtext_results = reader.readtext(cropped_image, detail=0)  # 문자 인식
                    if readtext_results:  # 빈 리스트가 아닌 경우만 처리
                        # show_images('cropped image', cropped_image)
                        license_numbers = readtext_results[0][-4:]
                        if license_numbers.isdecimal():
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 이미지 위에 사각형 표시
                            license_plates.append(license_numbers)
                            print(license_numbers)
                            # print('contour type', type(contour))
                            # print('contour',contour.shape)
    # 최종 이미지 저장
    cv2.imwrite("images/result_image.jpg", img)

    # show_images("detect_license_plate", img)  # 감지된 사각형 영역이 표시된 이미지 출력
    return license_plates if license_plates else "Could not find license plate"