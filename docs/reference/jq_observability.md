# Using jq to observe log data

## Log inspection (jq one-liners)

Assumes JSON Lines (server.jsonl, events.jsonl, debug.jsonl) per ADR-0017.

### Errors only

```sh
jq 'select(.level | IN("ERROR","CRITICAL"))' saskan_logs/server.jsonl
```

### Handshakes with latencies

```sh
jq 'select(.evt=="HELLO") | {ts, outcome, latency_ms, session_id}' saskan_logs/server.jsonl
```

### Event counts by type

```sh
jq -r '.evt' saskan_logs/events.jsonl | sort | uniq -c | sort -nr
```

### Recent connections (open/close)

```sh
jq -r 'select(.evt=="CONN_OPEN" or .evt=="CONN_CLOSE") | [.ts,.evt,.addr] | @tsv' saskan_logs/server.jsonl | tail
```

### Messages sent/received (names only)

```sh
jq -r 'select(.evt=="MSG_SENT" or .evt=="MSG_RECV") | [.ts,.evt,.name] | @tsv' saskan_logs/events.jsonl
```

### Filter a session/correlation

```sh
jq --arg sid "$SESSION_ID" 'select(.session_id==$sid)' saskan_logs/*.jsonl
jq --arg corr "$CORR"      'select(.corr==$corr)'      saskan_logs/*.jsonl
```

### Largest payloads (if enabled)

```sh
jq 'select(.payload!=null) | {ts,evt,name: .name?,size:(.payload | tostring | length)}' saskan_logs/events.jsonl \
  | sort -t: -k3 -nr | head
```
