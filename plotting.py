import gc
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np


def plot_stereo_spectrum(
    frequencies: np.ndarray,
    left_db: np.ndarray,
    right_db: np.ndarray,
    plot_mode: str,
    plot_path: Optional[Path],
    dpi: int = 300,
) -> None:
    frequency_range = (
        (frequencies >= 20)
        & (frequencies <= 20_000)
    )

    plt.figure(figsize=(10, 6))

    plt.semilogx(
        frequencies[frequency_range],
        left_db[frequency_range],
        label="Left Channel",
    )

    plt.semilogx(
        frequencies[frequency_range],
        right_db[frequency_range],
        label="Right Channel",
    )

    plt.title(
        "Left and Right Channel Frequency Spectrum"
    )
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Relative magnitude (dB)")

    plt.xlim(20, 20_000)
    plt.ylim(-120, 5)

    frequency_ticks = [
        20,
        50,
        100,
        200,
        500,
        1_000,
        2_000,
        5_000,
        10_000,
        20_000,
    ]

    frequency_labels = [
        "20",
        "50",
        "100",
        "200",
        "500",
        "1k",
        "2k",
        "5k",
        "10k",
        "20k",
    ]

    plt.xticks(
        frequency_ticks,
        frequency_labels,
    )

    plt.grid(
        which="both",
        linestyle="--",
        alpha=0.4,
    )

    plt.legend()
    plt.tight_layout()

    try:
        if plot_mode in ("save", "both"):
            plt.savefig(
                plot_path,
                dpi=dpi,
                bbox_inches="tight"
            )

            print(f"Plot saved to: {plot_path.resolve()}")
        if plot_mode in ("show", "both"):
            try:
                plt.show()
            except Exception:
                logger = __import__("logging").getLogger(__name__)
                logger.exception("Failed to show plot interactively")
    finally:
        try:
            plt.close("all")
        except Exception:
            pass

        try:
            gc.collect()
        except Exception:
            pass
