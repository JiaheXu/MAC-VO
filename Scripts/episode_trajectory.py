"""Persist the latest graph poses, including asynchronous pose revisions."""
import csv
import os


def save_trajectory(path, timestamps, poses, need_interp):
    if not (len(timestamps) == len(poses) == len(need_interp)):
        raise ValueError('Trajectory field lengths differ')
    if any(len(pose) != 7 for pose in poses):
        raise ValueError('Expected xyz and xyzw quaternion per pose')
    temporary = path.with_suffix(path.suffix + '.tmp')
    try:
        with temporary.open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['timestamp_ns', 'tx', 'ty', 'tz', 'qx', 'qy', 'qz', 'qw', 'need_interp'])
            for stamp, pose, lost in zip(timestamps, poses, need_interp):
                writer.writerow([int(stamp), *pose, int(lost)])
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
