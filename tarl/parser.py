from tarl.core import TARL

def parse(text: str) -> TARL:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    data = {"constraints": []}
    key = None
    for line in lines:
        if line.endswith(":") and line[:-1].isupper():
            key = line[:-1]
            continue
        if key == "CONSTRAINTS" and line.startswith("-"):
            data["constraints"].append(line[1:].strip())
        elif ":" in line:
            k, v = line.split(":", 1)
            data[k.strip().lower()] = v.strip()
    return TARL(
        intent=data["intent"],
        scope=data["scope"],
        authority=data["authority"],
        constraints=tuple(data["constraints"]),
    )
