#API1 — Create store	POST /api/store with valid JSON	HTTP 201 and returned store
#API2 — Invalid create body	POST /api/store with a negative amount	HTTP 422
#API3 — Get existing store	GET /api/store/1	HTTP 200 and store data
#API4 — Invalid store ID	GET /api/store/0	HTTP 422
#API5 — Get all stores	GET /api/store	HTTP 200 and a list
#API6 — Filter stores	GET /api/store?storetype=groceries	HTTP 200; service receives the filter
#API7 — Update store	PATCH /api/store/1 with valid changes	HTTP 200 and updated store
#API8 — Empty update body	PATCH /api/store/1 with {}	HTTP 200 and existing store
#API9 — Null update field	PATCH /api/store/1 with {"address": null}	HTTP 422
#API10 — Delete store	DELETE /api/store/1	HTTP 204 and an empty response body
#API11 — Store not found	Service raises HTTP 404	HTTP 404 returned to client
#API12 — Authentication required	Request without required authentication	Verify the configured authentication behavior