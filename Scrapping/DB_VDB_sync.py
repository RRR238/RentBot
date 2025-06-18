from Rent_offers_repository import Rent_offers_repository
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Shared.Vector_database.Vector_DB_interface import Vector_DB_interface
import os
from dotenv import load_dotenv

load_dotenv()
conn_string = os.getenv('connection_string')

def sync(db:Rent_offers_repository,
         vdb:Vector_DB_interface):

    db_urls = set(db.get_all_source_urls())
    vdb_urls = set([i['source_url'] for i in vdb.get_all_metadata()])
    db_not_vdb = db_urls - vdb_urls
    vdb_not_db = vdb_urls - db_urls
    if len(db_not_vdb)>0:
        for j in db_not_vdb:
            db.delete_by_source_urls([j])
    if len(vdb_not_db)>0:
        for k in vdb_not_db:
            vdb.delete_element(source_url=k)

    print(f'Deleted {len(db_not_vdb)} items from DB...')
    print(f'Deleted {len(vdb_not_db)} items from VDB...')

if __name__ == "__main__":
    sync(Rent_offers_repository(conn_string),
            Vector_DB_Qdrant('rent-bot-index'))
