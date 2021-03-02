from .models import QcInput
import math
from django.utils import timezone

def get_stats(prod_sessions, start_time, end_time):
    if start_time > end_time:
        return None

    # To avoid double counting while calculating total_pieces_processed
    # Rectified should always be ignored.
    # Rejected should be ignored if the piece came back after being marked defective.
    total_pieces_processed = 0
    ftt, defective, rejected, rectified, defects, operators, helpers, sam, target = 0, 0, 0, 0, 0, 0, 0, 0, 0
    duration_seconds, elapsed_seconds, remaining_seconds = 0, 0, 0
    buyers, styles, shifts, lines = '', '', '', ''
    
    # Accumulate metrics for all production sessions
    for prod_session in prod_sessions:

        if lines != '':
            lines += ', '
        lines += str(prod_session.line.number)

        style = prod_session.style
        if styles != '':
            styles += ', '
        styles += f'{style.number} {style.name}'

        operators += prod_session.operators
        helpers += prod_session.helpers
        sam += style.sam
        
        if buyers != '':
            buyers += ', '
        buyers += style.order.buyer.buyer

        if shifts != '':
            shifts += ', '
        shifts += prod_session.get_session_name()

        qc_inputs = prod_session.qcinput_set.filter(datetime__gte=start_time, datetime__lt=end_time)
        for qc_input in qc_inputs:
            if qc_input.input_type == QcInput.FTT:
                ftt += qc_input.quantity
                total_pieces_processed += qc_input.quantity
            elif qc_input.input_type == QcInput.DEFECTIVE:
                defective += qc_input.quantity
                defects += qc_input.defects.count() * qc_input.quantity
                total_pieces_processed += qc_input.quantity
            elif qc_input.input_type == QcInput.REJECTED:
                rejected += qc_input.quantity
                if qc_input.is_ftt:
                    total_pieces_processed += qc_input.quantity
            elif qc_input.input_type == QcInput.RECTIFIED:
                rectified += qc_input.quantity

        # For accurate calculation bring time period in range of current production session
        adjusted_start_time, adjusted_end_time = start_time, end_time
        if start_time < prod_session.start_time:
            adjusted_start_time = prod_session.start_time
        if end_time > prod_session.end_time:
            adjusted_end_time = prod_session.end_time
        if adjusted_start_time > adjusted_end_time:
            continue
        
        target += prod_session.target * ((adjusted_end_time - adjusted_start_time)/(prod_session.end_time - prod_session.start_time))
        
        current_time = timezone.now()
        duration_seconds += (adjusted_end_time - adjusted_start_time).total_seconds()
        if current_time > adjusted_end_time:
            elapsed_seconds += (adjusted_end_time - adjusted_start_time).total_seconds()
            remaining_seconds += 0
        elif current_time < adjusted_start_time:
            elapsed_seconds += 0
            remaining_seconds += (adjusted_end_time - adjusted_start_time).total_seconds()
        else:
            elapsed_seconds += (current_time - adjusted_start_time).total_seconds()
            remaining_seconds = (adjusted_end_time - current_time).total_seconds()
    
    output = ftt + rectified
    manpower = operators + helpers

    stats = {
        "ftt": ftt,
        "line": lines,
        "target": round(target),
        "production": output,
        "buyer": buyers,
        "style": styles,
        "defective": defective,
        "rectified": rectified,
        "rejected": rejected,
        "total_pieces_processed": total_pieces_processed,
        "operators": operators,
        "helpers": helpers,
        "shift": shifts,
    }

    # Calculate efficiency
    if manpower > 0 and duration_seconds > 0:
        target_efficiency = target * sam * 100 / (manpower * duration_seconds / 60)
        stats["target_efficiency"] = f'{round(target_efficiency, 2)}%'
        if elapsed_seconds > 0:
            efficiency = output * sam * 100 / (manpower * elapsed_seconds / 60)
            stats["efficiency"] = f'{round(efficiency, 2)}%'
            stats["target_efficiency_variance"] = f'{round(target_efficiency - efficiency, 2)}%'
    
    # Calculate RTT Stats
    if duration_seconds > 0:
        rtt = target * (elapsed_seconds / duration_seconds)
        stats["rtt"] = round(rtt)
        stats["rtt_variance"] = round(rtt - output)

        if manpower > 0 and elapsed_seconds > 0:
            rtt_efficiency = rtt * sam * 100 / (manpower * elapsed_seconds / 60)
            stats["rtt_efficiency"] = f'{round(rtt_efficiency, 2)}%'
            stats["rtt_efficiency_variance"] = f'{round(rtt_efficiency - efficiency, 2)}%'

    # Calculate Target Variance
    stats["target_variance"] = round(target - output)

    # Calculate Projected Output
    if elapsed_seconds > 0:
        production_rate = output / elapsed_seconds
        stats["projected"] = round(output + production_rate * remaining_seconds)

    # Calcaulate Input type rates
    if total_pieces_processed > 0:
        stats["ftt_percentage"] = f'{round(ftt * 100 / total_pieces_processed, 2)}%'
        stats["reject_percentage"] = f'{round(rejected * 100 / total_pieces_processed, 2)}%'
        stats["defective_percentage"] = f'{round(defective * 100 / total_pieces_processed, 2)}%'
        dhu = defects * 100 / total_pieces_processed
        stats["dhu"] = round(dhu, 2)
    if defective > 0:
        stats["rectified_percentage"] = f'{round(rectified * 100 / defective, 2)}%'

    return stats


import os
from .models import ProductionSession
from datetime import timedelta
BREAK_START_HOUR = int(os.environ['BREAK_START_HOUR'])
BREAK_START_MINUTE = int(os.environ['BREAK_START_MINUTE'])
BREAK_MINUTES = int(os.environ['BREAK_MINUTES'])

def get_prod_sessions_and_timings(day):
    day = timezone.localtime(day)
    day_start_time = day.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end_time = day.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Multi day production sessions will not be selected with this method
    day_production_sessions = ProductionSession.objects.filter(
        start_time__gte=day_start_time,
        end_time__lte=day_end_time,
    )
    session_start_times, session_end_times = [], []
    for prod_session in day_production_sessions:
        session_start_times.append(timezone.localtime(prod_session.start_time))
        session_end_times.append(timezone.localtime(prod_session.end_time))
    
    if len(session_start_times) > 0 and len(session_end_times) > 0:
        production_start_time = min(session_start_times)
        production_end_time = max(session_end_times)
    else:
        production_start_time = day.replace(hour=8, minute=0, second=0, microsecond=0)
        production_end_time =  day.replace(hour=16, minute=0, second=0, microsecond=0)
    production_duration = production_end_time - production_start_time

    break_start_time = day.replace(hour=BREAK_START_HOUR, minute=BREAK_START_MINUTE, second=0, microsecond=0)
    if break_start_time > production_start_time and break_start_time < production_end_time:
        break_duration = timedelta(minutes=BREAK_MINUTES)
    else:
        break_duration = timedelta(minutes=0)

    return day_production_sessions, production_start_time, production_duration, break_start_time, break_duration