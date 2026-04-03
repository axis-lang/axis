#%%
from __future__ import annotations

import protomorph


def main() -> None:
    samples = [
        int,
        tuple[int, str],
        list[int],
    ]
    for sample in samples:
        carrier = protomorph.wrap(sample)
        print(f"{sample!r} -> {carrier}")


if __name__ == "__main__":
    main()
