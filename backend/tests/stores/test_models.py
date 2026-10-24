#M1 — Valid store creation	All four fields supplied with valid values	StoreCreate is created successfully
#M2 — Empty enterprise name	enterprisename=""	Validation error
#M3 — Empty store type	storetype=""	Validation error
#M4 — Empty address	address=""	Validation error
#M5 — Negative minimum order	minimumorderamount=-1	Validation error
#M6 — Zero minimum order	minimumorderamount=0	Accepted
#M7 — Extra field supplied	Add a field such as unknownfield	Validation error
#M8 — Valid store update	Supply only address	Accepted; other fields aren't required
#M9 — Null update field	Supply address=None	Accepted by the model; the service should reject it
#M10 — Valid full store	Include all creation fields and a positive storeid	Store is created successfully
#M11 — Invalid store ID	storeid=0 or a negative ID	Validation error
#M12 — Missing required field	Omit address when creating a store	Validation error