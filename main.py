from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- Configuração do Banco de Dados (MongoDB) ---
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "lightsail_db")

client = AsyncIOMotorClient(MONGO_URL)
database = client[DATABASE_NAME]
products_collection = database.products

# --- Modelos Pydantic ---

# Classe para garantir que o ObjectId seja serializável
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Modelo base para o Produto (para entrada de dados)
class ProductBase(BaseModel):
    nome: str = Field(..., example="Smartphone X")
    descricao: str = Field(..., example="Um smartphone de última geração.")
    preco: float = Field(..., gt=0, example=1999.99)
    estoque: int = Field(..., ge=0, example=50)

# Modelo para o Produto no banco de dados (inclui o ID)
class ProductDB(ProductBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Modelo para atualização (campos opcionais)
class ProductUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[float] = None
    estoque: Optional[int] = None

# --- Configuração da Autenticação ---
# Token simples para demonstração (deve ser mais robusto em produção)
API_TOKEN = os.getenv("API_TOKEN", "token-secreto-para-demonstracao")

def get_api_token(token: str):
    if token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

# --- Inicialização do FastAPI ---
app = FastAPI(
    title="Lightsail CRUD API",
    description="API RESTful CRUD para gerenciamento de Produtos, hospedada no AWS Lightsail.",
    version="1.0.0",
)

# --- Rotas CRUD ---

# Rota de teste
@app.get("/", tags=["Status"])
async def root():
    return {"message": "API de Produtos rodando com sucesso!"}

# 1. CREATE (POST)
@app.post("/products/", response_model=ProductDB, status_code=status.HTTP_201_CREATED, tags=["Produtos"])
async def create_product(product: ProductBase, token: str = Depends(get_api_token)):
    product_dict = product.dict()
    result = await products_collection.insert_one(product_dict)
    new_product = await products_collection.find_one({"_id": result.inserted_id})
    return ProductDB(**new_product)

# 2. READ All (GET)
@app.get("/products/", response_model=List[ProductDB], tags=["Produtos"])
async def read_products():
    products = []
    for doc in await products_collection.find().to_list(length=100):
        products.append(ProductDB(**doc))
    return products

# 2. READ One (GET)
@app.get("/products/{id}", response_model=ProductDB, tags=["Produtos"])
async def read_product(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    product = await products_collection.find_one({"_id": ObjectId(id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return ProductDB(**product)

# 3. UPDATE (PUT)
@app.put("/products/{id}", response_model=ProductDB, tags=["Produtos"])
async def update_product(id: str, product: ProductUpdate, token: str = Depends(get_api_token)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    update_data = {k: v for k, v in product.dict(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    result = await products_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    updated_product = await products_collection.find_one({"_id": ObjectId(id)})
    return ProductDB(**updated_product)

# 4. DELETE (DELETE)
@app.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Produtos"])
async def delete_product(id: str, token: str = Depends(get_api_token)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await products_collection.delete_one({"_id": ObjectId(id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return {"message": "Produto excluído com sucesso"}
