import time

final_speed = 5

def take_off_orbit(conn, vessel, ap):
    turn_start_altitude = 250
    turn_end_altitude = 45000

    vessel = conn.space_center.active_vessel
    ap = vessel.auto_pilot

    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    srb_fuel = conn.add_stream(vessel.resources.amount, 'SolidFuel')
    engine_fuel = conn.add_stream(vessel.resources.amount, 'LiquidFuel')
    periapsis_altitude = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
    apoapsis_altitude = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
    prograde_direction = conn.add_stream(getattr, vessel.flight(), 'prograde')

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

# takeoff on a two-stages vessel
def take_off_suborbit(conn):
    vessel = conn.space_center.active_vessel
    ap = vessel.auto_pilot

    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')

    ap.target_pitch_and_heading(90, 90)
    ap.engage()
    vessel.control.throttle = 1.0

    print('Launch in:')
    time.sleep(1)
    print('3')
    time.sleep(1)
    print('2')
    time.sleep(1)
    print('1')
    time.sleep(1)
    print('Go!')

    vessel.control.activate_next_stage()

    turn_start_altitude = 250
    turn_end_altitude = 25000
    angle = 0.0
    while vessel.flight(vessel.orbit.body.reference_frame).vertical_speed > -0.01:
        if altitude() >= turn_start_altitude and altitude() < turn_end_altitude:
            turn = (altitude() - turn_start_altitude)/(turn_end_altitude - turn_start_altitude)
            new_angle = 90.0 * turn
            if abs(new_angle - angle) > 0.5:
                angle = new_angle
                print(f'Turning to\t{90 - angle} degrees.')
                ap.target_pitch_and_heading(90 - angle, 90)
    ap.disengage()
    vessel.control.activate_next_stage()

# assuming:
# - the vessel has legs
# - the vessel has fuel
# - the vessel has an engine
# - the vessel has only the last stage
def land(conn):
    vessel = conn.space_center.active_vessel
    ap = vessel.auto_pilot
    
    altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
    speed = conn.add_stream(getattr, vessel.flight(vessel.orbit.body.reference_frame), 'speed')
    vertical_speed = conn.add_stream(getattr, vessel.flight(vessel.orbit.body.reference_frame), 'vertical_speed')

    ap.sas = True
    ap.sas_mode = ap.sas_mode.retrograde

    while altitude() > 10000:
        pass
    print('Initiating landing procedure...')
    time.sleep(1)
    print('Deploying landing gear...')
    for leg in vessel.parts.legs:
        leg.deployed = True
    print('Deployment complete.')

    while altitude() > 1000:
        pass

    start_altitude = altitude()
    start_speed = speed()
    full_throttle = 1.0
    zero_throttle = 0.0
    print('Performing landing maneuver...')
    
    while altitude() > 2:
        target_speed = (altitude()/start_altitude)*start_speed
        print(f'Target speed: {target_speed} m/s.')
        if target_speed < speed() - 5 and vertical_speed() < -1:
            if altitude() < 150:
                ap.engage()
                ap.target_pitch_and_heading(90, 90)
                full_throttle = 0.5
                zero_throttle = 0.1
            vessel.control.throttle = full_throttle
        else:
            vessel.control.throttle = zero_throttle
        
        print(f'Altitude: {altitude()} m. Speed: {speed()}')
    vessel.control.throttle = 0.0
    print('Landing complete!')