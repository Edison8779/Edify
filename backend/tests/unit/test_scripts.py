"""
Seed and Reset Scripts Unit Tests
"""
import pytest
from app.scripts.seed import seed_data
from app.scripts.reset import reset_system


@pytest.mark.asyncio
async def test_seed_and_reset_scripts():
    # Run seed script
    await seed_data()

    # Run reset script
    await reset_system()
