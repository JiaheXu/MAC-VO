"""Offline episode adapter for this MAC-VO checkout; no ROS runtime required."""
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
WEIGHT = ROOT/'Model/MACVO_FrontendCov.pth'


def episode_config(camera, baseline):
    config=yaml.safe_load((ROOT/'Config/Sequence/ego_episode.yaml').read_text())
    config['Camera']=dict(camera,bl=baseline)
    config['Odometry']['frontend']['args']['weight']=str(WEIGHT)
    return config


def backend_identity():
    from Odometry import MACVO as backend_module
    return dict(backend=str(Path(backend_module.__file__).resolve()),
                backend_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip())


class EpisodeOdometry:
    def __init__(self, config_path, trajectory_path):
        from Utility.Config import load_config
        from Odometry.MACVO import MACVO
        config,_=load_config(config_path)
        self.odometry=MACVO.from_config(config)
        self.trajectory_path=trajectory_path

    def process(self, index, timestamp, images, camera, baseline):
        import cv2
        import torch
        import pypose as pp
        from DataLoader import StereoFrame, StereoData
        if any(image.shape!=(480,640,3) for image in images) or len(images)!=2:
            raise ValueError('Expected two 640x480 BGR images')
        rgb=[torch.from_numpy(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)).permute(2,0,1).unsqueeze(0).float()/255 for im in images]
        k=torch.tensor([[[camera['fx'],0,camera['cx']],[0,camera['fy'],camera['cy']],[0,0,1]]])
        frame=StereoFrame(idx=[index],time_ns=[timestamp],stereo=StereoData(T_BS=pp.identity_SE3(1),K=k,baseline=torch.tensor([baseline]),time_ns=[timestamp],height=480,width=640,imageL=rgb[0],imageR=rgb[1]))
        self.odometry.run(frame)
        self.snapshot()

    def snapshot(self):
        from Scripts.episode_trajectory import save_trajectory
        frames=self.odometry.graph.frames.data
        save_trajectory(self.trajectory_path,frames['time_ns'].tolist(),frames['pose'].tolist(),frames['need_interp'].tolist())

    def terminate(self):
        try:
            self.odometry.terminate()
        finally:
            self.snapshot()
