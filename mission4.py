import time
import krpc

turn_start_altitude = 250
turn_end_altitude = 45000

conn = krpc.connect(name='Orbital flight')
vessel = conn.space_center.active_vessel
ap = vessel.auto_pilot

altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
srb_fuel = conn.add_stream(vessel.resources.amount, 'SolidFuel')
engine_fuel = conn.add_stream(vessel.resources.amount, 'LiquidFuel')
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

boosters_separated = False
in_orbit = False
angle = 0.0
while True:
    if altitude() >= turn_start_altitude and altitude() < turn_end_altitude:
        turn = (altitude() - turn_start_altitude)/(turn_end_altitude - turn_start_altitude)
        new_angle = 85.0 * turn
        if abs(new_angle - angle) > 0.5:
            angle = new_angle
            print(f'Turning to\t{90 - angle} degrees.')
            ap.target_pitch_and_heading(90 - angle, 90)
    if srb_fuel() < 0.01 and boosters_separated == False:
        print('Separating boosters...')
        vessel.control.activate_next_stage()
        print('Activating engine...')
        vessel.control.throttle = 0.75
        vessel.control.activate_next_stage()
        boosters_separated = True
        in_orbit = True
    if altitude() > turn_end_altitude or apoapsis_altitude() > 100000:
        vessel.control.throttle = 0.0
    if engine_fuel() < 0.01:
        print('Separating engine...')
        vessel.control.activate_next_stage()
    if abs(altitude() - apoapsis_altitude()) < 500 and in_orbit:
        print('Rising periapsis...')
        ap.target_direction = prograde_direction()
        ap.wait()
        vessel.control.throttle = 1.0
        while abs(periapsis_altitude() - 100000) > 2000:
            ap.target_direction = prograde_direction()
            print(f'Periapsis altitude: {periapsis_altitude()} m')
        print(f'Complete! Periapsis altitude: {periapsis_altitude()} m')
        vessel.control.throttle = 0.0
        break
while True:
    if abs(altitude() - apoapsis_altitude()) < 500:
        print('Falling periapsis...')
        ap.target_direction = retrograde_direction()
        ap.wait()
        while periapsis_altitude() > 0:
            vessel.control.throttle = 0.25
            ap.target_direction = retrograde_direction()
            print(f'Periapsis altitude: {periapsis_altitude()} m')
        vessel.control.throttle = 0.0
    if vessel.flight(vessel.orbit.body.reference_frame).vertical_speed < -0.01 and altitude() < 10000:
        ap.target_pitch_and_heading(90, 90)
        vessel.control.activate_next_stage()
        break