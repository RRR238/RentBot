from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Shared.LLM import LLM
import re
from Shared.Geolocation import get_coordinates
import json
from sqlalchemy.inspection import inspect
from datetime import datetime

repository = Rent_offers_repository(CONN_STRING)
vdb = Vector_DB_Qdrant('rent-bot-index')
llm = LLM()

prompt = """Z nasledujúceho opisu nehnuteľnosti extrahuj cenu **čisto za energie**, ak je to možné.
Pozor – uveď **iba cenu za energie**! Ak je v texte uvedené „cena nájmu <cena> vrátane energií“, odpíš: None.

{description}

Odpovedz IBA číslom. Ak nie je možné určiť konkrétnu sumu, odpíš: None.
Tvoja odpoveď:
"""


def extract_energy_price(lt: str) -> str:
    patterns = [
        r'energie:(\d+)',                    # energie:100
        r'\+(\d+)energie',                   # +100energie
        r'\+(\d+)€energie',                  # +100€energie
        r'\+(\d+)eurenergie',                # +100eurenergie
        r'energievrátaneinternetuatv:(\d+)', # energievrátaneinternetuatv:300
        r'\+(\d+),-',                        # +100,-
        r'\+energie(\d+)',                   # +energie100
        r'cenanezahŕňaenergie(\d+)'          # cenanezahŕňaenergie250
    ]

    for pattern in patterns:
        match = re.search(pattern, lt)
        if match:
            return match.group(1)
    return "None"

sources = repository.get_all_source_urls()
count = 1
found_dups = 0
not_deleted = []
not_deleted_vdb = []
l = len(sources)
duplicates=[]
for i in sources:

    print(f"processing: {count}/{l}")
    # # # print(f"dups found: {found_dups}")
    # # # count += 1
    offer = repository.get_offer_by_id_or_url(i)
    # if offer.price_energies is not None:
    #     count += 1
    #     continue
    #
    # lt = offer.description.lower().replace(' ','')
    # #print(offer.description)
    # manually = extract_energy_price(lt).strip()
    # #print(f"manually: {manually}")
    # if manually == 'None':
    #     generated = llm.generate_answer(prompt=prompt.format(description=offer.description)).strip()
    #     print(f"generated - no customization: {generated}")
    #     #print(f"generated: {generated}")
    #     try:
    #         generated = int(re.sub(r'\D', '', generated))
    #         print(f"generated - after customization: {generated}")
    #         if generated == 'None':
    #             energies = None
    #         elif generated >= offer.price_rent:
    #             energies = None
    #         else:
    #             energies = generated
    #     except Exception as e:
    #         #print("conclusion: None")
    #         print(f"{str(e)} on: {i}")
    #         energies = None
    # else:
    #     try:
    #         print(f"manual extraction: {manually}")
    #         energies = int(manually)
    #     except Exception as e:
    #         energies = None
    #         print(f"{str(e)} on: {i}")
    #
    # if energies is not None and offer.price_rent is not None:
    #     total = offer.price_rent + energies
    # else:
    #     total = offer.price_rent

    # try:
    #     lat, lon = get_coordinates(offer.location)
    # except:
    #     lat, lon = None, None
    # repository.update_offer(i,{"price_total":total,"price_energies":energies})
    # resource = vdb.get_element(source_url=i)[0].points[0].payload
    # resource.update({"price_total":total})
    # vdb.update_metadata_by_url(source_url=i,updated_metadata=resource)
    # count+=1

    dups = repository.find_duplicates(
        price_rent=offer.price_rent,
        price_energies=offer.price_energies,
        size=offer.size,
        rooms=offer.rooms,
        ownership=offer.ownership,
        lat=offer.latitude,
        lon=offer.longtitude,
        url=i
    )

    print(dups)
    if len(dups) > 0:
        if len(dups) > 0:
            duplicates.append({
                "original": i,
                "lat":offer.latitude,
                "lon":offer.longtitude,
                "duplicates": [{"source":dup.source_url, "lat":dup.latitude,"lon":dup.longtitude}for dup in dups]
            })
#
#
        try:
            repository.delete_by_source_urls([i])
        except:
            not_deleted.append(i)
            continue
        try:
            vdb.delete_element(source_url=i)
        except:
            not_deleted_vdb.append(i)

        found_dups += 1

    count += 1

with open("duplicates.json", "w", encoding="utf-8") as f:
    json.dump(duplicates, f, ensure_ascii=False, indent=2)