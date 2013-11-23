def initialize(context):
    # define portfolio
    # [AIG, CLF, USG, BIDU, MGM Resorts]
    context.sids = [sid(239),
        sid(1595),
        sid(7844),
        sid(27533),
        sid(4831)]
    context.N = len(context.sids)
    # init dict to track whether we invested in a particular sid
    context.invested = {}
    context.risk_percent = 0.01
    context.stops = {}
    context.stop_width = {}
    context.slow_period = 120
    context.fast_period = 30
    context.price_array = {}
    
    for cur_sid in context.sids:
        context.invested[cur_sid] = False
        context.stops[cur_sid] = None
        context.stop_width[cur_sid] = 0
        context.price_array[cur_sid] = []
#
# Figure out the position size we want based on how much we want to lose
#
def get_position_size(cash, cur_price, stop_price, risk_percent):
    ticks_at_risk = abs(stop_price - cur_price)
    cash_to_risk = cash * risk_percent
    return int(cash_to_risk/ticks_at_risk)

# Clear the stops
def wipe_stops(cur_sid, context):
    context.stops[cur_sid] = 0.0
    context.stop_width[cur_sid] = 0.0
    
#    
# A simple Trailing Stop implementation
#
def do_trailing_stop(cur_sid, data, context):
    # We have a long position here:
    if data.portfolio.positions[cur_sid].amount > 0:
        # If the current price is less than or equal to our stop price,
        if data[cur_sid].price <= context.stops[cur_sid]:
            # then close the position
            log.info('Trailing stop closing open Position in SID %i by %i shares' %(cur_sid, data.portfolio.positions[cur_sid].amount))
            order(cur_sid, -data.portfolio.positions[cur_sid].amount)
            context.invested[cur_sid] = False
            wipe_stops(cur_sid, context)
        
        # Prices is greater than our max trailing stop width, so we'll trail it up
        elif data[cur_sid].price - context.stops[cur_sid] > context.stop_width[cur_sid] and context.stop_width[cur_sid] > 0.0:
            context.stops[cur_sid] = data[cur_sid].price - context.stop_width[cur_sid]
            
    # This is a short position
    elif data.portfolio.positions[cur_sid].amount < 0:
        # If the current price is greater than or equal to our stop price,
        if data[cur_sid].price >= context.stops[cur_sid]:
            # then close the position
            log.info('Trailing stop closing open Position in SID %i by %i shares' %(cur_sid, data.portfolio.positions[cur_sid].amount))
            order(cur_sid, -data.portfolio.positions[cur_sid].amount)
            context.invested[cur_sid] = False
            wipe_stops(cur_sid, context)
            
        # Prices is lower than our max trailing stop width, so we'll trail it down
        elif context.stops[cur_sid] - data[cur_sid].price > context.stop_width[cur_sid] and context.stop_width[cur_sid] > 0.0:
            context.stops[cur_sid] = data[cur_sid].price + context.stop_width[cur_sid]

#
# Main Loop:
# Put it all together and make it sing!
#
def handle_data(data, context):
    
    # loop over sids
    for cur_sid in context.sids:
        # skip non-existent sids
        if not data.available(cur_sid):
            continue
        
        # buy if short term moving average crossed long term moving average
        if (data[cur_sid].mavg(30) > data[cur_sid].mavg(120)) and not context.invested[cur_sid]:
            # Calculate volatility for use in the stop loss
            stop_width = float(data[cur_sid].stddev(30))*10
            stop_price = data[cur_sid].price - stop_width
            context.stops[cur_sid] = stop_price
            context.stop_width[cur_sid] = stop_width
            # Calculate the number of shares based on our Risk
            shares = get_position_size(data.portfolio.cash, data[cur_sid].price, stop_price, context.risk_percent)
            # Sometimes if volatility is too high or starting capital too low we get 0 for shares to buy
            if shares != 0:
                log.info('Opening LONG Position in SID %i with %i shares' %(cur_sid, shares))
                order(cur_sid, shares)
                context.invested[cur_sid] = 'long'
            
        # Close position if we were long and the trend changes
        elif (data[cur_sid].mavg(30) < data[cur_sid].mavg(120)) and context.invested[cur_sid] == 'long':
            log.info('Closing open LONG position in SID %i by %i shares' %(cur_sid, data.portfolio.positions[cur_sid].amount))
            # sell the amount we invested
            shares = data.portfolio.positions[cur_sid].amount
            if shares == 0:
                log.error('Open LONG position in SID %i is %i shares!' %(cur_sid, shares))
            order(cur_sid, shares * -1)
            context.invested[cur_sid] = False
        
        # Go short if short term MA is below long term
        elif (data[cur_sid].mavg(30) < data[cur_sid].mavg(120)) and not context.invested[cur_sid]:
            stop_width = float(data[cur_sid].stddev(30)) * 10
            stop_price = data[cur_sid].price + stop_width
            context.stops[cur_sid] = stop_price
            context.stop_width[cur_sid] = stop_width
            shares = get_position_size(data.portfolio.cash, data[cur_sid].price, stop_price, context.risk_percent)
            if shares != 0:
                log.info('Opening SHORT Position in SID %i with %i shares' %(cur_sid, shares))
                order(cur_sid, shares)
                context.invested[cur_sid] = 'short'

        # Close the short if the trend changes
        elif (data[cur_sid].mavg(30) > data[cur_sid].mavg(120)) and context.invested[cur_sid] == 'short':
            log.info('Closing open SHORT position in SID %i by %i shares' %(cur_sid, data.portfolio.positions[cur_sid].amount))
            # sell the amount we invested
            shares = data.portfolio.positions[cur_sid].amount
            if shares == 0:
                log.error('Open SHORT position in SID %i is %i shares!' %(cur_sid, shares))
            order(cur_sid, shares * -1)
            context.invested[cur_sid] = False
        
        # Recalculate stop.
        if context.invested[cur_sid]:
            do_trailing_stop(cur_sid, data, context)