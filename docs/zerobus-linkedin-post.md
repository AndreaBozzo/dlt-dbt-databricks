# LinkedIn post — dltHub × Databricks Zerobus

From a Python event to a governed Delta table—without object-storage staging on the event path.

I just ran dlt's new per-resource Databricks Zerobus integration end to end on AWS:

`databricks_adapter(events, insert_api="zerobus")`

That one line keeps the normal dlt workflow—resources, schema normalization, load packages and
state—while sending this append-only event resource directly through Zerobus over Arrow Flight.

The live result:

→ 2 events landed in `zerobus_demo.dlt_events.zerobus_events`  
→ dlt package: `LOADED`  
→ failed jobs: `0`  
→ dedicated OAuth service principal with access to one table only

The detail I like most is the separation of concerns: dlt manages the pipeline contract; Zerobus
handles the direct-to-Delta data path; Unity Catalog keeps the boundary governed.

Small example, useful pattern—especially for telemetry, product events and other append-heavy
streams.

#dltHub #Databricks #Zerobus #DataEngineering #Lakehouse

## Publishing notes

- Attach `docs/assets/zerobus-linkedin-live.png`.
- Add the repository/example link in the first comment if the post itself should stay compact.
- The screenshot contains live query results but no workspace URL, workspace ID, warehouse ID, or
  credentials.
