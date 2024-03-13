from db import SessionLocal
from models import Pool

if __name__ == "__main__":
    db = SessionLocal()
    db.add(Pool(**{
        "name": "pool1",
        "id": 1,
        "domains": {'domain-a.xyz': 2, 'domain-b.xyz': 1},
    }))
    db.commit()
    db.add(Pool(**{
        "name": "pool2",
        "id": 2,
        "domains": {'domain-c.xyz': 3, 'domain-d.xyz': 1, 'domain-e.xyz': 2},
    }))
    db.commit()
    db.add(Pool(**{
        "name": "pool3",
        "id": 3,
        "domains": {},
    }))
    db.commit()
    db.close()
