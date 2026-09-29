# DAKboard School Menu

A compact Monday–Friday breakfast/lunch display for DAKboard using the public LINQ Connect FamilyMenu data.

## What it shows
- Monday through Friday
- Breakfast: savory entrée, sweet entrée, and parfait
- Lunch: main hot/cold entrées, vegetarian entrée, and grab-and-go choices when present
- Omits repetitive milk, fruit, juice, cereal, condiments, and sides
- Highlights the current day in America/New_York
- Refreshes the browser display every 30 minutes

## GitHub setup
1. Upload all files/folders in this project to the repository root.
2. Go to **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **GitHub Actions**.
4. Go to **Actions → Update and deploy school menu → Run workflow**.
5. If the run succeeds, the site should be:
   `https://afunahashi.github.io/dakboard_school_menu/`
6. Put that URL into a DAKboard **Website / iFrame** block.

## Automation
The workflow runs daily at 5:15 AM America/New_York and can also be run manually. It requests the current Monday–Friday range from LINQ and rewrites `menu.json`.

## LINQ note
LINQ may block requests from some datacenter/headless clients. The fetcher sends browser-like headers. If the GitHub Action receives a 403, the next step is to place only the LINQ fetch behind a small proxy; the display itself can remain on GitHub Pages.
