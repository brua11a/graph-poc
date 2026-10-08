"""
Initializes Neo4j schema constraints for the app.

Run this once against a fresh database:
    python init_schema.py

Safe to re-run — all statements use IF NOT EXISTS.
"""
import asyncio
from database import driver, close_driver

CONSTRAINTS = [
    "CREATE CONSTRAINT course_id_unique IF NOT EXISTS "
    "FOR (c:Course) REQUIRE c.ID IS UNIQUE",

    # Person is the shared label across Student/Teacher/Admin (multi-label people
    # get this once). These two constraints cover identity + login for ALL of them,
    # replacing what used to be separate per-label Teacher/Student constraints.
    "CREATE CONSTRAINT person_id_unique IF NOT EXISTS "
    "FOR (p:Person) REQUIRE p.ID IS UNIQUE",

    "CREATE CONSTRAINT person_email_unique IF NOT EXISTS "
    "FOR (p:Person) REQUIRE p.email IS UNIQUE",

    # Composite uniqueness: no two courses may share the same name+semester.
    # NOTE: composite/multi-property uniqueness constraints require
    # Neo4j ENTERPRISE Edition. On Community Edition this line will fail —
    # comment it out and rely on MERGE (see routers/courses.py) instead.
    "CREATE CONSTRAINT course_name_semester_unique IF NOT EXISTS "
    "FOR (c:Course) REQUIRE (c.name, c.semester) IS UNIQUE",

    # Existence constraints (Neo4j Enterprise Edition only —
    # comment these out if you're on Community Edition)
    # "CREATE CONSTRAINT course_name_required IF NOT EXISTS "
    # "FOR (c:Course) REQUIRE c.name IS NOT NULL",
    # "CREATE CONSTRAINT course_semester_required IF NOT EXISTS "
    # "FOR (c:Course) REQUIRE c.semester IS NOT NULL",
]


async def init_schema():
    async with driver.session() as session:
        for statement in CONSTRAINTS:
            await session.run(statement)
            print(f"Applied: {statement.splitlines()[0]}...")
    await close_driver()
    print("Schema initialization complete.")


if __name__ == "__main__":
    asyncio.run(init_schema())