from models import * 

# --- In-Memory Database ---
db_clients: List[ClientResponse] = []
client_id_counter = 1

db_account_types: List[AccountType] = [AccountType(name=n) for n in ["Checking", "Savings", "Credit Card", "Investment"]]
db_account_currencies: List[AccountCurrency] = [
    AccountCurrency(code="BRL", name="Brazilian Real"), AccountCurrency(code="USD", name="US Dollar"), AccountCurrency(code="EUR", name="Euro")
]
db_financial_accounts: Dict[int, List[FinancialAccountResponse]] = {}
account_id_counter = 1

db_categories: List[Category] = [
    Category(id=1, name="Office Supplies", type=CategoryType.EXPENSE, description="Pens, paper, etc."),
    Category(id=2, name="Sales Revenue", type=CategoryType.INCOME, description="Primary income from sales.")
]
category_id_counter = 3

db_statuses: List[Status] = [
    Status(id=1, name="Pending", description="Transaction is awaiting confirmation."),
    Status(id=2, name="Completed", description="Transaction is finalized."),
    Status(id=3, name="Cancelled", description="Transaction was voided.")
]
status_id_counter = 4

db_partners: List[Partner] = []
partner_id_counter = 1
db_cost_centers: List[CostCenter] = []
cost_center_id_counter = 1
db_invoices: List[Invoice] = []
invoice_id_counter = 1

db_transactions: Dict[int, List[TransactionResponse]] = {}
transaction_id_counter = 1