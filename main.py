from fastapi import FastAPI, Form, Request
from uploadFile import upload_router
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/css", StaticFiles(directory="css"))
app.mount("/assets", StaticFiles(directory="assets"))
app.mount("/js", StaticFiles(directory="js"))
app.mount("/static", StaticFiles(directory="static"))
app.mount("/images", StaticFiles(directory="images"))
app.include_router(upload_router)


@app.get("/")
async def main(request:Request):
    return templates.TemplateResponse('main_page.html', {'request':request})