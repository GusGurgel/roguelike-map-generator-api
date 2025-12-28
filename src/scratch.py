from vector_db import query_vector_store, StoreType

result_item = query_vector_store("A gun", "items")
result_entity = query_vector_store("A dwarf named Arthur.", "entities")
result_environment = query_vector_store("A stone floor", "environments")

print(result_item)
print("-" * 80)
print(result_entity)
print("-" * 80)
print(result_environment)
