from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.restaurants import router as restaurants_router
from app.core.config import settings
from app.domain.models import DEFAULT_LIMIT, PRICE_LABELS
from app.services.restaurant_service import get_service

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title=settings.APP_NAME)
app.include_router(restaurants_router, prefix="/api/v1")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")
templates.env.globals["price_labels"] = PRICE_LABELS
templates.env.globals["app_name"] = settings.APP_NAME

FLASH_MESSAGES = {
    "created": "Restaurante creado correctamente.",
    "updated": "Restaurante actualizado correctamente.",
    "deleted": "Restaurante eliminado correctamente.",
}

BASE_CATEGORIES = ["Mexicana", "Tacos", "Pizza", "Italiana", "Japonesa", "Mariscos",
                   "Hamburguesas", "Cafetería", "Cemitas", "Vegetariana", "Postres"]
BASE_CITIES = ["Puebla", "Cholula", "Atlixco"]


def _form_options() -> dict:
    """Sugerencias para el formulario: las ya registradas más una lista base."""
    catalog = get_service().list(limit=100)
    cities = sorted({r["city"] for r in catalog if r.get("city")} | set(BASE_CITIES))
    categories = sorted({r["category"] for r in catalog if r.get("category")} | set(BASE_CATEGORIES))
    return {"cities": cities, "categories": categories}


@app.get("/health")
def health():
    return {"status": "ok"}


def _render_error(request: Request, status_code: int, message: str):
    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": status_code, "message": message},
        status_code=status_code,
    )


@app.get("/", include_in_schema=False)
def home(
    request: Request,
    city: str = "",
    category: str = "",
    price: str = "",
    order_by: str = "name",
    start_after: str = "",
    msg: str = "",
):
    service = get_service()
    price_value = int(price) if price in ("1", "2", "3") else None
    order = order_by if order_by in ("name", "avgRating") else "name"

    restaurants = service.list(
        category=category.strip() or None,
        city=city.strip() or None,
        price=price_value,
        order_by=order,
        limit=DEFAULT_LIMIT,
        start_after=start_after or None,
    )

    catalog = service.list(limit=100)
    cities = sorted({r["city"] for r in catalog if r.get("city")})
    categories = sorted({r["category"] for r in catalog if r.get("category")})

    next_url = None
    if len(restaurants) == DEFAULT_LIMIT:
        next_url = str(request.url.include_query_params(start_after=restaurants[-1]["id"], msg=""))

    return templates.TemplateResponse(
        request,
        "restaurants.html",
        {
            "restaurants": restaurants,
            "cities": cities,
            "categories": categories,
            "filters": {"city": city, "category": category, "price": price_value, "order_by": order},
            "next_url": next_url,
            "has_prev": bool(start_after),
            "flash": FLASH_MESSAGES.get(msg),
        },
    )


# /restaurants/new va ANTES que /restaurants/{id} para que no choquen
@app.get("/restaurants/new", include_in_schema=False)
def new_restaurant_form(request: Request):
    return templates.TemplateResponse(
        request, "restaurant_form.html", {"restaurant": None, **_form_options()}
    )


@app.get("/restaurants/{restaurant_id}", include_in_schema=False)
def restaurant_detail(request: Request, restaurant_id: str, msg: str = ""):
    try:
        restaurant = get_service().get(restaurant_id)
    except HTTPException as exc:
        return _render_error(request, exc.status_code, str(exc.detail))
    return templates.TemplateResponse(
        request,
        "restaurant_detail.html",
        {"restaurant": restaurant, "flash": FLASH_MESSAGES.get(msg)},
    )


@app.get("/restaurants/{restaurant_id}/edit", include_in_schema=False)
def edit_restaurant_form(request: Request, restaurant_id: str):
    try:
        restaurant = get_service().get(restaurant_id)
    except HTTPException as exc:
        return _render_error(request, exc.status_code, str(exc.detail))
    return templates.TemplateResponse(
        request, "restaurant_form.html", {"restaurant": restaurant, **_form_options()}
    )