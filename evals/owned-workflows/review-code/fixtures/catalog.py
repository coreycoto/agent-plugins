class Catalog:
    def __init__(self, store):
        self.store = store
        self.cache = {}

    def get(self, tenant, sku):
        if sku not in self.cache:
            self.cache[sku] = self.store.lookup(tenant, sku)
        return self.cache[sku]
