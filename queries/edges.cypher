CALL apoc.load.json("file:///nodes/terms.json") YIELD value AS ctrow
MATCH (c:Curriculum {id: ctrow.curriculum_id})
MATCH (ct:CurriculumTerm {id: ctrow.id})
MERGE (c)-[:HAS_TERM]->(ct);

CALL apoc.load.json("file:///edges/term_subjects.json") YIELD value AS csrow
MATCH (c:Curriculum {id: csrow.curriculum_id})-[:HAS_TERM]->(ct:CurriculumTerm {sem: csrow.sem})
MATCH (su:Subject {code: csrow.subject_code})
MERGE (ct)-[:CONTAINS]->(su);

CALL apoc.load.json("file:///edges/curriculum_faculties.json") YIELD value AS ccrow
MATCH (c:Curriculum {id: ccrow.curriculum_id})
MATCH (fa:Faculty {id: ccrow.faculty_id})
MERGE (c)-[:IS_IN]->(fa);

CALL apoc.load.json("file:///nodes/groups.json") YIELD value AS grow
MATCH (g:Group {id: grow.id})
MATCH (ac:AcademicCycle {id: grow.cycle_id})
MATCH (r:Room {id: grow.room_id})
MERGE (g)-[:IN_CYCLE]->(ac)
MERGE (g)-[:IN_ROOM]->(r);

CALL apoc.load.json("file:///edges/group_subject.json") YIELD value AS gsrow
MATCH (g:Group {id: gsrow.group_id})
MATCH (su:Subject {code: gsrow.subject_code})
MERGE (g)-[:OF_SUBJECT]->(su);

CALL apoc.load.json("file:///edges/teacher_group.json") YIELD value AS row
MATCH (t:Teacher {idx: row.teacher_idx})
MATCH (g:Group {id: row.group_id})
MERGE (t)-[:TEACHES]->(g);

CALL apoc.load.json("file:///edges/teacher_faculty.json") YIELD value AS tfrow
MATCH (t:Teacher {idx: tfrow.teacher_idx})
MATCH (fa:Faculty {id: tfrow.faculty_id})
MERGE (t)-[:WORKS_AT]->(fa);

CALL apoc.load.json("file:///edges/student_enrolled.json") YIELD value AS serow
MATCH (st:Student {idx: serow.student_idx})
MATCH (c:Curriculum {id: serow.curriculum_id})
MERGE (st)-[:ENROLLED]->(c);

CALL apoc.load.json("file:///edges/student_currently_at.json") YIELD value AS scarow
MATCH (st:Student {idx: scarow.student_idx})
MATCH (ct:CurriculumTerm {id: scarow.term_id})
MERGE (st)-[:CURRENTLY_AT]->(ct);

CALL apoc.load.json("file:///edges/student_registered.json") YIELD value AS srrow
MATCH (st:Student {idx: srrow.student_idx})
MATCH (g:Group {id: srrow.group_id})
MERGE (st)-[:REGISTERED_IN]->(g);
