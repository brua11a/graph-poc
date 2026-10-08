CYPHER 25 ALTER CURRENT GRAPH TYPE SET {

	(t:Teacher => {
		idx :: STRING,
		name :: STRING NOT NULL,
		surname :: STRING NOT NULL,
		phone :: STRING,
		degree :: STRING NOT NULL,
		photo :: STRING,
		working_since :: DATE NOT NULL
	}) REQUIRE t.idx IS KEY,

	(st:Student => {
		idx :: STRING,
		name :: STRING NOT NULL,
		surname :: STRING NOT NULL,
		phone :: STRING,
		photo :: STRING,
		joined :: ZONED DATETIME NOT NULL
	}) REQUIRE st.idx IS KEY,

	(u:User => {
		email :: STRING,
		passwd_hash :: STRING NOT NULL
	}) REQUIRE u.email IS KEY,

//	(a:Admin => {}),

	(o:Opinion => {
		id :: INTEGER,
		grade :: FLOAT NOT NULL,
		content :: STRING,
		submit :: ZONED DATETIME NOT NULL
	}) REQUIRE o.id IS KEY,

	(g:Group => {
		id :: INTEGER,
		weekday :: INTEGER NOT NULL,
		type :: STRING NOT NULL,
		number :: INTEGER NOT NULL,
		pnp :: STRING NOT NULL,
		capacity :: INTEGER NOT NULL,
		start_hr :: ZONED TIME NOT NULL,
		end_time :: ZONED TIME NOT NULL
	}) REQUIRE g.id IS KEY,

	(r:Room => {
		id :: INTEGER,
		building :: STRING NOT NULL,
		room_num :: STRING NOT NULL
	}) REQUIRE r.id IS KEY,

	(ac:AcademicCycle => {
		id :: INTEGER,
		year :: STRING NOT NULL,
		season :: STRING NOT NULL
	}) REQUIRE ac.id IS KEY,

	(su:Subject => {
		code :: STRING,
		name :: STRING NOT NULL,
		ects :: INTEGER NOT NULL
	}) REQUIRE su.code IS KEY,

	(ct:CurriculumTerm => {
		id :: INTEGER,
		sem :: INTEGER NOT NULL
	}) REQUIRE ct.id IS KEY,

	(c:Curriculum => {
		id :: INTEGER,
		name :: STRING NOT NULL
	}) REQUIRE c.id IS KEY,

	(fa:Faculty => {
		id :: INTEGER,
		name :: STRING NOT NULL,
		full_name :: STRING NOT NULL
	}) REQUIRE fa.id IS KEY,

	(st)-[:WRITES => {}]->(o),
	(st)-[:ENROLLED => {}]->(c),
	(st)-[:REGISTERED_IN => {}]->(g),
	(st)-[:CURRENTLY_AT => {}]->(ct),
	(o)-[:ON => {}]->(g),
	(c)-[:HAS_TERM => {}]->(ct),
	(c)-[:IS_IN => {}]->(fa),
	(ct)-[:CONTAINS => {}]->(su),
	(g)-[:OF_SUBJECT => {}]->(su),
	(g)-[:IN_CYCLE => {}]->(ac),
	(g)-[:IN_ROOM => {}]->(r),
	(t)-[:WORKS_AT => {}]->(fa),
	(t)-[:TEACHES => {}]->(g)

}
