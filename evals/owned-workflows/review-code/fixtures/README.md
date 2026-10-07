# Catalog contract

Catalog.get(tenant, sku) obtains that tenant's product from store.lookup(tenant, sku). Two tenants may have the same SKU with different products. Cache reuse must preserve tenant isolation. This file is the candidate under review.
