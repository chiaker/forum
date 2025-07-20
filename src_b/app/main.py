from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src_b.api_v1.views import router
from src_b.api_v1.models import init_db
from fastapi.staticfiles import StaticFiles

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # или ["http://127.0.0.1:5500", "https://web.shuman.keenetic.pro"]
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api/v1")
app.mount("/", StaticFiles(directory="/home/root_server/forum/forum",
          html=True), name="static")
