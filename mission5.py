import krpc
import maneuvers
turn_start_altitude = 250
turn_end_altitude = 45000

conn = krpc.connect(name='Orbital flight')
maneuvers.take_off_suborbit(conn)
maneuvers.land(conn)