from copy import deepcopy

from fastapi import FastAPI, HTTPException, Request
from starlette.responses import RedirectResponse
from urllib.parse import urlencode

from config import settings
from models import Pool
from middleware import DatabaseMiddleware
from db import SessionLocal

app = FastAPI(debug=settings.DEBUG)

initial_domain_pools = {}
domain_pools = deepcopy(initial_domain_pools)


@app.middleware("http")
async def add_database_middleware(request: Request, call_next):
    response = await DatabaseMiddleware(SessionLocal())(request, call_next)
    return response


@app.on_event('startup')
async def startup_event():
    global initial_domain_pools
    global domain_pools
    initial_domain_pools = Pool.load_pools()
    domain_pools = deepcopy(initial_domain_pools)


@app.get("/")
async def health_check():
    return {"status": "ok"}


def sort_domains_by_weight(pool_id):
    domain_pool = domain_pools[pool_id]
    sorted_domains = sorted(domain_pools[pool_id].items(), key=lambda x: x[1], reverse=True)
    return domain_pool, sorted_domains


@app.get("/{path:path}")
async def redirect_to_domain(path: str, request: Request):
    query_params = dict(request.query_params)
    pool_id = query_params.pop("pool_id", None)
    if pool_id not in initial_domain_pools:
        raise HTTPException(status_code=400, detail="Invalid pool ID")

    domain_pool, sorted_domains = sort_domains_by_weight(pool_id)
    if not sorted_domains:
        domain_pools[pool_id] = deepcopy(initial_domain_pools[pool_id])
        domain_pool, sorted_domains = sort_domains_by_weight(pool_id)
        if not sorted_domains:
            raise HTTPException(status_code=400, detail="No domains available")

    # Choose the first domain
    chosen_domain = sorted_domains[0][0]

    # Update weight
    domain_pool[chosen_domain] -= 1
    if domain_pool[chosen_domain] == 0:
        del domain_pool[chosen_domain]

    full_url = f"{settings.SCHEMA}://{chosen_domain}/{path}"
    query_params = urlencode(query_params)

    if query_params:
        full_url += "?" + query_params
    if settings.DEBUG:
        return {"url": full_url}, settings.REDIRECT_STATUS_CODE
    return RedirectResponse(**{"url": full_url}, status_code=settings.REDIRECT_STATUS_CODE)


if __name__ == "__main__":
    import uvicorn
    # TODO: add redis cache
    # TODO: add api to CRUD domains and pools
    # TODO: add cache invalidation on Pools changing
    # TODO: add api to GET log info (add filtering)

    initial_domain_pools = Pool.load_pools()
    domain_pools = deepcopy(initial_domain_pools)
    uvicorn.run(app, host="0.0.0.0", port=8000)
