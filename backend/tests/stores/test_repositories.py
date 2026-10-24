#R1 — Successful query	Supabase returns records	The returned .data is passed back
#R2 — Foreign key violation	Error code 23503	HTTP 409
#R3 — Unique constraint violation	Error code 23505	HTTP 409
#R4 — Permission error	Error code 42501	HTTP 403
#R5 — Other access errors	Error codes PGRST301 and PGRST302	HTTP 403
#R6 — Required field violation	Error code 23502	HTTP 422
#R7 — Check constraint violation	Error code 23514	HTTP 422
#R8 — Numeric overflow	Error code 22003	HTTP 422
#R9 — Unknown database error	Any other APIError code	HTTP 503
#R10 — Network error	Supabase request raises RequestError	HTTP 503

#R11 — Find existing store	Query returns one valid store	Returns a Store instance with matching fields
#R12 — Store not found	Query returns an empty list	HTTP 404
#R13 — Find uses correct table	Inspect query construction	Uses table store
#R14 — Find filters by ID	Request store ID 5	Filters on storeid = 5
#R15 — Find limits results	Inspect query construction	Applies a limit of 1

#R16 — Insert store	Valid values supplied	Calls insert with the supplied values
#R17 — List all stores	No filter supplied	Orders by storeid
#R18 — Filter by store type	storetype="groceries"	Filters on storetype
#R19 — Update store	ID and changes supplied	Updates the correct record
#R20 — Delete store	ID supplied	Deletes the correct record and selects storeid