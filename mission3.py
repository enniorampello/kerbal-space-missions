import time
import krpc

turn_start_altitude = 100
turn_end_altitude = 15000

conn = krpc.connect(name='Orbital flight')
vessel = conn.space_center.active_vessel
ap = vessel.auto_pilot

altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
srb_fuel = conn.add_stream(vessel.resources.amount, 'LiquidFuel')
periapsis_altitude = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
apoapsis_altitude = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
prograde_direction = conn.add_stream(getattr, vessel.flight(), 'prograde')
retrograde_direction = conn.add_stream(getattr, vessel.flight(), 'retrograde')

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

engine_separated = False
in_orbit = False
angle = 0.0
while True:
    if (altitude() >= turn_start_altitude and altitude() < turn_end_altitude):
        turn = (altitude() - turn_start_altitude)/(turn_end_altitude - turn_start_altitude)
        new_angle = 60.0 * turn
        if abs(new_angle - angle) > 0.5:
            angle = new_angle
            print(f'Turning to\t{90 + angle} degrees.')
            ap.target_pitch_and_heading(90 + angle, 90)
    if (srb_fuel() < 0.01 and engine_separated == False):
        print('Separating engines...')
        vessel.control.activate_next_stage()
        engine_separated = True
        in_orbit = True
    if abs(altitude() - apoapsis_altitude()) < 1000 and in_orbit:
        print('Rising apoapsis...')
        vessel.control.sas = True
        ap.target_direction = (0,1,0)
        vessel.control.activate_next_stage()
        ap.wait()
        while apoapsis_altitude() < 100000:
            ap.target_direction = (0,1,0)
            print(f'Apoapsis altitude: {apoapsis_altitude()} m')
            time.sleep(1)
        break
while True:
    if abs(altitude() - apoapsis_altitude()) < 100:
        ap.target_direction = (0,-1,0)
        ap.wait()
        vessel.control.activate_next_stage()
        while periapsis_altitude() > 25000:
            pass
    if vessel.flight(vessel.orbit.body.reference_frame).vertical_speed < -0.01:
        vessel.control.sas = True
        ap.target_pitch_and_heading(90, 90)
        vessel.control.activate_next_stage()
        break
    