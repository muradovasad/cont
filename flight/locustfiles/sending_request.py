from random import randint
from locust import HttpUser, task

class WebUser(HttpUser):
    # wait_time = randint(1, 3)

    @task
    def search_ow(self):
        body = self._request_maker_ow()
        self.client.post('/search/', json=body)

    def _request_maker_ow(self):
        month = randint(10, 12)
        day = randint(10, 30)
        data = {  
            "directions": [
                {
                    "departure_airport": "MOW",
                    "arrival_airport": "TAS",
                    "departure_date": f"2023-{month}-{day}"
                }
            ],
            "adt": 1,
            "chd": 0,
            "inf": 0,
            "ins": 0,
            "providers": [
                {
                    "uuid": "25b107aa-8570-4fea-94fb-0ad75a067733",
                    "name": "mixvel",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                },
                {
                    "uuid": "25b107aa-8570-4fea-94fb-0ad75a067733",
                    "name": "mixvel",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                },
                {
                    "uuid": "25b107aa-8570-4fea-94fb-0ad75a067733",
                    "name": "mixvel",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                },
                {
                    "uuid": "25b107aa-8570-4fea-94fb-0ad75a067733",
                    "name": "mixvel",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                },
                {
                    "uuid": "25b107aa-8570-4fea-94fb-0ad75a067733",
                    "name": "mixvel",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                },
                {
                    "uuid": "25b107aa-8570-4fea-94fb-0ad75a067733",
                    "name": "mixvel",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                },
                {
                    "uuid": "3292hsaa-8570-4fea-7sa7-0ud75a067786",
                    "name": "centrum",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                },
                {
                    "uuid": "3292hsaa-8570-4fea-7da7-0ad75a067786",
                    "name": "amadeus",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                },
                {
                    "uuid": "3292hsaa-857h-4fea-7sa7-0ad75a067786",
                    "name": "aerticket",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                },
                {
                    "uuid": "329mhsaa-8570-4fea-7sa7-0ad75a067786",
                    "name": "centrum",
                    "auth_data": {
                        "login": "eba9992c-819b-492b-b4bd-a267e5578e40@01138",
                        "password": "gAkl1TQ3TuCd8to3",
                        "structure_unit_id": "01138_DTFVR"
                    }
                }
            ],
            "class": "economy",
            "flexible": 0,
            "direct": True
        }

        return data