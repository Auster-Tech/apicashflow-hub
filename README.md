# apicashflow-hub

## Endpoints
@app.get("/")


#### --- Client CRUD Endpoints ---

@app.post("/clients/", response_model=ClientResponse, status_code=201, tags=["Clients"])

@app.get("/clients/", response_model=List[ClientResponse], tags=["Clients"])

@app.get("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
    
@app.put("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])

@app.delete("/clients/{client_id}", status_code=204, tags=["Clients"])


#### --- Client User CRUD Endpoints ---

@app.get("/clients/{client_id}/users/", response_model=List[CompanyUser], tags=["Client Users"])
    
@app.get("/clients/{client_id}/users/{user_id}", response_model=List[CompanyUser], tags=["Client Users"])

@app.post("/clients/{client_id}/users/", response_model=CompanyUser, status_code=201, tags=["Client Users"])

@app.put("/clients/{client_id}/users/{user_id}", response_model=CompanyUser, tags=["Client Users"])

@app.delete("/clients/{client_id}/users/{user_id}", status_code=204, tags=["Client Users"])


#### --- Account Type CRUD Endpoints ---
@app.get("/account-types/", response_model=List[AccountType], tags=["Account Configuration"])

@app.post("/account-types/", response_model=AccountType, status_code=201, tags=["Account Configuration"])

@app.put("/account-types/{account_id}", response_model=AccountType, tags=["Client Users"])

@app.delete("/account-types/{account_id}", status_code=204, tags=["Client Users"])

#### --- Account Currency CRUD Endpoints ---
@app.get("/account-currencies/", response_model=List[AccountCurrency], tags=["Account Configuration"])

@app.post("/account-currencies/", response_model=AccountCurrency, status_code=201, tags=["Account Configuration"])

@app.put("/account-currencies/{account_id}", response_model=AccountCurrency, tags=["Client Users"])

@app.delete("/account-currencies/{account_id}", status_code=204, tags=["Client Users"])