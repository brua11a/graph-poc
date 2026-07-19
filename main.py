from neo4j import GraphDatabase, Driver
from dotenv import dotenv_values
from neo4j.exceptions import Neo4jError


def establish_connection(AUTH, PORT) -> Driver:
    URI = f"bolt://localhost:{PORT}"
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()
    print("Connection established.")
    return driver

def create_nodes(driver: Driver, DB: str) -> None:
    summary = driver.execute_query("""
        CREATE (a:Person {name: $name})
        CREATE (b:Person {name: $friendName})
        CREATE (a)-[:KNOWS]->(b)
        """,
        name="Alice", friendName="David",
        database_=DB,
    ).summary
    print("Created {nodes_created} nodes in {time} ms.".format(
        nodes_created=summary.counters.nodes_created,
        time=summary.result_available_after
    ))

def read_nodes(driver: Driver, DB: str) -> None:
    records, summary, keys = driver.execute_query("""
        MATCH (p:Person)-[:KNOWS]->(:Person)
        RETURN p.name AS name
        """,
        database_=DB,
    )

    # Loop through results and do something with them
    for record in records:
        print(record.data())  # get record as dict

    # Summary information
    print("The query `{query}` returned {records_count} records in {time} ms.".format(
        query=summary.query, records_count=len(records),
        time=summary.result_available_after
    ))

def update_nodes(driver: Driver, DB: str) -> None:
    records, summary, keys = driver.execute_query("""
        MATCH (p:Person {name: $name})
        SET p.age = $age
        """,
        name="Alice", age=42,
        database_=DB,
    )
    print(f"Query counters: {summary.counters}.")

def cause_error(driver: Driver, DB: str) -> None:
    try:
        driver.execute_query('MATCH (p:Person) RETURN', database_=DB)
    except Neo4jError as e:
        if e.find_by_gql_status('42001'):
            # Neo.ClientError.Statement.SyntaxError
            # special handling of syntax error in query
            print(e.message)
        elif e.find_by_gql_status('42NFF'):
            # Neo.ClientError.Security.Forbidden
            # special handling of user not having CREATE permissions
            print(e.message)
        else:
            # handling of all other exceptions
            print(e.message)

def main():
    config = dotenv_values(".env")
    UNAME = config["USERNAME"]
    PASSWD = config["PASSWORD"]
    DB = config["DATABASE"]
    PORT = config["PORT"]
    driver = establish_connection((UNAME, PASSWD), PORT)

    create_nodes(driver, DB)
    read_nodes(driver, DB)
    update_nodes(driver, DB)
    cause_error(driver, DB)


    driver.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()