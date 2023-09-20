async def is_login_endpoint(endpoint):
    return endpoint == "/api/Accounts/login"


async def request_template(endpoint):
    return {
        "/api/Accounts/login": "accounts_login.xml",
        "/api/Order/airshopping": "order_airshopping.xml",
        "/api/Order/create": "order_create.xml",
        "/api/Order/retrieve": "order_retrieve.xml",
        "/api/Order/change": "order_change.xml",
        "/api/Order/cancel": "order_cancel.xml",
        "/api/Order/import": "order_import.xml",
        "/api/get/dictionary/carriers": "dictionary_carriers.xml",
        "/api/Order/OrderRules": "order_rules.xml"
    }.get(endpoint, None)