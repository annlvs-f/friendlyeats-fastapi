from google.cloud.firestore_v1 import Query
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.firebase import get_db
from app.domain.models import COLLECTION_NAME


class RestaurantRepository:
    """Único lugar de la app que habla con Firestore."""

    @property
    def collection(self):
        return get_db().collection(COLLECTION_NAME)

    def create(self, data: dict) -> dict:
        ref = self.collection.document()  # ID automático
        document = {**data, "avgRating": 0, "numRatings": 0}
        ref.set(document)
        return {**document, "id": ref.id}

    def get(self, restaurant_id: str) -> dict | None:
        doc = self.collection.document(restaurant_id).get()
        if not doc.exists:
            return None
        return {**doc.to_dict(), "id": doc.id}

    def list(self, category=None, city=None, price=None,
             order_by="name", limit=20, start_after=None) -> list[dict]:
        query = self.collection
        if category:
            query = query.where(filter=FieldFilter("category", "==", category))
        if city:
            query = query.where(filter=FieldFilter("city", "==", city))
        if price:
            query = query.where(filter=FieldFilter("price", "==", price))

        direction = Query.DESCENDING if order_by == "avgRating" else Query.ASCENDING
        query = query.order_by(order_by, direction=direction)

        if start_after:
            last_doc = self.collection.document(start_after).get()
            if last_doc.exists:
                query = query.start_after(last_doc)

        query = query.limit(limit)
        return [{**doc.to_dict(), "id": doc.id} for doc in query.stream()]

    def update(self, restaurant_id: str, data: dict) -> dict | None:
        ref = self.collection.document(restaurant_id)
        if not ref.get().exists:
            return None
        ref.update(data)
        return self.get(restaurant_id)

    def delete(self, restaurant_id: str) -> bool:
        ref = self.collection.document(restaurant_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True