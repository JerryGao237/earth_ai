"""Sample GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL at a coordinate.

Usage:
    python examples/satellite_embedding_test.py --lon 116.39 --lat 39.9 --year 2023

Requirements:
    pip install earthengine-api
    earthengine authenticate
"""

from __future__ import annotations

import argparse
from typing import List

import ee


COLLECTION_ID = "GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL"


def init_ee(project: str | None = None) -> None:
    """Initialize Earth Engine SDK."""
    if project:
        ee.Initialize(project=project)
    else:
        ee.Initialize()


def get_annual_embedding_image(year: int) -> ee.Image:
    """Return the first annual embedding image for a given year."""
    start = f"{year}-01-01"
    end = f"{year + 1}-01-01"
    image = ee.ImageCollection(COLLECTION_ID).filterDate(start, end).first()
    if image is None:
        raise RuntimeError(f"No image found in {COLLECTION_ID} for year {year}")
    return ee.Image(image)


def sample_embedding_at_point(
    image: ee.Image,
    lon: float,
    lat: float,
    scale: int = 10,
) -> List[float]:
    """Sample the 64-D embedding at the provided coordinate."""
    point = ee.Geometry.Point([lon, lat])
    feature = image.sample(region=point, scale=scale, numPixels=1, geometries=False).first()
    if feature is None:
        raise RuntimeError("No sample returned. Check coordinate coverage or adjust scale.")

    band_names = image.bandNames().getInfo()
    properties = feature.toDictionary().getInfo()
    embedding = [properties[name] for name in band_names]
    return embedding


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lon", type=float, required=True, help="Longitude, e.g. 116.39")
    parser.add_argument("--lat", type=float, required=True, help="Latitude, e.g. 39.90")
    parser.add_argument("--year", type=int, default=2023, help="Year to query (default: 2023)")
    parser.add_argument("--scale", type=int, default=10, help="Sampling scale in meters")
    parser.add_argument("--project", type=str, default=None, help="Optional GCP project for EE")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_ee(args.project)
    image = get_annual_embedding_image(args.year)

    band_count = image.bandNames().size().getInfo()
    image_id = image.get("system:id").getInfo()

    embedding = sample_embedding_at_point(image, lon=args.lon, lat=args.lat, scale=args.scale)

    print(f"Collection: {COLLECTION_ID}")
    print(f"Image ID: {image_id}")
    print(f"Band count: {band_count}")
    print(f"Embedding length: {len(embedding)}")
    print(f"First 8 dims: {embedding[:8]}")


if __name__ == "__main__":
    main()
