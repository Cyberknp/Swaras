"""
saraga_mir_pipeline.py
======================
Production-grade pipeline for loading, preprocessing, and annotating tracks
from the Saraga Carnatic / Saraga Hindustani datasets via `mirdata`.

Designed for downstream Swara detection / pitch transcription models.

Usage
-----
# Process with default config (no audio download):
    python saraga_mir_pipeline.py --dataset saraga_carnatic --data_home /data/saraga

# Force re-download of missing audio (use sparingly):
    python saraga_mir_pipeline.py --dataset saraga_hindustani --data_home /data/saraga --download

# Use Log-Mel spectrogram instead of CQT:
    python saraga_mir_pipeline.py --dataset saraga_carnatic --feature mel

# Limit to N tracks (useful for smoke-testing):
    python saraga_mir_pipeline.py --dataset saraga_carnatic --max_tracks 10

Dependencies
------------
    pip install mirdata librosa numpy
"""

from __future__ import annotations

import argparse
import logging
import math
import sys
from dataclasses import dataclass, field
from typing import Generator, Optional

import librosa
import mirdata
import numpy as np

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("saraga_mir_pipeline")


# ---------------------------------------------------------------------------
# Config dataclass — single source of truth for all hyperparameters
# ---------------------------------------------------------------------------
@dataclass
class PipelineConfig:
    """Immutable hyperparameter store for the preprocessing pipeline.

    Attributes
    ----------
    dataset_name:
        mirdata dataset key — ``"saraga_carnatic"`` or ``"saraga_hindustani"``.
    data_home:
        Root directory where the dataset files reside (or will be downloaded to).
    sample_rate:
        Target audio sample rate in Hz. Resampled by librosa if the source differs.
    mono:
        If True, mix down multichannel audio to a single channel.
    feature_type:
        ``"cqt"`` — Constant-Q Transform, or ``"mel"`` — Log-Mel Spectrogram.
    hop_length:
        Number of audio samples between successive analysis frames.
    n_fft:
        FFT window size (used only for mel spectrogram).
    n_mels:
        Number of mel filter-bank channels (used only for mel spectrogram).
    n_bins:
        Total number of CQT frequency bins (used only for CQT).
    bins_per_octave:
        CQT bins per octave — 60 gives 5-cent resolution.
    fmin:
        Lowest frequency analysed (Hz). C1 ≈ 32.7 Hz is a sensible floor.
    max_tracks:
        Stop after yielding this many tracks (``None`` = no limit).
    download:
        Whether to attempt downloading absent audio files.
    """

    dataset_name: str = "saraga_carnatic"
    data_home: Optional[str] = None
    sample_rate: int = 22050
    mono: bool = True
    feature_type: str = "cqt"          # "cqt" | "mel"
    hop_length: int = 512
    n_fft: int = 2048
    n_mels: int = 128
    n_bins: int = 252                   # 7 octaves × 36 bins/octave
    bins_per_octave: int = 36
    fmin: float = librosa.note_to_hz("C1")  # ≈ 32.70 Hz
    max_tracks: Optional[int] = None
    download: bool = False
    # Derived — set automatically in __post_init__
    _valid_datasets: tuple = field(
        default=("saraga_carnatic", "saraga_hindustani"), init=False, repr=False
    )

    def __post_init__(self) -> None:
        if self.dataset_name not in self._valid_datasets:
            raise ValueError(
                f"dataset_name must be one of {self._valid_datasets}, "
                f"got '{self.dataset_name}'"
            )
        if self.feature_type not in ("cqt", "mel"):
            raise ValueError(
                f"feature_type must be 'cqt' or 'mel', got '{self.feature_type}'"
            )


# ---------------------------------------------------------------------------
# Dataset initialisation
# ---------------------------------------------------------------------------
def init_dataset(config: PipelineConfig) -> mirdata.core.Dataset:
    """Initialise (but do *not* download) a mirdata Saraga dataset object.

    Parameters
    ----------
    config:
        Pipeline configuration dataclass.

    Returns
    -------
    mirdata.core.Dataset
        Fully initialised dataset handle.  No audio is touched here.

    Notes
    -----
    Passing ``data_home=None`` lets mirdata use its default cache location
    (``~/mir_datasets``).  Explicit paths are forwarded verbatim.
    """
    logger.info(
        "Initialising mirdata dataset '%s' (data_home=%s)",
        config.dataset_name,
        config.data_home or "<mirdata default>",
    )
    dataset = mirdata.initialize(
        config.dataset_name,
        data_home=config.data_home,
    )

    if config.download:
        # Selective download: annotations only (small) unless audio is also absent.
        # Full audio bulk-download is intentionally left to the user's discretion.
        logger.warning(
            "--download flag set.  Downloading *annotation* index only. "
            "To fetch audio, run dataset.download(['audio']) outside this script."
        )
        try:
            dataset.download(partial_download=["metadata", "annotations"])
        except Exception as exc:  # noqa: BLE001
            logger.error("Annotation download failed: %s", exc)

    logger.info("Dataset initialised.  Total tracks: %d", len(dataset.track_ids))
    return dataset


