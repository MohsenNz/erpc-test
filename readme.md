# Run

```bash
nohup python3 rely-test.py > output.log 2>&1 &
```

# Check running

```bash
ps aux | grep rely-test.py
```

# Stop

```bash
kill <PID>
```

# Find PID

```bash
ps aux | grep rely-test.py | grep -v grep
 ```
