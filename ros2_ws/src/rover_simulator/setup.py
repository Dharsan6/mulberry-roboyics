from setuptools import setup

package_name = 'rover_simulator'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name] if False else []),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Precision Sericulture Team',
    maintainer_email='agronomy@precision-sericulture.org',
    description='ROS 2 telemetry publisher and 4-state sequential rover simulator node',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simulator_node = rover_simulator.simulator_node:main',
        ],
    },
)
