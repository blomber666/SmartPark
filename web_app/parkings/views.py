from django.shortcuts import render
from parkings.map_tools import generate_map
#from users import views as users_views
from parkings.models import Stop, Payment, TbApi, Price
from users.models import User
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, time
from datetime import timedelta



# Create your views here.
def park_1(request, context={}):
    
    if request.user.is_authenticated:
        start_filter = None
        start_date_converted = None
        end_filter = None
        end_date_converted = None
        park_num = 1

        #read free_spaces and total_spaces from file park_1.txt inside media folder
        with open('media/park_1.txt', 'r') as f:
            free_spaces = int(f.readline())
            total_spaces = int(f.readline())

        stop = Stop.objects.filter(user=request.user).last()
        start = stop.start_time if stop and stop.start_time else None
        end = stop.end_time if stop and stop.end_time else None

        #last time is the last time the user was in the parking, if the user is in the parking now, the last time is the start time
        #if the user is not in the parking, the last time is the end time
        #if the user never was in the parking, the last time is Never
        last_time = end if end else start if start else 'Never'
        #convert to only date
        if last_time != 'Never':
            last_time = last_time.date()

        payment = Payment.objects.filter(stop=stop).last() if stop else None
        if payment:
            amount = f'{payment.amount}€'
        elif stop:
            amount = f'{ calculate_amount(start)["amount"] }€'
        else:
            amount = '0€'
        payed = payment

        park_status = str((total_spaces-free_spaces)) + '/' + str(total_spaces)
        park_percent = int(((total_spaces-free_spaces)/total_spaces)*100)

        if request.method == 'POST':

            if 'start_filter' in request.POST and request.POST.get("start_filter")!='':
                start_filter = request.POST.get("start_filter")
                #convert to yyyy-mm-dd
                start_date_converted = datetime.strptime(start_filter, '%m/%d/%Y').date()
                context.update({'start_filter': start_filter})

            if 'end_filter' in request.POST and request.POST.get("end_filter")!='':
                end_filter = request.POST.get("end_filter")
                #convert to yyyy-mm-dd
                end_date_converted = datetime.strptime(end_filter, '%m/%d/%Y')
                end_date_converted = end_date_converted.date()
                context.update({'end_filter': end_filter})
            else:
                end_date_converted = datetime.today().date()

        stops = get_stops(request.user, start_date_converted, end_date_converted, park_num)

        context = {'username': request.userz, 'start': start, 'end': end , 'last_time':last_time, 'amount': amount, 'payed': payed, \
            'free_spaces': free_spaces, 'park_status': park_status, 'park_percent': park_percent, 'total_spaces': total_spaces,\
                'stops': stops}
        return render(request, 'park_1.html', context)
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')

def get_stops(user, start_date, end_date, park_num):
    '''
    Get all stops with the given filters, bu always filter by user
    '''
    #completed_stops_1 filters by start_time that is between start_date and end_date
    #completed_stops_2 filters by end_time that is between start_date and end_date
    #then we combine the two querysets
    assert(user), 'user is required'

    args = {}
    args['user'] = user
    if start_date and end_date:
        args['start_time__range'] = [start_date, end_date+timedelta(days=1)]
    if park_num:
        args['park'] = park_num
    stops_1 = Stop.objects.filter(**args)

    args = {}
    args['user'] = user
    if start_date and end_date:
        args['end_time__range'] = [start_date, end_date+timedelta(days=1)]
    if park_num:
        args['park'] = park_num
    stops_2 = Stop.objects.filter(**args)

    stops = stops_1 | stops_2

    for stop in stops:
        payment = Payment.objects.filter(stop=stop).last()
        if payment:
            stop.amount = f'{payment.amount}€'
        elif stop.start_time:
            stop.amount = f'{ calculate_amount(stop.start_time)["amount"] }€ (not payed)'
        else:
            stop.amount = '0€'
    
    return stops

def pay(request):
    if request.user.is_authenticated and request.method == 'GET':
        stop = Stop.objects.filter(user=request.user).last()
        #check if already payed
        payment = Payment.objects.filter(stop=stop)
        if not payment:
            #calculate the amount in euors, every minute is 1 cent
            amount = calculate_amount(stop.start_time)['amount']
            payment = Payment(stop=stop, payment_time=0, amount=amount)
            payment.save()
        else:
            #already payed
            pass

        return redirect('/park_1')
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')

def get_parkings(request):
    if(request.user.is_authenticated):
        with open('media/park_1.txt', 'r') as f:
            free_spaces = int(f.readline())
            total_spaces = int(f.readline())
        park_status = str((total_spaces-free_spaces)) + '/' + str(total_spaces)
        park_percent = int(((total_spaces-free_spaces)/total_spaces)*100)
        context = {'park_status': park_status, 'park_percent': park_percent}
        return JsonResponse(context)
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return JsonResponse({})
        
