from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from src_b.api_v1.views import router
from src_b.api_v1.models import init_db
from fastapi.staticfiles import StaticFiles

init_db()


class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response: Response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0"
        return response


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")



app.mount("/", NoCacheStaticFiles(directory="/home/root_server/forum/forum",
          html=True), name="static")
app.mount("/css", NoCacheStaticFiles(directory="/home/root_server/forum/forum/css"), name="css")
