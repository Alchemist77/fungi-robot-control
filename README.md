# Title: Sensorimotor Control of Robots Mediated by Fungal Mycelia

## Abstract
Living tissues are still far from being used as practical components in biohybrid robots
due to limitations in lifespan, sensitivity to environmental factors, and stringent culture
procedures. In this paper, we introduce fungal mycelium as an easy to use and robust, living
component in biohybrid robots. We construct two biohybrid robots that use the
electrophysiological activity of living mycelium to control its artificial actuators. The mycelia
sense their environment and issue action potential-like spiking voltages as control signals to the
motors and valves of the robots we designed and built. The paper highlights two key innovations:
First, a vibration and EMI shielded mycelium electrical interface that allows for stable, long-term
electrophysiological bioelectric recordings during untethered, mobile operation. Second, we
develop a control architecture for robots inspired by neural central pattern generators,
incorporating rhythmic patterns of positive and negative spikes from the living mycelia. We used
these signals to control a walking soft robot as well as a wheeled hard robot. We demonstrated
the use of these mycelium to respond to environmental cues by using UV light stimulation to
augment the robots’ gaits.


## run
```
python3 collecting_fungi_data.py
```
```
python3 calc_fungi_data.py
```
```
python3 fungi_motor_control.py
```
