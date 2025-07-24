from Scrapping.Rent_offers_repository import Rent_offers_repository
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Shared.Vector_database.Vector_DB_interface import Vector_DB_interface
import os
from dotenv import load_dotenv
from collections import Counter


load_dotenv()
conn_string = os.getenv('connection_string')

def delete_duplicates_db(db:Rent_offers_repository):
    all_urls = db.get_all_source_urls()
    all_items = {item.id:item.source_url for item in db.get_all_items()}
    url_counts = Counter(all_urls)
    deleted=0
    for id, url in all_items.items():
        if url_counts[url] > 1:
            db.delete_by_ids([id])
            url_counts[url]-=1
            deleted+=1


    print(f"Deleted {deleted} duplicate URLs.")


def delete_duplicates_vdb(vdb:Vector_DB_interface):
    all_items = vdb.get_all_metadata()
    all_urls = [i['source_url'] for i in all_items]
    ids_urls = {item['id']:item["source_url"] for item in all_items}
    url_counts = Counter(all_urls)
    deleted=0
    for id, url in ids_urls.items():
        if url_counts[url] > 1:
            vdb.delete_element(postgres_id=id)
            url_counts[url]-=1
            deleted+=1


    print(f"Deleted {deleted} duplicate URLs.")

def sync(db:Rent_offers_repository,
         vdb:Vector_DB_interface):

    db_ids = set([item.id for item in db.get_all_items()])
    vdb_ids = set([i['id'] for i in vdb.get_all_metadata()])
    db_not_vdb = db_ids - vdb_ids
    vdb_not_db = vdb_ids - db_ids
    if len(db_not_vdb)>0:
        for j in db_not_vdb:
            db.delete_by_ids([j])
    if len(vdb_not_db)>0:
        for k in vdb_not_db:
            vdb.delete_element(postgres_id=k)

    print(f'Deleted {len(db_not_vdb)} items from DB...')
    print(f'Deleted {len(vdb_not_db)} items from VDB...')

if __name__ == "__main__":
    print('Deleting from DB...')
    delete_duplicates_db(Rent_offers_repository(conn_string))
    print('Deleting from VDB...')
    delete_duplicates_vdb(Vector_DB_Qdrant('rent-bot-index'))
    print('Syncing DB & VDB')
    sync(Rent_offers_repository(conn_string),
            Vector_DB_Qdrant('rent-bot-index'))

