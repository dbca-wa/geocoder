CREATE TABLE IF NOT EXISTS shack_address (
    id SERIAL NOT NULL PRIMARY KEY,
    object_id character varying(64) NOT NULL UNIQUE,
    address_text text NOT NULL,
    address_nice text,
    centroid geometry(Point,4326) NOT NULL,
    envelope geometry(Polygon,4326),
    data jsonb NOT NULL,
    tsv tsvector,
    owner text,
    boundary geometry(Polygon,4326)
);
CREATE FUNCTION shack_address_search_trigger() RETURNS trigger AS $$
begin
  new.tsv :=
    setweight(to_tsvector(coalesce(new.data->>'road_name','')), 'A') ||
    setweight(to_tsvector(coalesce(new.data->>'locality','')), 'A') ||
    setweight(to_tsvector(coalesce(new.data->>'lot_number','')), 'B') ||
    setweight(to_tsvector(coalesce(new.data->>'pin','')), 'B') ||
    setweight(to_tsvector(coalesce(new.data->>'reserve','')), 'B') ||
    setweight(to_tsvector(coalesce(new.address_text,'')), 'D');
  return new;
end
$$ LANGUAGE plpgsql;
CREATE TRIGGER shack_address_tsv_update BEFORE INSERT OR UPDATE ON shack_address FOR EACH ROW EXECUTE FUNCTION shack_address_search_trigger();
