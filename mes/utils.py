from .models import QcInput
import math
from django.utils import timezone
import datetime

def get_stats(prod_sessions, start_time, end_time):
    # limit data to before current time
    if end_time > timezone.now():
        end_time = timezone.now()

    if start_time > end_time:
        return None

    # To avoid double counting while calculating total_pieces_processed
    # Rectified should always be ignored.
    # Rejected should be ignored if the piece came back after being marked defective.
    total_pieces_processed = 0
    ftt, defective, rejected, rectified, defects, operators, helpers, sam, target = 0, 0, 0, 0, 0, 0, 0, 0, 0
    duration_seconds, elapsed_seconds, remaining_seconds = 0, 0, 0
    buyers, styles, shifts, lines = set(), set(), set(), set()
    
    # Accumulate metrics for all production sessions
    for prod_session in prod_sessions:
        style = prod_session.style
        styles.add(style)
        buyers.add(style.order.buyer)
        shifts.add(prod_session)
        lines.add(prod_session.line)

        operators += prod_session.operators
        helpers += prod_session.helpers
        sam += style.sam
        
        qc_inputs = prod_session.qcinput_set.filter(datetime__gte=start_time, datetime__lt=end_time)
        for qc_input in qc_inputs:
            if qc_input.input_type == QcInput.FTT:
                ftt += qc_input.quantity
                total_pieces_processed += qc_input.quantity
            elif qc_input.input_type == QcInput.DEFECTIVE:
                defective += qc_input.quantity
                defects += qc_input.operation_defects.count() * qc_input.quantity
                total_pieces_processed += qc_input.quantity
            elif qc_input.input_type == QcInput.REJECTED:
                rejected += qc_input.quantity
                if qc_input.is_ftt:
                    total_pieces_processed += qc_input.quantity
            elif qc_input.input_type == QcInput.RECTIFIED:
                rectified += qc_input.quantity
        # if rectified count is more than defective count.
        # There difference should be added to total_pieces_processed count
        if rectified > defective:
            total_pieces_processed += rectified - defective

        # For accurate calculation bring time period in range of current production session
        adjusted_start_time, adjusted_end_time = start_time, end_time
        if start_time < prod_session.start_time:
            adjusted_start_time = prod_session.start_time
        if end_time > prod_session.end_time:
            adjusted_end_time = prod_session.end_time
        if adjusted_start_time > adjusted_end_time:
            continue
        
        breaks_duration = get_breaks_duration([prod_session]).total_seconds()
        prod_session_duration = (prod_session.end_time - prod_session.start_time).total_seconds()
        # Adjust production duration for breaks
        production_duration = prod_session_duration - breaks_duration
        computation_time_range_duration = (adjusted_end_time - adjusted_start_time).total_seconds()
        if computation_time_range_duration > production_duration:
            computation_time_range_duration = production_duration
        production_duration_fraction = computation_time_range_duration / production_duration
        target += prod_session.target * production_duration_fraction
        
        current_time = timezone.now()
        duration_seconds += computation_time_range_duration
        if current_time > adjusted_end_time:
            elapsed_seconds += computation_time_range_duration
            remaining_seconds += 0
        elif current_time < adjusted_start_time:
            elapsed_seconds += 0
            remaining_seconds += computation_time_range_duration
        else:
            elapsed_seconds_for_this_session = (current_time - adjusted_start_time).total_seconds()
            breaks_duration_elapsed = get_breaks_duration_elapsed(adjusted_start_time, adjusted_end_time, prod_session).total_seconds()
            elapsed_seconds += elapsed_seconds_for_this_session - breaks_duration_elapsed
            remaining_seconds += (adjusted_end_time - current_time).total_seconds()
    
    output = ftt + rectified
    manpower = operators + helpers

    stats = {
        "ftt": ftt,
        "line": ", ".join([str(ele.number) for ele in lines]),
        "target": round(target),
        "production": output,
        "buyer": ", ".join([ele.buyer for ele in buyers]),
        "style": ", ".join([ele.number for ele in styles]),
        "defective": defective,
        "rectified": rectified,
        "rejected": rejected,
        "total_pieces_processed": total_pieces_processed,
        "operators": operators,
        "helpers": helpers,
        "shift": ", ".join([ele.get_session_name() for ele in shifts]),
    }
    
    # from django.db.models import Q
    # total_produced = 0
    # for style in styles:
    #     qc_inputs = QcInput.objects.filter(production_session__style=style)
    #     qc_inputs = qc_inputs.filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED))
    #     for qc_input in qc_inputs:
    #         total_produced += qc_input.quantity
    # style_quantity = sum([style.quantity() for style in styles])
    # stats["wip"] = style_quantity - total_produced
    # if stats["wip"] < 0:
    #     stats["wip"] = 0

    # Calculate efficiency
    if manpower > 0 and duration_seconds > 0:
        target_efficiency = target * sam * 100 / (manpower * duration_seconds / 60)
        stats["target_efficiency"] = f'{round(target_efficiency, 2)}%'
        if elapsed_seconds > 0:
            efficiency = output * sam * 100 / (manpower * elapsed_seconds / 60)
            stats["efficiency"] = f'{round(efficiency, 2)}%'
            stats["target_efficiency_variance"] = f'{round(target_efficiency - efficiency, 2)}%'
    
    # Calculate RTT Stats
    if duration_seconds > 0 and remaining_seconds > 0:
        rtt = target * (elapsed_seconds / duration_seconds)
        stats["rtt"] = round(rtt)
        stats["rtt_variance"] = round(rtt) - output

        if manpower > 0 and elapsed_seconds > 0:
            rtt_efficiency = rtt * sam * 100 / (manpower * elapsed_seconds / 60)
            stats["rtt_efficiency"] = f'{round(rtt_efficiency, 2)}%'
            stats["rtt_efficiency_variance"] = f'{round(rtt_efficiency - efficiency, 2)}%'

    # Calculate Target Variance
    stats["target_variance"] = round(target) - output

    # Calculate Projected Output
    if elapsed_seconds > 0:
        production_rate = output / elapsed_seconds
        stats["projected"] = round(output + production_rate * remaining_seconds)

    # Calcaulate Input type rates
    if total_pieces_processed > 0:
        stats["ftt_percentage"] = f'{round(ftt * 100 / total_pieces_processed, 2)}%'
        stats["rejected_percentage"] = f'{round(rejected * 100 / total_pieces_processed, 2)}%'
        stats["defective_percentage"] = f'{round(defective * 100 / total_pieces_processed, 2)}%'
        dhu = defects * 100 / total_pieces_processed
        stats["dhu"] = round(dhu, 2)
    if defective > 0:
        stats["rectified_percentage"] = f'{round(rectified * 100 / defective, 2)}%'

    return stats


