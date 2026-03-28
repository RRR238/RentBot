from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType
import os

client = QdrantClient(url=os.getenv('QDRANT_ENDPOINT'), api_key=os.getenv('QDRANT_API_KEY'))
collection = 'rent-bot-index'

indexes = [
    ('price_total', PayloadSchemaType.FLOAT),
    ('size', PayloadSchemaType.FLOAT),
    ('latitude', PayloadSchemaType.FLOAT),
    ('longtitude', PayloadSchemaType.FLOAT),
    ('rooms', PayloadSchemaType.INTEGER),
    ('property_type', PayloadSchemaType.KEYWORD),
    ('property_status', PayloadSchemaType.KEYWORD),
]

for field, schema in indexes:
    client.create_payload_index(collection_name=collection, field_name=field, field_schema=schema)
    print(f'Created index: {field}')
