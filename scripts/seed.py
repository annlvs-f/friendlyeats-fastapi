"""Carga 10 restaurantes de prueba. Uso: python -m scripts.seed"""
from app.core.firebase import get_db
from app.domain.models import COLLECTION_NAME

RESTAURANTS = [
    {"id": "la-abuela", "name": "La Abuela", "category": "Mexicana", "city": "Puebla", "price": 2,
     "photoUrl": "https://images.unsplash.com/photo-1552566626-52f8b828add9", "avgRating": 4.5, "numRatings": 20},
    {"id": "pizza-central", "name": "Pizza Central", "category": "Pizza", "city": "Puebla", "price": 1,
     "photoUrl": "https://images.unsplash.com/photo-1513104890138-7c749659a591", "avgRating": 4.0, "numRatings": 12},
    {"id": "casa-del-mole", "name": "Casa del Mole Poblano", "category": "Mexicana", "city": "Puebla", "price": 3,
     "photoUrl": None, "avgRating": 4.8, "numRatings": 54},
    {"id": "cemitas-la-poblana", "name": "Cemitas La Poblana", "category": "Cemitas", "city": "Puebla", "price": 1,
     "photoUrl": None, "avgRating": 4.3, "numRatings": 31},
    {"id": "tacos-pastor-dorado", "name": "Tacos Árabes El Pastor Dorado", "category": "Tacos", "city": "Puebla", "price": 1,
     "photoUrl": None, "avgRating": 4.6, "numRatings": 77},
    {"id": "sushi-angelopolis", "name": "Sushi Angelópolis", "category": "Japonesa", "city": "Puebla", "price": 2,
     "photoUrl": None, "avgRating": 3.9, "numRatings": 18},
    {"id": "cafe-barroco", "name": "Café Barroco", "category": "Cafetería", "city": "Puebla", "price": 2,
     "photoUrl": None, "avgRating": 4.2, "numRatings": 26},
    {"id": "trattoria-los-fuertes", "name": "Trattoria Los Fuertes", "category": "Italiana", "city": "Puebla", "price": 3,
     "photoUrl": None, "avgRating": 4.4, "numRatings": 40},
    {"id": "mariscos-el-marinero", "name": "Mariscos El Marinero", "category": "Mariscos", "city": "Atlixco", "price": 2,
     "photoUrl": None, "avgRating": 4.1, "numRatings": 15},
    {"id": "hamburguesas-la-calera", "name": "Hamburguesas La Calera", "category": "Hamburguesas", "city": "Cholula", "price": 1,
     "photoUrl": None, "avgRating": 3.7, "numRatings": 9},
]


def main() -> None:
    collection = get_db().collection(COLLECTION_NAME)
    for item in RESTAURANTS:
        data = dict(item)
        doc_id = data.pop("id")
        collection.document(doc_id).set(data)
    print(f"Datos semilla creados: {len(RESTAURANTS)} restaurantes")


if __name__ == "__main__":
    main()