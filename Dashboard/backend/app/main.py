from fastapi import FastAPI
from app.routes import classes, payments
from app.database.session import engine, Base

# Create tables in Supabase automatically on boot
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Axiom AI API")

app.include_router(classes.router)
app.include_router(payments.router)

@app.get("/")
def root():
    return {"status": "Axiom AI Backend Running"}