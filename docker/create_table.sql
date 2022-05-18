DROP TABLE IF EXISTS search_keys CASCADE;
CREATE TABLE IF NOT EXISTS search_keys (
   id INT GENERATED ALWAYS AS IDENTITY,
   key TEXT UNIQUE,
   date_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   PRIMARY KEY(id)
);
DROP INDEX IF EXISTS search_keys_key_idx;
CREATE INDEX IF NOT EXISTS search_keys_key_idx ON search_keys(key);

DROP TABLE IF EXISTS search_index_int;
CREATE TABLE IF NOT EXISTS search_index_int (
   doc_id INT NOT NULL,
   key_id INT NOT NULL,
   date_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   value INT,
   PRIMARY KEY(doc_id, key_id),
   CONSTRAINT fk_key FOREIGN KEY(key_id) REFERENCES search_keys(id)
);
DROP INDEX IF EXISTS search_index_int_doc_key_idx;
--CREATE INDEX IF NOT EXISTS search_index_int_doc_key_idx ON search_index_int(doc_id, key_id);
--CLUSTER search_index_int_doc_key_idx ON search_index_int;

DROP INDEX IF EXISTS search_index_int_value_idx;
CREATE INDEX IF NOT EXISTS search_index_int_value_idx ON search_index_int(value);

DROP TABLE IF EXISTS search_index_int_array;
CREATE TABLE IF NOT EXISTS search_index_int_array (
   doc_id INT NOT NULL,
   key_id INT NOT NULL,
   date_inserted TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   value INT[],
   PRIMARY KEY(doc_id, key_id),
   CONSTRAINT fk_key FOREIGN KEY(key_id) REFERENCES search_keys(id)
);

DROP INDEX IF EXISTS search_index_int_array_doc_key_idx;
--CREATE INDEX IF NOT EXISTS search_index_int_array_doc_key_idx ON search_index_int_array(doc_id, key_id);
--CLUSTER search_index_int_array_doc_key_idx ON search_index_int_array;

DROP INDEX IF EXISTS search_index_int_array_value_idx;
CREATE INDEX IF NOT EXISTS search_index_int_array_value_idx ON search_index_int_array USING GIN(value);
