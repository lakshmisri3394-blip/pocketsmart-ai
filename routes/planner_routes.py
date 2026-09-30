import json, os, uuid
from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from ..auth import require_user
from ..database import get_db
from ..services.recommender import gemini_recommend

router=APIRouter()

def save_result(user, category, data, result):
    with get_db() as db:
        db.execute(
            "INSERT INTO recommendations(user_id,category,budget,input_json,result_json) VALUES(?,?,?,?,?)",
            (user["id"],category,float(data["budget"]),json.dumps(data),json.dumps(result))
        )

@router.post("/generate-home")
def generate_home(request: Request, budget: float=Form(...), room_type: str=Form(...),
                  style: str=Form("Modern"), items: str=Form(""), notes: str=Form("")):
    user=require_user(request)
    data={"budget":budget,"room_type":room_type,"style":style,"items":items,"notes":notes}
    result=gemini_recommend("home",data)
    save_result(user,"Home",data,result)
    return JSONResponse(result)

@router.post("/generate-party")
def generate_party(request: Request, budget: float=Form(...), guests: int=Form(...),
                   event_type: str=Form(...), venue: str=Form(""), preferences: str=Form("")):
    user=require_user(request)
    data={"budget":budget,"guests":guests,"event_type":event_type,"venue":venue,"preferences":preferences}
    result=gemini_recommend("party",data)
    save_result(user,"Party",data,result)
    return JSONResponse(result)

@router.post("/generate-jewelry")
async def generate_jewelry(request: Request, budget: float=Form(...), occasion: str=Form(...),
                           style: str=Form("Elegant"), outfit_description: str=Form(""),
                           outfit_image: UploadFile|None=File(None)):
    user=require_user(request)
    image_bytes=None
    if outfit_image and outfit_image.filename:
        image_bytes=await outfit_image.read()
        os.makedirs("uploads",exist_ok=True)
        safe_name=f"{uuid.uuid4().hex}_{outfit_image.filename.replace('/','_').replace('\\','_')}"
        with open(os.path.join("uploads",safe_name),"wb") as f:
            f.write(image_bytes)
    data={"budget":budget,"occasion":occasion,"style":style,"outfit_description":outfit_description}
    result=gemini_recommend("jewelry",data,image_bytes)
    save_result(user,"Jewelry",data,result)
    return JSONResponse(result)
