# Offline episode integration

`episode_backend.py` owns MAC-VO creation, 640x480 RGB conversion, stereo frame construction with real nanosecond acquisition timestamps, and per-step trajectory snapshots. `episode_trajectory.py` saves atomic graph snapshots. Config: `../Config/Sequence/ego_episode.yaml`; weights resolve inside this checkout's `Model/` directory.

From the parent ego_data_processing directory, use the unchanged command:

```bash
python3 -m utils.process_episode odometry output/rectified/20260907020254 --output output/rectified-640/20260907020254/odometry
```

The pipeline inserts this checkout and `.runtime/episode` into its import path. To restore isolated typing dependencies from the parent directory:

```bash
python3 -m pip install --target MAC-VO/.runtime/episode -r MAC-VO/Scripts/episode_requirements.txt
```

FlowFormer must be initialized at the commit recorded by this checkout (`git submodule update --init -- Module/Network/FlowFormer`). The currently unused DPVO baseline is not needed. The machine's CUDA solver preload documented in `../docs/RECTIFIED_PIPELINE.md` is still required. Existing outputs are preserved; choose a new output directory. The top-level `odometry/trajectory.py` is only a compatibility import.
