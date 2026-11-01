from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _validate_photo_url(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if not value.startswith(("http://", "https://")) or len(value) > 500:
        raise ValueError("photoUrl debe ser una URL http(s) de máximo 500 caracteres")
    return value


class RestaurantBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    city: str = Field(min_length=1, max_length=50)
    price: int = Field(ge=1, le=3)
    photoUrl: str | None = None

    @field_validator("photoUrl")
    @classmethod
    def check_photo_url(cls, value):
        return _validate_photo_url(value)


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    city: str | None = Field(default=None, min_length=1, max_length=50)
    price: int | None = Field(default=None, ge=1, le=3)
    photoUrl: str | None = None

    @field_validator("photoUrl")
    @classmethod
    def check_photo_url(cls, value):
        return _validate_photo_url(value)

    @model_validator(mode="after")
    def no_null_required_fields(self):
        for field in ("name", "category", "city", "price"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} no puede ser null")
        return self


class RestaurantResponse(RestaurantBase):
    id: str
    avgRating: float = 0
    numRatings: int = 0