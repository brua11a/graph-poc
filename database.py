import os

from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Single driver instance shared across the app
driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


async def get_session():
    """FastAPI dependency that yields a Neo4j async session."""
    async with driver.session() as session:
        yield session


async def close_driver():
    """Call this on app shutdown to close the connection pool cleanly."""
    await driver.close()


async def verify_connectivity():
    """Optional: ping the database to confirm the connection works."""
    await driver.verify_connectivity()