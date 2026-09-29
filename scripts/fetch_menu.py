import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BUILDING_ID = "6b71bbc4-ead9-eb11-a2c4-daeb5c6bb933"
DISTRICT_ID = "c48c6d9c-9ad9-eb11-a2c4-ae34736f1064"
TZ = ZoneInfo("America/New_York")
API = "https://api.linqconnect.com/api/FamilyMenu"

# Keep the useful choices; omit milk, fruit, juice, condiments, cereal, and sides.
BREAKFAST_MEALS = {
    "Savory Breakfast Entree of the Day",
    "Sweet Breakfast Entree of the Day",
    "Yogurt Parfait of the Day",
}
LUNCH_PREFIXES = ("Hot Entree", "Cold Entree", "Grab", "Bagel", "Sunbutter")
SKIP_MEAL_WORDS = ("side", "milk", "condiment", "fruit", "vegetable")
SKIP_CATEGORY_WORDS = ("milk", "condiment", "fruit", "juice", "vegetable")

def monday_of_week(d):
    return d - timedelta(days=d.weekday())

def fmt_api(d):
    return d.strftime("%m-%d-%Y")

def iso_from_linq(s):
    return datetime.strptime(s, "%m/%d/%Y").date().isoformat()

def recipes_from_meal(meal):
    out = []
    for cat in meal.get("RecipeCategories", []):
        cname = cat.get("CategoryName", "").lower()
        if any(w in cname for w in SKIP_CATEGORY_WORDS):
            continue
        for recipe in cat.get("Recipes", []):
            name = (recipe.get("RecipeName") or "").strip()
            if name and name not in out:
                out.append(name)
    return out

def include_breakfast(meal_name):
    return meal_name in BREAKFAST_MEALS

def include_lunch(meal_name):
    low = meal_name.lower()
    if any(w in low for w in SKIP_MEAL_WORDS):
        return False
    return meal_name.startswith(LUNCH_PREFIXES)

def note_for(meal_name):
    low = meal_name.lower()
    if "vegetarian" in low:
        return "Vegetarian"
    if "grab" in low or "bagel" in low or "sunbutter" in low:
        return "Grab & Go"
    return ""

def fetch_json(start, end):
    params = urllib.parse.urlencode({
        "buildingId": BUILDING_ID,
        "districtId": DISTRICT_ID,
        "startDate": fmt_api(start),
        "endDate": fmt_api(end),
    })
    req = urllib.request.Request(API + "?" + params, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://linqconnect.com/",
        "Origin": "https://linqconnect.com",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)

def main():
    today = datetime.now(TZ).date()
    start = monday_of_week(today)
    end = start + timedelta(days=4)
    raw = fetch_json(start, end)

    days = {}
    for i in range(5):
        d = start + timedelta(days=i)
        days[d.isoformat()] = {
            "iso": d.isoformat(),
            "weekday": d.strftime("%A").upper(),
            "displayDate": d.strftime("%b %-d"),
            "breakfast": [],
            "lunch": [],
        }

    sessions = raw.get("FamilyMenuSessions", [])
    for session in sessions:
        serving = (session.get("ServingSession") or "").lower()
        if serving not in ("breakfast", "lunch"):
            continue
        for plan in session.get("MenuPlans", []):
            for day in plan.get("Days", []):
                try:
                    key = iso_from_linq(day.get("Date", ""))
                except ValueError:
                    continue
                if key not in days:
                    continue
                seen = set()
                for meal in day.get("MenuMeals", []):
                    meal_name = meal.get("MenuMealName", "")
                    keep = include_breakfast(meal_name) if serving == "breakfast" else include_lunch(meal_name)
                    if not keep:
                        continue
                    for name in recipes_from_meal(meal):
                        marker = (name, note_for(meal_name))
                        if marker in seen:
                            continue
                        seen.add(marker)
                        days[key][serving].append({"name": name, "note": marker[1]})

    payload = {
        "weekLabel": f"{start.strftime('%b %-d')} – {end.strftime('%b %-d, %Y')}",
        "updatedAt": datetime.now(TZ).isoformat(),
        "days": list(days.values()),
    }
    with open("menu.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"LINQ fetch failed: {e}", file=sys.stderr)
        # Fail the Action so GitHub clearly reports the problem.
        sys.exit(1)
