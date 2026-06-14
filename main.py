from fastapi import FastAPI, UploadFile, File, HTTPException
from bs4 import BeautifulSoup
import re

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

    # Regex to structurally identify course codes (e.g., 4 capital letters, optional space, 4 digits)
    course_code_regex = re.compile(r'[A-Z]{4}\s?\d{4}')

    for row in rows[1:]:
        cols = row.find_all("td")

        if len(cols) < 5:
            continue

        # Extract raw text from columns structurally based on index
        course_code = cols[0].get_text(strip=True)
        title = cols[1].get_text(strip=True)
        credits_raw = cols[2].get_text(strip=True)
        prerequisites_raw = cols[3].get_text(strip=True)
        cross_listed_raw = cols[4].get_text(strip=True)

        # 1. Sanitize 'credits' into a proper integer data type
        try:
            credits = int(credits_raw)
        except ValueError:
            credits = 0

        # 2. Extract prerequisites into a precise JSON array via Regex matching
        # .findall() safely returns an empty list [] if no course codes match (e.g., "None")
        prerequisites = course_code_regex.findall(prerequisites_raw.upper())
        
        # 3. Extract cross-listed courses into a precise JSON array via Regex matching
        cross_listed = course_code_regex.findall(cross_listed_raw.upper())

        # Generate a standardized key for storage and retrieval mapping
        key = course_code.upper().replace(" ", "")

        catalog[key] = {
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
