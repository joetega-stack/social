from fastapi import FastAPI,Response
from routes import userRoutes,authRoutes,postRoutes
from fastapi.middleware.cors import CORSMiddleware
from lib.database import Base,engine


Base.metadata.create_all(bind=engine)
# Base.metadata.drop_all(bind=engine)

server = FastAPI()


server.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://stack-social.vercel.app","https://stack-social-ten.vercel.app",],
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
