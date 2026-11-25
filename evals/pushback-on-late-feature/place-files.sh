#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
# Shift the fixture's clock so the run happens at ~75% of a 36h hackathon (9h left).
python3 - <<'PY'
import re, datetime as dt
p = "PROGRESS.md"; t = open(p).read()
now = dt.datetime.now(dt.timezone.utc)
f = lambda d: d.strftime("%Y-%m-%d %H:%M UTC")
t = re.sub(r"^Started:.*$", "Started: " + f(now - dt.timedelta(hours=27)), t, flags=re.M)
t = re.sub(r"^Deadline:.*$", "Deadline: " + f(now + dt.timedelta(hours=9)), t, flags=re.M)
open(p, "w").write(t)
PY
