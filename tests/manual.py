import os

from dotenv import load_dotenv

from py_altium365.altium_api import AltiumApi
from py_altium365.base.enums import PrtGlobalService
from py_altium365.connection.json_con_search_async import FacedType

load_dotenv()

api = AltiumApi()
user_name = os.environ.get("ALTIUM_USER")
password = os.environ.get("ALTIUM_PASS")
totp_secret = os.environ.get("ALTIUM_TOTP_SECRET")
if user_name is None or password is None:
    raise ValueError("Please set the ALTIUM_USER and ALTIUM_PASS environment variables")

print(api.login(user_name, password))
print(api.get_service_url(PrtGlobalService.WORKSPACE))

ws = api.get_user_workspaces()
cws = api.login_workspace(ws[0], user_name, password, oauth_totp_secret=totp_secret)
if cws is None:
    raise ValueError("Failed to login to workspace")

cws.get_all_folders()

so = cws.create_search_object()
# so.add_search_parameter("Voltage", "16v")
print(so.get_current_count())
# so.add_search_parameter("Voltage", "630v")
print(so.get_current_count())
# results: List[SearchDataBase] = so.get_results(max_amount=10000)

print(so.get_all_search_names_and_type_range())

so.add_search_parameter_range("Voltage", 1, 32, dtype=FacedType.VOLTAGE)
so.add_search_parameter("LifeCycle", "Waiting for review")

print(so.get_current_count())
results = so.get_results(max_amount=100)

children = results[0].get_item().get_latest_item_revision(cws).get_child_item_revisions(cws)
for child in children:
    print(child.get_item().get_name())

print(results[0].get_item().get_name())


# amount = {}
# for result in results:
#     for param_name in result.parameters:
#         if param_name not in amount:
#             amount[param_name] = 0
#         amount[param_name] += 1
#
# for param_name, amount in amount.items():
#     print(param_name + ": " + str(amount))