from mes.serializers.query_serializers import DetailFilterQuerySerializer

def get_filter_values_from_query_params(query_params):
    query_params = DetailFilterQuerySerializer(data=query_params)
    query_params.is_valid(raise_exception=True)
    start_time = timezone.localtime(query_params.validated_data['startDateTime'])
    end_time = timezone.localtime(query_params.validated_data['endDateTime'])
    order = query_params.validated_data['order']
    style = query_params.validated_data['style']
    line = query_params.validated_data['line']
    affectMetricsByTime = query_params.validated_data['affectMetricsByTime']
    return start_time, end_time, order, style, line, affectMetricsByTime

def get_prod_sessions_for_time_range(start_time, end_time):
    from .models import ProductionSession
    return ProductionSession.objects.filter(
        start_time__gte=start_time,
        end_time__lte=end_time,
    )

def get_prod_sessions_timings(prod_sessions):
    session_start_times, session_end_times = [], []
    for prod_session in prod_sessions:
        session_start_times.append(timezone.localtime(prod_session.start_time))
        session_end_times.append(timezone.localtime(prod_session.end_time))
    if len(session_start_times) > 0 and len(session_end_times) > 0:
        prod_start_time = min(session_start_times)
        prod_end_time = max(session_end_times)
    else:
        day = timezone.localtime(timezone.now())
        prod_start_time = day.replace(hour=8, minute=0, second=0, microsecond=0)
        prod_end_time =  day.replace(hour=16, minute=0, second=0, microsecond=0)
    return prod_start_time, prod_end_time

def get_prod_sessions_breaks(prod_sessions):
    breaks = set()
    for prod_session in prod_sessions:
        breaks.update(prod_session.get_breaks_in_datetime())
    return list(breaks)

