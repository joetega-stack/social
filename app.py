from fastapi import FastAPI,Response
from routes import userRoutes,authRoutes,postRoutes,messageRoutes
from fastapi.middleware.cors import CORSMiddleware
from lib.database import Base,engine


Base.metadata.create_all(bind=engine)
# Base.metadata.drop_all(bind=engine)
# print(Base.metadata.tables.keys())
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://stack-social.vercel.app","https://stack-social-ten.vercel.app","https://social-topaz-five-10.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def check_health(response: Response):
    response.status_code = 200
    return {"message":"Server is healthy"}

app.include_router(authRoutes.router)
app.include_router(userRoutes.router)
app.include_router(postRoutes.router)
app.include_router(messageRoutes.router)
