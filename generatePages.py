# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 22:40:06 2025

@author: vinee
"""

import pandas as pd
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).parent

CSV_FILE = BASE_DIR / "recipes.csv"

# Output directory: same folder as CSS/template so relative links work
OUTPUT_DIR = BASE_DIR /"recipes"  # or BASE_DIR / "recipes" if you prefer a subfolder

env = Environment(
    loader=FileSystemLoader(str(BASE_DIR)),
    autoescape=select_autoescape(["html"])
 )
template = env.get_template("recipes_template.html")


def split_multi(value, sep="||"):
    """Split a field into a list by the given separator."""
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(sep) if str(part).strip()]


def split_tags(value):
    if pd.isna(value):
        return []
    return [tag.strip() for tag in str(value).split(",") if tag.strip()]


def build_nav(df: pd.DataFrame):
    """Build {category: [{title, slug}, ...]} for sidebar navigation."""
    nav = {}
    for _, row in df.iterrows():
        slug = str(row.get("slug", "")).strip()
        title = str(row.get("title", "")).strip() or "Untitled"
        if not slug:
            continue
        category = str(row.get("category", "Other")).strip() or "Other"

        nav.setdefault(category, []).append({"title": title, "slug": slug})

    # sort recipes within each category by title
    for cat in nav:
        nav[cat] = sorted(nav[cat], key=lambda r: r["title"].lower())

    return nav


def main():
    df = pd.read_csv(CSV_FILE)

    nav = build_nav(df)

    for _, row in df.iterrows():
        slug = str(row.get("slug", "")).strip()
        if not slug:
            continue

        title = row.get("title", "Untitled Recipe")
        category = row.get("category", "Recipe")
        short_description = row.get("short_description", "")
        prep_time = row.get("prep_time", "")
        cook_time = row.get("cook_time", "")
        servings = row.get("servings", "")

        ingredients = split_multi(row.get("ingredients", ""), sep="||")
        instructions = split_multi(row.get("instructions", ""), sep="||")
        instructions = [ins.split(".",1)[1] for ins in instructions]
        
        tags = split_tags(row.get("tags", ""))

        health_note = row.get("health_note", "")
        benefits = row.get("benefits", "")
        source = row.get("source", "")

        raw_image = row.get("image", "")
        if pd.isna(raw_image) or str(raw_image).strip() == "":
            # Fallback: local image named by slug (you can change this)
            image_url = f"images/{slug}.jpg"
        else:
            image_url = str(raw_image).strip()

        context = {
            "slug": slug,
            "title": title,
            "category": category,
            "short_description": short_description,
            "prep_time": prep_time,
            "cook_time": cook_time,
            "servings": servings,
            "ingredients": ingredients,
            "instructions": instructions,
            "tags": tags,
            "health_note": health_note,
            "benefits": benefits,
            "source": source,
            "image_url": image_url,
            "nav": nav,  # full nav for sidebar
        }

        html = template.render(**context)

        out_file = OUTPUT_DIR / f"{slug}.html"
        out_file.write_text(html, encoding="utf-8")
        print(f"Generated {out_file.name}")


if __name__ == "__main__":
    main()
