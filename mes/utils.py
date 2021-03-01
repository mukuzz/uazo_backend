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
                defects += qc_input.defects.count()
                total_pieces_processed += qc_input.quantity
            elif qc_input.input_type == QcInput.REJECTED:
                rejected += qc_input.quantity
                if qc_input.is_ftt:
                    total_pieces_processed += qc_input.quantity
            elif qc_input.input_type == QcInput.RECTIFIED:
                rectified += qc_input.quantity

        # For accurate calculation bring time period in range of current production session
        if start_time < prod_session.start_time:
            start_time = prod_session.start_time
        if end_time > prod_session.end_time:
            end_time = prod_session.end_time
        if start_time > end_time:
            continue
        
        target += prod_session.target * ((end_time - start_time)/(prod_session.end_time - prod_session.start_time))
        
        current_time = timezone.now()
        duration_seconds += (end_time - start_time).total_seconds()
        if current_time > end_time:
            elapsed_seconds += (end_time - start_time).total_seconds()
            remaining_seconds += 0
        elif current_time < start_time:
            elapsed_seconds += 0
            remaining_seconds += (end_time - start_time).total_seconds()
        else:
            elapsed_seconds += (current_time - start_time).total_seconds()
            remaining_seconds = (end_time - current_time).total_seconds()
    
    output = ftt + rectified

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
        "operators": operators,
        "helpers": helpers,
    }
    
    stats["shift"] = shifts

    if output > 0:
        # Calculate RTT
        try:
            rtt = target * (elapsed_seconds / duration_seconds)
            stats["rtt"] = round(rtt)

            # Calculate efficiency
            manpower = operators + helpers
            efficiency = output * sam * 100 / (manpower * elapsed_seconds / 60)
            stats["efficiency"] = f'{round(efficiency, 2)}%'
            rtt_efficiency = rtt * sam * 100 / (manpower * elapsed_seconds / 60)
            stats["target_efficiency"] = f'{round(rtt_efficiency, 2)}%'

            # Calculate Variance
            stats["rtt_variance"] = round(rtt - output)
            stats["target_variance"] = round(target - output)
            stats["target_efficiency_variance"] = f'{round(rtt_efficiency - efficiency, 2)}%'

            # Calculate Projected Output
            production_rate = output / elapsed_seconds
            stats["projected"] = round(output + production_rate * remaining_seconds)
        except ZeroDivisionError:
            pass

    try:
        if total_pieces_processed != 0:
            stats["ftt_percentage"] = f'{round(ftt * 100 / total_pieces_processed, 2)}%'
            stats["reject_percentage"] = f'{round(rejected * 100 / total_pieces_processed, 2)}%'
            stats["defective_percentage"] = f'{round(defective * 100 / total_pieces_processed, 2)}%'
            stats["rectified_percentage"] = f'{round(rectified * 100 / defective, 2)}%'
            dhu = defects * 100 / total_pieces_processed
            stats["dhu"] = round(dhu, 2)
    except ZeroDivisionError:
        pass

    return stats