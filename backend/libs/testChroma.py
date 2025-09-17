import chromadb

# 连接到 ChromaDB Cloud
client = chromadb.CloudClient(
    api_key="ck-CDMMhWMnpbzGwU6vZUPkucdL8sUL7dFq5XK7eX3hY8BR",
    tenant="fd1cb388-55f9-432c-9fc3-b12811c67ee0",
    database="test-global-cs"
)

# collection 名
collection_name = "test-global-cs"

# 获取或创建一个 collection
collection = client.get_or_create_collection(name=collection_name)

print(f"Connected to collection: {collection_name}")

# 查询
query_text = "项目"
result = collection.query(
    query_texts=[query_text],
    n_results=1
)
print(f"Query: {query_text}")
print(result)