from typing import List
from fastapi import APIRouter
from models.domain import ClientCreate, ClientResponse
import service.clients as service

router = APIRouter()
# --- Client CRUD ---
@router.post("/", response_model=ClientResponse, status_code=201, tags=["Clients"])
def create_client(client_data: ClientCreate):
    new_client: ClientResponse = service(client_data)
    return new_client

@router.get("/", response_model=List[ClientResponse], tags=["Clients"])
def get_all_clients(): 
    db_clients: List[ClientResponse] = service.get_all_clients()
    return db_clients

@router.get("/{client_id}", response_model=ClientResponse, tags=["Clients"])
def get_client_by_id(client_id: int): return find_client_or_404(client_id)

@router.put("/{client_id}", response_model=ClientResponse, tags=["Clients"])
def update_client(client_id: int, client_data: ClientCreate):
    client = find_client_or_404(client_id)
    client_index = db_clients.index(client)
    updated_client = ClientResponse(client_id=client_id, **client_data.dict())
    db_clients[client_index] = updated_client
    return updated_client

@router.delete("/{client_id}", status_code=204, tags=["Clients"])
def delete_client(client_id: int):
    client = find_client_or_404(client_id)
    db_clients.remove(client)
    if client_id in db_financial_accounts:
        del db_financial_accounts[client_id]
    return None