```
<your base search> "runID"
| rex field=_raw "\"runID\":\"(?<runID>[^\"]+)\"
| stats latest(_time) as _time by runID
| table runID _time
| sort + runID

```

```
<your base search> "runID"
| rex field=_raw '"runID":"(?<runID>[^"]+)"'
| stats latest(_time) as _time by runID
| table runID _time
| sort + runID
```