# ---------------------------------------------------------------------------
# Annotation alignment utility
# ---------------------------------------------------------------------------
def align_pitch_to_frames(
    pitch_times: np.ndarray,
    pitch_hz: np.ndarray,
    tonic_hz: float,
    frame_times: np.ndarray,
) -> np.ndarray:
    """Resample a pitch contour to align with spectrogram frame timestamps,
    then normalise relative to the tonic in cents.

    Parameters
    ----------
    pitch_times:
        1-D array of pitch annotation timestamps (seconds), shape ``(N,)``.
    pitch_hz:
        1-D array of pitch values in Hz (may contain 0.0 for unvoiced frames),
        shape ``(N,)``.
    tonic_hz:
        Scalar tonic frequency in Hz.  Used as the reference for cent
        normalisation (0 cents == unison with tonic).
    frame_times:
        1-D array of spectrogram frame centre times (seconds), shape ``(M,)``.

    Returns
    -------
    np.ndarray
        Shape ``(M,)`` — frame-aligned pitch in **cents** relative to the
        tonic.  Frames that fall outside the annotation span, or where the
        original pitch was 0 Hz (unvoiced), are set to ``np.nan``.

    Notes
    -----
    Cent offset formula:
        ``cents = 1200 × log₂(pitch_hz / tonic_hz)``
    Unvoiced regions (pitch == 0) are masked *before* interpolation to
    prevent artefacts from log(0).
    """
    if tonic_hz <= 0:
        raise ValueError(f"tonic_hz must be positive, got {tonic_hz}")
    if pitch_times.shape != pitch_hz.shape:
        raise ValueError(
            f"pitch_times and pitch_hz must have the same shape; "
            f"got {pitch_times.shape} vs {pitch_hz.shape}"
        )

    # --- Step 1: Convert voiced Hz to cents; mask unvoiced regions ----------
    voiced_mask = pitch_hz > 0.0
    pitch_cents_raw = np.where(
        voiced_mask,
        1200.0 * np.log2(np.where(voiced_mask, pitch_hz, 1.0) / tonic_hz),
        np.nan,
    )

    # --- Step 2: Interpolate onto spectrogram frame grid --------------------
    # np.interp does not support NaN — interpolate Hz values then convert,
    # but we need to honour the voiced/unvoiced mask.  Strategy: interpolate
    # a binary voicing flag to detect frames where annotation is unvoiced.
    voicing_interp = np.interp(
        frame_times,
        pitch_times,
        voiced_mask.astype(float),
        left=np.nan,
        right=np.nan,
    )

    # Replace NaN sentinels (outside annotation range) and unvoiced frames
    # with a safe placeholder (0.0) for the pitch interpolation, then mask out.
    safe_cents = np.where(np.isnan(pitch_cents_raw), 0.0, pitch_cents_raw)
    aligned_cents = np.interp(
        frame_times,
        pitch_times,
        safe_cents,
        left=np.nan,
        right=np.nan,
    )

    # Re-apply unvoiced / out-of-range mask
    unvoiced_frame = (voicing_interp < 0.5) | np.isnan(voicing_interp)
    aligned_cents[unvoiced_frame] = np.nan

    return aligned_cents  # shape: (n_frames,)


# ---------------------------------------------------------------------------
# Feature extraction helpers  (internal — not part of public API)
# ---------------------------------------------------------------------------
def _compute_cqt(audio: np.ndarray, config: PipelineConfig) -> np.ndarray:
    """Compute a magnitude CQT and convert to dB scale.

    Returns
    -------
    np.ndarray
        Shape ``(n_bins, n_frames)``.
    """
    cqt = librosa.cqt(
        y=audio,
        sr=config.sample_rate,
        hop_length=config.hop_length,
        fmin=config.fmin,
        n_bins=config.n_bins,
        bins_per_octave=config.bins_per_octave,
    )
    return librosa.amplitude_to_db(np.abs(cqt), ref=np.max)


