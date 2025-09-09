from test.functions import * 
from test.database import *
from models.domain import ClientCreate, ClientResponse

def create_client(client_data: ClientCreate):
    global client_id_counter
    new_client: ClientResponse = ClientResponse(client_id=client_id_counter, **client_data.model_dump())
    db_clients.append(new_client)
    db_financial_accounts[client_id_counter] = []
    db_transactions[client_id_counter] = []
    client_id_counter += 1
    return new_client

def get_all_clients(): 
    return db_clients

def get_client_by_id(client_id: int): 
    return find_client_or_404(client_id)

def update_client(client_id: int, client_data: ClientCreate):
    return

def delete_client(client_id: int):
    return