from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status

from app.domain.models import DEFAULT_LIMIT, MAX_LIMIT
from app.domain.schemas import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.services.restaurant_service import RestaurantService, get_service

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("", response_model=list[RestaurantResponse])
def list_restaurants(
    category: str | None = None,
    city: str | None = None,
    price: int | None = Query(default=None, ge=1, le=3),
    order_by: Literal["name", "avgRating"] = "name",
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    start_after: str | None = None,
    service: RestaurantService = Depends(get_service),
):
    return service.list(category=category, city=city, price=price,
                        order_by=order_by, limit=limit, start_after=start_after)


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: str, service: RestaurantService = Depends(get_service)):
    return service.get(restaurant_id)


@router.post("", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant(payload: RestaurantCreate, service: RestaurantService = Depends(get_service)):
    return service.create(payload)


@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(restaurant_id: str, payload: RestaurantUpdate,
                      service: RestaurantService = Depends(get_service)):
    return service.update(restaurant_id, payload)


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(restaurant_id: str, service: RestaurantService = Depends(get_service)):
    service.delete(restaurant_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)