def _compute_mel(audio: np.ndarray, config: PipelineConfig) -> np.ndarray:
    """Compute a Log-Mel Spectrogram.

    Returns
    -------
    np.ndarray
        Shape ``(n_mels, n_frames)``.
    """
    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=config.sample_rate,
        n_fft=config.n_fft,
        hop_length=config.hop_length,
        n_mels=config.n_mels,
        fmin=config.fmin,
    )
    return librosa.power_to_db(mel, ref=np.max)


def _frame_times(feature: np.ndarray, config: PipelineConfig) -> np.ndarray:
    """Return the centre time (in seconds) for each spectrogram frame column.

    Parameters
    ----------
    feature:
        2-D feature array of shape ``(freq_bins, n_frames)``.
    config:
        Pipeline config (provides ``hop_length`` and ``sample_rate``).

    Returns
    -------
    np.ndarray
        Shape ``(n_frames,)``.
    """
    n_frames = feature.shape[1]
    return librosa.frames_to_time(
        np.arange(n_frames),
        sr=config.sample_rate,
        hop_length=config.hop_length,
    )


# ---------------------------------------------------------------------------
# Core streaming generator
# ---------------------------------------------------------------------------
def preprocess_tracks(
    dataset: mirdata.core.Dataset,
    config: PipelineConfig,
) -> Generator[tuple[str, np.ndarray, dict], None, None]:
    """Stream-process Saraga tracks one at a time, yielding preprocessed tuples.

    This is a *generator*: it holds at most one track's audio in memory at a
    time.  It is safe to iterate indefinitely over large datasets without
    exhausting RAM.

    Parameters
    ----------
    dataset:
        Initialised mirdata dataset (from :func:`init_dataset`).
    config:
        Pipeline configuration.

    Yields
    ------
    track_id : str
        The mirdata track identifier string.
    feature : np.ndarray
        Shape ``(freq_bins, n_frames)`` — CQT or Log-Mel spectrogram.
    annotation : dict
        Keys:
        ``"pitch_hz"``       — raw pitch array in Hz, shape ``(N,)``
        ``"pitch_times"``    — corresponding timestamps, shape ``(N,)``
        ``"pitch_aligned"``  — frame-aligned, tonic-normalised pitch in
                                cents, shape ``(n_frames,)``
        ``"tonic_hz"``       — scalar tonic frequency
        ``"track_title"``    — human-readable title (where available)

    Notes
    -----
    Tracks are skipped (with a logged warning) when:
    * The audio file path does not exist on disk.
    * librosa raises any exception during loading or feature extraction.
    * Pitch or tonic annotations are absent or malformed.
    """
    track_ids = dataset.track_ids
    processed = 0

    for track_id in track_ids:
        # --- Early exit if max_tracks cap reached ---------------------------
        if config.max_tracks is not None and processed >= config.max_tracks:
            logger.info("Reached max_tracks=%d limit, stopping.", config.max_tracks)
            break

        logger.debug("Inspecting track: %s", track_id)

        # --- Load mirdata track object (metadata only at this point) --------
        try:
            track = dataset.track(track_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load track object '%s': %s", track_id, exc)
            continue

        # --- Gate on audio file existence BEFORE loading --------------------
        audio_path: Optional[str] = getattr(track, "audio_path", None)
        if audio_path is None:
            logger.warning("Track '%s' has no audio_path attribute — skipping.", track_id)
            continue

        import os
        if not os.path.isfile(audio_path):
            logger.warning(
                "Audio file absent for track '%s' (%s) — skipping.",
                track_id,
                audio_path,
            )
            continue

        # --- Extract annotations (pitch contour + tonic) --------------------
        pitch_times: Optional[np.ndarray] = None
        pitch_hz: Optional[np.ndarray] = None
        tonic_hz: Optional[float] = None

        try:
            # mirdata annotation objects differ slightly between datasets;
            # both Saraga variants expose .pitch and .tonic.
            pitch_annotation = track.pitch
            tonic_annotation = track.tonic

            if pitch_annotation is None:
                raise ValueError("pitch annotation is None")
            if tonic_annotation is None:
                raise ValueError("tonic annotation is None")

            # Saraga pitch annotation: NoteData or F0Data — access .times / .frequencies
            pitch_times = np.asarray(pitch_annotation.times, dtype=np.float64)
            pitch_hz = np.asarray(pitch_annotation.frequencies, dtype=np.float64)

            # Tonic may be a scalar or a single-element array
            tonic_val = tonic_annotation.value if hasattr(tonic_annotation, "value") else tonic_annotation
            tonic_hz = float(np.atleast_1d(tonic_val)[0])

            if math.isnan(tonic_hz) or tonic_hz <= 0:
                raise ValueError(f"Invalid tonic_hz: {tonic_hz}")

        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Annotation extraction failed for track '%s': %s — skipping.",
                track_id,
                exc,
            )
            continue

        # --- Load audio (deferred to here, only when we know file exists) ---
        try:
            audio, _ = librosa.load(
                audio_path,
                sr=config.sample_rate,
                mono=config.mono,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "librosa failed to load audio for track '%s': %s — skipping.",
                track_id,
                exc,
            )
            continue

        # --- Compute spectrogram feature ------------------------------------
        try:
            if config.feature_type == "cqt":
                feature = _compute_cqt(audio, config)
            else:
                feature = _compute_mel(audio, config)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Feature extraction failed for track '%s': %s — skipping.",
                track_id,
                exc,
            )
            del audio  # release memory immediately on failure
            continue

        # Audio waveform is no longer needed once feature is computed
        del audio

        # --- Align pitch annotation to spectrogram frame grid ---------------
        try:
            frame_times = _frame_times(feature, config)
            pitch_aligned = align_pitch_to_frames(
                pitch_times=pitch_times,
                pitch_hz=pitch_hz,
                tonic_hz=tonic_hz,
                frame_times=frame_times,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Pitch alignment failed for track '%s': %s — skipping.",
                track_id,
                exc,
            )
            del feature
            continue

        # --- Build annotation dict ------------------------------------------
        track_title: str = getattr(track, "title", track_id) or track_id
        annotation: dict = {
            "pitch_hz": pitch_hz,
            "pitch_times": pitch_times,
            "pitch_aligned": pitch_aligned,   # shape: (n_frames,), in cents
            "tonic_hz": tonic_hz,
            "track_title": track_title,
        }

        logger.info(
            "Processed track '%s' (%s) | feature: %s | frames: %d",
            track_id,
            track_title,
            str(feature.shape),
            feature.shape[1],
        )

        processed += 1
        yield track_id, feature, annotation

    logger.info("Pipeline complete.  Tracks yielded: %d", processed)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="saraga_mir_pipeline",
        description=(
            "Stream-preprocess Saraga Carnatic / Hindustani tracks for "
            "Swara detection / pitch transcription."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--dataset",
        choices=["saraga_carnatic", "saraga_hindustani"],
        default="saraga_carnatic",
        help="Which Saraga sub-dataset to process.",
    )
    parser.add_argument(
        "--data_home",
        default=None,
        help="Root directory for mirdata cache.  Defaults to ~/mir_datasets.",
    )
    parser.add_argument(
        "--feature",
        choices=["cqt", "mel"],
        default="cqt",
        help="Spectrogram feature type to compute.",
    )
    parser.add_argument(
        "--hop_length",
        type=int,
        default=512,
        help="STFT/CQT hop length in samples.",
    )
    parser.add_argument(
        "--max_tracks",
        type=int,
        default=None,
        help="Stop after N tracks (useful for smoke tests).",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Attempt to download missing annotation index files.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )
    return parser


def main() -> None:
    """CLI entry point — parses arguments, builds config, runs pipeline."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    config = PipelineConfig(
        dataset_name=args.dataset,
        data_home=args.data_home,
        feature_type=args.feature,
        hop_length=args.hop_length,
        max_tracks=args.max_tracks,
        download=args.download,
    )

    logger.info("Pipeline config: %s", config)

    dataset = init_dataset(config)

    # --- Iterate the generator — this is where work actually happens --------
    # In a real training loop you would feed (feature, annotation) to your
    # model here.  This main() simply demonstrates the pipeline is functional.
    total_frames = 0
    for track_id, feature, annotation in preprocess_tracks(dataset, config):
        n_frames = feature.shape[1]
        total_frames += n_frames
        voiced_ratio = float(np.mean(~np.isnan(annotation["pitch_aligned"])))

        logger.info(
            "  track_id=%-40s | shape=%-18s | tonic=%.2f Hz | voiced=%.1f%%",
            track_id,
            str(feature.shape),
            annotation["tonic_hz"],
            voiced_ratio * 100,
        )
        # feature and annotation go out of scope here → memory reclaimed

    logger.info("Grand total frames processed: %d", total_frames)


if __name__ == "__main__":
    main()
