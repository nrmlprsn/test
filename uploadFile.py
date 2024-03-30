from fastapi import APIRouter, Request
from fastapi import UploadFile, File, HTTPException
from pathlib import Path
import shutil
from fastapi.templating import Jinja2Templates
from license_plate import detect_license_plate
import json

upload_router = APIRouter()
templates = Jinja2Templates(directory="templates")

@upload_router.post("/upload")
async def upload_image(request: Request, file: UploadFile = File(...)):
    # 이미지 파일 확장자 확인
    file_extension = Path(file.filename).suffix # 파일 확장자를 문자열로 추출
    if file_extension not in ['.jpg', '.jpeg', '.png']:
        raise HTTPException(status_code=400, detail="Invalid image file type")

    # 이미지 파일 저장
    image_file_path = f'images/{file.filename}'
    with open(image_file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 이미지에서 자동차 번호 추출
    license_numbers = detect_license_plate(image_file_path)

    registered = []
    with open('static/car_data.json','r') as file:
        car_data = json.load(file)
    for number in license_numbers:
        for data in car_data:
            if data['차량번호'][-4:]==number:
                registered.append(number)

    not_registered = list(set(license_numbers)-set(registered))

    if not_registered:
        reply = "등록되지 않은 차량번호는 "+", ".join(not_registered)+" 입니다."
    else: reply = "모두 등록된 차량입니다."

    # 클라이언트에게 전달할 응답 생성
    data = {"title": "License plate recognition results", "license_numbers": license_numbers, "reply": reply}
    return templates.TemplateResponse("result.html", {"request": request, **data})