def calculate_amount(start, end=timezone.localtime(timezone.now()), default_price=0.01): 

    remaining_times = [(start, end)]
    remaining_times = split_times(remaining_times)
    prices = Price.objects.all()
    amount = 0

    while remaining_times:
        found_day = None
        found_date = None
        found_every_day = None
        start = remaining_times[0][0].replace(tzinfo=None)
        end = remaining_times[0][1].replace(tzinfo=None)
        if start == end:
            remaining_times.pop(0)
            continue
        assert(start < end), 'start must be before end'


        for p in prices:
            if p.day == 'Day':
                pass
            else:
                #check if the price is valid for the given date (p.date must be between start and end)
                if p.date and p.date >= start.date() and p.date <= end.date():
                    #check if the p (p.start_time and p.end_time) interesct with start and end
                    if time_intersect(p.start_time, p.end_time, start.time(), end.time()):
                        found_date = p
                        break
                #check if the price is valid for the given day (p.day must be between start and end, day is in the form "Monday", "Tuesday", ...)
                elif p.day:
                    #get all days between start and end 
                    days = [start] + [start + timedelta(days=x) for x in range((end-start).days + 1)] + [end]
                    days_conv = [d.strftime('%A') for d in days]

                    if p.day != 'Every Day':

                        if 'Every ' in p.day:
                            p.day = p.day.replace('Every ', '')
                        
                        while p.day in days_conv:
                            temp_found_start = datetime.combine(days[days_conv.index(p.day)], p.start_time)
                            temp_found_end = datetime.combine(days[days_conv.index(p.day)], p.end_time)
                            #check intersection
                            if time_intersect(temp_found_start, temp_found_end, start, end):
                                found_day = p
                                found_day_date = days[days_conv.index(p.day)]
                                break
                            else:
                                days.remove(days[days_conv.index(p.day)])
                                days_conv.remove(p.day)

                        
                    elif p.day == 'Every Day':
                        while days_conv:
                            temp_found_start = datetime.combine(days[0], p.start_time)
                            temp_found_end = datetime.combine(days[0], p.end_time)
                            #check intersection
                            if time_intersect(temp_found_start, temp_found_end, start, end):
                                found_every_day = p
                                found_day_date = days[0]
                                break
                            else:
                                days.remove(days[0])
                                days_conv.remove(days_conv[0])

        found = None
        for p in [found_date, found_day, found_every_day]:
            if p:
                found = p
                if p.day :
                    #get the date of the found price, using days and days_conv
                    found_start = datetime.combine(found_day_date, found.start_time)
                    found_end = datetime.combine(found_day_date, found.end_time)
                else:
                    found_start = datetime.combine(found.date, found.start_time)
                    found_end = datetime.combine(found.date, found.end_time)
                break
        
        #calculate the partial price only for the time period that is covered by the price
        if found:
            found_price = float(found.price)
            if found_start <= start and found_end >= end:
                amount += (end - start).total_seconds() / 60 * found_price
                remaining_times.pop(0)

            elif found_start <= start: #and found_end >= start.time():
                amount += (found_end - start).total_seconds() / 60 * found_price
                if found_end < end:
                    remaining_times.append([found_end+timedelta(seconds=1), end])
                remaining_times.pop(0)

            elif found_end >= end: #and found_start <= end.time():
                amount += (end - found_start).total_seconds() / 60 * found_price
                if start < found_start:
                    remaining_times.append([start, found_start-timedelta(seconds=1)])
                remaining_times.pop(0)
              
            elif found_start >= start and found_end <= end:
                assert(time_intersect(found_start, found_end, start, end))
                amount += (found_end - found_start).total_seconds() / 60 * found_price
                if start < found_start:
                    remaining_times.append([start, found_start-timedelta(seconds=1)])
                if found_end < end:
                    remaining_times.append([found_end+timedelta(seconds=1), end])
                remaining_times.pop(0)
            
            assert(1 > 0), 'should not reach here'

        else:
            amount += (end - start).total_seconds() / 60 * default_price
            remaining_times.pop(0)
            
    amount = round(amount, 2)
    #add a zero at the end if the cents are a multiple of 10 or if there are no cents
    # if amount % 0.1 == 0 or amount % 1 == 0:
    #     amount = str(amount) + '0'
    #da fare altrove, qui amount deve essere un numero

    assert amount >= 0, 'amount is negative'
    context = {'amount': amount}
    return context

def time_intersect(start1, end1, start2, end2):
    '''check if the time periods (start1, end1) and (start2, end2) intersect'''
    #4 cases
    if start1 <= start2 and end1 >= end2: # 2 is inside 1
        return True
    elif start1 >= start2 and end1 <= end2: # 1 is inside 2
        return True
    elif start1 <= start2 and end1 >= start2: # 2 starts inside 1
        return True
    elif start1 <= end2 and end1 >= end2: # 2 ends inside 1
        return True
    else: #no intersection
        return False

def split_times(times):
    """times is a list of tuples (start, end) where start and end are datetime objects.
    This function returns a list of tuples (start, end) where start and end are datetime objects.
    Every tuple start and end will have the same day and start < end.
    """
    # time(23, 59, 59)
    result = []
    for t in times:
        start = t[0]
        end = t[1]
        if start.day == end.day:
            result.append(t)
        else:
            if end-start < timedelta(days=1):
                #split the time in two
                result.append([start, datetime.combine(start.date(), time(23, 59, 59))])
                result.append([datetime.combine(end.date(), time(0, 0, 0)), end])
            else:
                #split the time in three
                result.append([start, datetime.combine(start.date(), time(23, 59, 59))])
                #append all the days in between
                i=1
                while start.date() + timedelta(days=i) < end.date():
                    result.append([datetime.combine(start.date() + timedelta(days=i), time(0, 0, 0)), datetime.combine(start.date() + timedelta(days=i), time(23, 59, 59))])
                    i += 1
                result.append([datetime.combine(end.date(), time(0, 0, 0)), end])
                
    #remove duplicates from nested list
    result = [x for x in set(tuple(x) for x in result)]
    #remove the tzinfo
    result = [[x[0].replace(tzinfo=None), x[1].replace(tzinfo=None)] for x in result]
    #sort the list
    result.sort(key=lambda x: x[0])
    #remove if start == end
    result = [x for x in result if x[0] != x[1]]
    return result        
