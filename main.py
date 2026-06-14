from fastapi import FastAPI, UploadFile, File, HTTPException
from bs4 import BeautifulSoup

app = FastAPI()
catalog = {}

@app.post("/api/v1/admin/catalog/import")
async def import_catalog(file: UploadFile = File(...)):
    content = await file.read()
    soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table")

    if table is None:
        raise HTTPException(status_code=400, detail="No table found")

    rows = table.find_all("tr")
    catalog.clear()

    for row in rows[1:]:
        cols = row.find_all("td")

        if len(cols) < 5:
            continue

        course_code = cols[0].get_text(strip=True)
        title = cols[1].get_text(strip=True)
        credits = cols[2].get_text(strip=True)
        prerequisites = cols[3].get_text(strip=True)
        cross_listed = cols[4].get_text(strip=True)

        catalog[course_code.upper().replace(" ", "")] = {
            "course_code": course_code,
            "title": title,
            "credits": credits,
            "prerequisites": prerequisites,
            "cross_listed": cross_listed
        }

    return {"message": "Catalog imported", "courses_loaded": len(catalog)}

@app.get("/api/v1/catalog/courses/{course_code}")
def get_course(course_code: str):
    key = course_code.upper().replace(" ", "")

    if key not in catalog:
        raise HTTPException(status_code=404, detail="Course not found")

    return catalog[key]
    