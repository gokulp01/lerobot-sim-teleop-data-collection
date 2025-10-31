from setuptools import find_packages, setup

setup(
    name="gym_lowcostrobot",
    version="0.0.1",
    description="Low cost robot gymnasium environments",
    author="Julien Perez",
    author_email="julien.perez@epita.fr",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gymnasium>=0.29",
        "mujoco>=3.0",
        "PyOpenGL==3.1.1a1",
        "viser>=1.0.0",
        "scipy>=1.0.0",
        "trimesh>=3.0.0",
        "pynput>=1.7.0",
        "pygame>=2.0.0",
        "rich>=13.0.0",
        "opencv-python>=4.0.0",
    ],
)
