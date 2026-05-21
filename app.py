from fastapi import FastAPI,Response
from routes import userRoutes,authRoutes,postRoutes
from fastapi.middleware.cors import CORSMiddleware
from supabase_client import supabase



# Base.metadata.drop_all(bind=engine)

server = FastAPI()


server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@server.get("/health")
def check_health(response: Response):
    response.status_code = 200
    return {"message":"Server is healthy"}

server.include_router(authRoutes.router)
server.include_router(userRoutes.router)
server.include_router(postRoutes.router)
