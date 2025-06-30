from datetime import datetime, timedelta

MAX_DRIVING_HOURS_DAILY = 11.0
MAX_ON_DUTY_HOURS_DAILY = 14.0
MAX_CYCLE_HOURS_8_DAYS = 70.0
MIN_OFF_DUTY_HOURS_RESET = 10.0
MANDATORY_BREAK_DRIVING_HOURS_THRESHOLD = 8.0
MANDATORY_BREAK_DURATION_MINS = 30
FUEL_STOP_INTERVAL_MILES = 1000.0
FUEL_STOP_DURATION_MINS = 30
PICKUP_DROPOFF_DURATION_HOURS = 1.0

STATUS_OFF_DUTY = "OFF"
STATUS_DRIVING = "DR"
STATUS_ON_DUTY_NOT_DRIVING = "ON"
STATUS_SLEEPER_BERTH = "SB"

class HOSCalculator:
    def __init__(self, start_time: datetime, initial_cycle_used_hours: float):
        self.current_time = start_time
        self.cycle_hours_used = initial_cycle_used_hours
        self.daily_logs = []
        self.stops = []

        self.current_day_driving_hours = 0.0
        self.current_day_on_duty_hours = 0.0

        self.driving_hours_since_last_break = 0.0
        self.last_break_taken_time = None

        self.last_activity_end_time = start_time

        self.daily_logs.append([])
        self._add_log_entry_internal(
            self.current_time, self.current_time, STATUS_OFF_DUTY, "Initial state before trip activities"
        )


    def _add_log_entry_internal(self, start_dt, end_dt, status, description=""):
        if start_dt >= end_dt:
            return

        self.daily_logs[-1].append({
            'start_time': start_dt.isoformat(),
            'end_time': end_dt.isoformat(),
            'status': status,
            'description': description
        })
        self.last_activity_end_time = end_dt


    def _add_log_entry(self, start_dt, end_dt, status, description=""):
        if start_dt >= end_dt:
            return

      
        if not self.daily_logs:
            self.daily_logs.append([])
        
      
        if self.daily_logs[-1] and self.last_activity_end_time < start_dt:
            gap_duration = (start_dt - self.last_activity_end_time).total_seconds() / 3600.0
            if gap_duration > 0.001:
                self._add_log_entry_internal(self.last_activity_end_time, start_dt, STATUS_OFF_DUTY, f'Off-duty (implicit gap: {gap_duration:.2f} hrs)')

  
        if self.daily_logs[-1] and end_dt.date() > datetime.fromisoformat(self.daily_logs[-1][-1]['end_time']).date():
            
            last_entry_end_on_previous_day = datetime.fromisoformat(self.daily_logs[-1][-1]['end_time'])
            midnight_next_day = (last_entry_end_on_previous_day + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            
            if last_entry_end_on_previous_day < midnight_next_day:
                self._add_log_entry_internal(last_entry_end_on_previous_day, midnight_next_day, STATUS_OFF_DUTY, 'Off-duty at end of day (implicit boundary)')
            
            self.daily_logs.append([]) 
        
            self.current_day_driving_hours = 0.0
            self.current_day_on_duty_hours = 0.0
            self.driving_hours_since_last_break = 0.0
            self.last_break_taken_time = None
            self.last_activity_end_time = self.current_time 

        if not self.daily_logs: 
            self.daily_logs.append([])
        elif not self.daily_logs[-1]: 
             self.daily_logs.append([]) 

        self._add_log_entry_internal(start_dt, end_dt, status, description)


    def _enforce_10_hour_off_duty_reset(self):
        if self.current_day_driving_hours >= MAX_DRIVING_HOURS_DAILY or \
           self.current_day_on_duty_hours >= MAX_ON_DUTY_HOURS_DAILY:
            
            off_duty_start = self.current_time
            off_duty_end = off_duty_start + timedelta(hours=MIN_OFF_DUTY_HOURS_RESET)
            
            self._add_log_entry(off_duty_start, off_duty_end, STATUS_OFF_DUTY, 'Required 10-hour off-duty reset')
            self.stops.append({'type': '10-Hr Off Duty', 'time': off_duty_start.isoformat(), 'duration_hours': MIN_OFF_DUTY_HOURS_RESET})
            self.current_time = off_duty_end
            
            self.current_day_driving_hours = 0.0
            self.current_day_on_duty_hours = 0.0
            self.driving_hours_since_last_break = 0.0
            self.last_break_taken_time = None
       
            if self.daily_logs and self.daily_logs[-1]:
                self.daily_logs.append([])
            self.last_activity_end_time = self.current_time


    def _enforce_30_minute_break(self):
        if self.driving_hours_since_last_break >= MANDATORY_BREAK_DRIVING_HOURS_THRESHOLD and \
           (self.last_break_taken_time is None or (self.current_time - self.last_break_taken_time).total_seconds() / 3600.0 >= MANDATORY_BREAK_DRIVING_HOURS_THRESHOLD):
            
            break_start = self.current_time
            break_end = break_start + timedelta(minutes=MANDATORY_BREAK_DURATION_MINS)
            
            self._add_log_entry(break_start, break_end, STATUS_OFF_DUTY, 'Mandatory 30-min break')
            self.stops.append({'type': 'Mandatory 30-Min Break', 'time': break_start.isoformat(), 'duration_minutes': MANDATORY_BREAK_DURATION_MINS})
            self.current_time = break_end
            self.last_break_taken_time = break_end
            self.driving_hours_since_last_break = 0.0


    def _handle_fuel_stop(self, current_miles_driven):
        pass


    def calculate_logs(self, total_driving_hours: float, total_distance_miles: float):
        remaining_driving_hours = total_driving_hours
        miles_driven_current_trip = 0.0
        miles_driven_since_last_fuel = 0.0

        pickup_start = self.current_time
        pickup_end = pickup_start + timedelta(hours=PICKUP_DROPOFF_DURATION_HOURS)
        self._add_log_entry(pickup_start, pickup_end, STATUS_ON_DUTY_NOT_DRIVING, 'Pickup')
        self.current_time = pickup_end
        self.current_day_on_duty_hours += PICKUP_DROPOFF_DURATION_HOURS
        self.cycle_hours_used += PICKUP_DROPOFF_DURATION_HOURS
        self.stops.append({'type': 'Pickup', 'time': pickup_start.isoformat(), 'duration_hours': PICKUP_DROPOFF_DURATION_HOURS})

        segment_duration_hours = 1.0

        while remaining_driving_hours > 0.001:
            self._enforce_10_hour_off_duty_reset()

            self._enforce_30_minute_break()

            available_driving_in_segment = min(
                remaining_driving_hours,
                segment_duration_hours,
                MAX_DRIVING_HOURS_DAILY - self.current_day_driving_hours,
                MAX_ON_DUTY_HOURS_DAILY - self.current_day_on_duty_hours,
                MAX_CYCLE_HOURS_8_DAYS - self.cycle_hours_used
            )

            if available_driving_in_segment <= 0.001:
                if remaining_driving_hours > 0.001:
                    self._enforce_10_hour_off_duty_reset()
                    continue
                else:
                    break

            driving_start_segment = self.current_time
            driving_end_segment = driving_start_segment + timedelta(hours=available_driving_in_segment)

            self._add_log_entry(driving_start_segment, driving_end_segment, STATUS_DRIVING, f'Driving ({available_driving_in_segment:.2f} hrs)')
            self.current_time = driving_end_segment
            remaining_driving_hours -= available_driving_in_segment
            self.current_day_driving_hours += available_driving_in_segment
            self.current_day_on_duty_hours += available_driving_in_segment
            self.cycle_hours_used += available_driving_in_segment
            self.driving_hours_since_last_break += available_driving_in_segment

            scale_factor = available_driving_in_segment / total_driving_hours if total_driving_hours > 0 else 0
            miles_driven_segment = scale_factor * total_distance_miles
            
            miles_driven_current_trip += miles_driven_segment
            miles_driven_since_last_fuel += miles_driven_segment

            if miles_driven_since_last_fuel >= FUEL_STOP_INTERVAL_MILES:
                fuel_start = self.current_time
                fuel_end = fuel_start + timedelta(minutes=FUEL_STOP_DURATION_MINS)
                self._add_log_entry(fuel_start, fuel_end, STATUS_ON_DUTY_NOT_DRIVING, 'Fueling stop')
                self.stops.append({'type': 'Fuel Stop', 'time': fuel_start.isoformat(), 'duration_minutes': FUEL_STOP_DURATION_MINS})
                self.current_time = fuel_end
                self.current_day_on_duty_hours += FUEL_STOP_DURATION_MINS / 60.0
                self.cycle_hours_used += FUEL_STOP_DURATION_MINS / 60.0
                miles_driven_since_last_fuel = 0.0

        dropoff_start = self.current_time
        dropoff_end = dropoff_start + timedelta(hours=PICKUP_DROPOFF_DURATION_HOURS)
        self._add_log_entry(dropoff_start, dropoff_end, STATUS_ON_DUTY_NOT_DRIVING, 'Dropoff')
        self.stops.append({'type': 'Dropoff', 'time': dropoff_start.isoformat(), 'duration_hours': PICKUP_DROPOFF_DURATION_HOURS})
        self.current_time = dropoff_end
        self.current_day_on_duty_hours += PICKUP_DROPOFF_DURATION_HOURS
        self.cycle_hours_used += PICKUP_DROPOFF_DURATION_HOURS

        return {
            'daily_logs': self.daily_logs,
            'stops': self.stops,
            'final_cycle_used_hours': self.cycle_hours_used
        }

def calculate_trip_logs(
    start_time: datetime,
    total_driving_hours: float,
    total_distance_miles: float,
    initial_cycle_used_hours: float
):
    calculator = HOSCalculator(start_time, initial_cycle_used_hours)
    return calculator.calculate_logs(total_driving_hours, total_distance_miles)
