from fastapi import FastAPI
from app.router.schedule import schedule_router
from app.router.booking import booking_router
from app.router.login import login_router
from scalar_fastapi import get_scalar_api_reference
from dotenv import load_dotenv
 

load_dotenv()

app = FastAPI(
    title="Gym Booking API",
    description="API for booking gym classes",
    version="1.0.0"
)

app.include_router(schedule_router)
app.include_router(booking_router)
app.include_router(login_router)


@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title= app.title
    )