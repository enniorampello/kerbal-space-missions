import time
import krpc

turn_start_altitude = 50
turn_end_altitude = 150

conn = krpc.connect(name='Orbital flight')
vessel = conn.space_center.active_vessel
ap = vessel.auto_pilot

altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
srb_fuel = conn.add_stream(vessel.resources.amount, 'SolidFuel')

vessel.control.sas = True
vessel.control.throttle = 1.0

print('Launch in:\n3')
time.sleep(1)
print('2')
time.sleep(1)
print('1')
time.sleep(1)
print('Go!')

ap.target_pitch_and_heading(90, 90)
ap.engage()
vessel.control.activate_next_stage()

chute_activated = False
while True:
    if (altitude() >= turn_start_altitude and altitude() < turn_end_altitude):
        turn = (altitude() - turn_start_altitude)/(turn_end_altitude - turn_start_altitude)
        angle = 30 * turn
        ap.target_pitch_and_heading(90 + angle, 90)
    if vessel.flight(vessel.orbit.body.reference_frame).vertical_speed < -0.01:
        ap.target_pitch_and_heading(90, 90)
        vessel.control.activate_next_stage()
        break