def get_breaks_duration(prod_sessions):
    prod_breaks = get_prod_sessions_breaks(prod_sessions)
    duration = datetime.timedelta(seconds=0)
    for prod_break in prod_breaks:
        duration += prod_break.end_time - prod_break.start_time
    return duration

def get_breaks_duration_elapsed(start_time, end_time, prod_session):
    prod_breaks = get_prod_sessions_breaks([prod_session])
    breaks_duration_elapsed = datetime.timedelta(seconds=0)
    current_date_time = timezone.localtime(timezone.now())
    for prod_break in prod_breaks:
        # If break timing is between the provided time range include the break duration in total
        if prod_break.start_time >= start_time and prod_break.end_time <= end_time:
            if current_date_time > prod_break.start_time:
                break_duration_elapsed = current_date_time - prod_break.start_time
                break_duration = prod_break.end_time - prod_break.start_time
                if break_duration_elapsed > break_duration:
                    breaks_duration_elapsed += break_duration
                else:
                    breaks_duration_elapsed += break_duration_elapsed
    return breaks_duration_elapsed

def get_prod_hours(prod_sessions):
    prod_start_time, prod_end_time = get_prod_sessions_timings(prod_sessions)
    prod_breaks = get_prod_sessions_breaks(prod_sessions)
    prod_hours = []
    pointer_date_time = prod_start_time
    while pointer_date_time < prod_end_time:
        part_start = pointer_date_time
        part_end = part_start + datetime.timedelta(hours=1)
        for prod_break in prod_breaks:
            if part_start < prod_break.start_time:
                if part_end > prod_break.start_time:
                    part_end = prod_break.start_time
            elif part_start < prod_break.end_time:
                time_diff = prod_break.end_time - part_start
                part_start += time_diff
                part_end += time_diff
        if part_end > prod_end_time:
            part_end = prod_end_time
        if part_start < part_end:
            prod_hours.append((part_start, part_end))
        pointer_date_time = part_end
    return prod_hours

def get_filtered_prod_sessions(start_time, end_time, order_id, style_id, line_id):
    prod_sessions = get_prod_sessions_for_time_range(start_time, end_time)
    prod_sessions = apply_filters_on_prod_sessions(prod_sessions, order_id, style_id, line_id)
    return prod_sessions

def apply_filters_on_prod_sessions(prod_sessions, order_id, style_id, line_id):
    if order_id is not None:
        prod_sessions = prod_sessions.filter(style__order__id=order_id)
    if style_id is not None:
        prod_sessions = prod_sessions.filter(style__id=style_id)
    if line_id is not None:
        prod_sessions = prod_sessions.filter(line__id=line_id)
    return prod_sessions

def apply_filters_on_defects(defects_filter, order_id, style_id, line_id):
    if order_id is not None:
        defects_filter = defects_filter.filter(qcinput__production_session__style__order__id=order_id)
    if style_id is not None:
        defects_filter = defects_filter.filter(qcinput__production_session__style__id=style_id)
    if line_id is not None:
        defects_filter = defects_filter.filter(qcinput__production_session__id=line_id)
    return defects_filter

def get_filtered_qc_inputs(start_time, end_time, order_id, style_id, line_id):
    if start_time is not None and end_time is not None:
        qc_inputs = QcInput.objects.filter(datetime__gte=start_time, datetime__lte=end_time)
    else:
        qc_inputs = QcInput.objects.filter()
    qc_inputs = apply_filters_on_qc_inputs(qc_inputs, order_id, style_id, line_id)
    return qc_inputs

def apply_filters_on_qc_inputs(qc_inputs, order_id, style_id, line_id):
    if order_id is not None:
        qc_inputs = qc_inputs.filter(production_session__style__order__id=order_id)
    if style_id is not None:
        qc_inputs = qc_inputs.filter(production_session__style__id=style_id)
    if line_id is not None:
        qc_inputs = qc_inputs.filter(production_session__line__id=line_id)
    return qc_inputs

def get_production_target_for_order(order, start_time, end_time, style_id, line_id):
    prod_sessions = get_filtered_prod_sessions(start_time, end_time, order.id, style_id, line_id)
    target = 0
    for session in prod_sessions:
        target += session.target
    return target

def get_production_target_for_style(style, start_time, end_time, order_id, line_id):
    prod_sessions = get_filtered_prod_sessions(start_time, end_time, order_id, style.id, line_id)
    target = 0
    for session in prod_sessions:
        target += session.target
    return target