import random
import uuid
from datetime import datetime
from typing import List

from dateutil.relativedelta import relativedelta

from src.app.core.utils.common import generate_str

USER_CREATED_AT = datetime.utcnow() - relativedelta(months=6)
USER_UPDATED_AT = USER_CREATED_AT
USERS: List = [
    {
        "id": 1,
        "uuid": uuid.uuid4().__str__(),
        "created_at": USER_CREATED_AT,
        "updated_at": USER_UPDATED_AT,
        "meta": {
            "first_name": "first_name_1",
            "last_name": "last_name_1",
        },
        "birthday": datetime.utcnow() - relativedelta(months=random.randint(2, 12)),
        "is_active": True,
        "first_name": "first_name_1",
        "last_name": "last_name_1",
        "email": "1" + generate_str(5) + "@gmail.com",
    },
    {
        "id": 2,
        "uuid": uuid.uuid4().__str__(),
        "created_at": USER_CREATED_AT,
        "updated_at": USER_UPDATED_AT,
        "meta": {
            "first_name": "first_name_2",
            "last_name": "last_name_2",
        },
        "birthday": datetime.utcnow() - relativedelta(months=random.randint(2, 12)),
        "is_active": True,
        "first_name": "first_name_2",
        "last_name": "last_name_2",
        "email": "2_" + generate_str(5) + "@gmail.com",
    },
    {
        "id": 3,
        "uuid": uuid.uuid4().__str__(),
        "created_at": USER_CREATED_AT,
        "updated_at": USER_UPDATED_AT,
        "meta": {
            "first_name": "first_name_3",
            "last_name": "last_name_3",
        },
        "birthday": datetime.utcnow() - relativedelta(months=random.randint(2, 12)),
        "is_active": True,
        "first_name": "first_name_3",
        "last_name": "last_name_3",
        "email": "3_" + generate_str(5) + "@gmail.com",
    },
    {
        "id": 4,
        "uuid": uuid.uuid4().__str__(),
        "created_at": USER_CREATED_AT,
        "updated_at": USER_UPDATED_AT,
        "meta": {
            "first_name": "first_name_4",
            "last_name": "last_name_4",
        },
        "birthday": datetime.utcnow() - relativedelta(months=random.randint(2, 12)),
        "is_active": True,
        "first_name": "first_name_4",
        "last_name": "last_name_4",
        "email": "4_" + generate_str(5) + "@gmail.com",
    },
]
