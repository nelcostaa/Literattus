#!/usr/bin/env python3
"""Debug configuration loading."""

from app.core.config import settings

print("Configuration loaded:")
print(f"DB_HOST: {settings.DB_HOST}")
print(f"DB_PORT: {settings.DB_PORT}")
print(f"DB_USER: {settings.DB_USER}")
print(f"DB_PASSWORD length: {len(settings.DB_PASSWORD)}")
print(f"DB_NAME: {settings.DB_NAME}")
print(f"\nDATABASE_URL (first 60 chars): {settings.DATABASE_URL[:60]}...")
print(f"DATABASE_URL (last 40 chars): ...{settings.DATABASE_URL[-40:]}")
print(f"\nAPP_ENV: {settings.APP_ENV}")
print(f"DEBUG: {settings.DEBUG}")

