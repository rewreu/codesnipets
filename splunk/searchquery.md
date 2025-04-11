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

```python
import re

# Replace this with your fixed prefix
prefix = "xx-yy"  # change to your actual fixed prefix
pattern = re.compile(rf"{re.escape(prefix)}-[a-zA-Z0-9]{{5}}")

matches = []

with open("your_file.txt", "r") as file:
    for line in file:
        found = pattern.findall(line)
        matches.extend(found)

print(matches)

```
