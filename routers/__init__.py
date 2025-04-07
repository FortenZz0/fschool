import importlib
import os


_is_router = lambda x: "_router.py" in x

routers = []


router_dir = os.scandir("./routers")


print("IMPORT ROUTERS:")

for f in router_dir:
    if _is_router(f.name):
        router_name = f.name.split(".")[0]
        
        router_lib = importlib.import_module(f"routers.{router_name}")
        router = router_lib.router
        router_active =  router_lib.ACTIVE
        
        if router_active:
            routers.append(router)
            print(f"  \"{router_name}\" imported")
        else:
            print(f"  \"{router_name}\" NOT imported (disabled)")

print("\n  All routers are imported\n")


router_dir.close()