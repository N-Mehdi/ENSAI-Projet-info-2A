from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])

@router.post("/s'inscrire")
def creer_compte()