from qdrant_client.models import PayloadSchemaType
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant

vdb = Vector_DB_Qdrant('rent-bot-index')
vdb.create_payload_indexes([
    ('price_total', PayloadSchemaType.FLOAT),
    ('size', PayloadSchemaType.FLOAT),
    ('latitude', PayloadSchemaType.FLOAT),
    ('longtitude', PayloadSchemaType.FLOAT),
    ('rooms', PayloadSchemaType.INTEGER),
    ('property_type', PayloadSchemaType.KEYWORD),
    ('property_status', PayloadSchemaType.KEYWORD),
])
print('Done.')
