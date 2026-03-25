#%%
from __future__ import annotations

import pm


def main() -> None:
    samples = [
        int,
        tuple[int, str],
        list[int],
    ]
    for sample in samples:
        carrier = pm.wrap(sample)
        print(f"{sample!r} -> {carrier}")


if __name__ == "__main__":
    main()
