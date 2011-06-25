def reduce_burndown_data( data ):
    """Takes a list of datapoints for a burnup chart and if there are more than 30, removes any redundant points.
       Redundant is when a point's two neighbors are equal to itself so it would just be a marker on a straight line.
       (I guess points along a straight sloped line could be considered redundant, but we don't remove those)
       The middle 15 is considered redundant here: [5,6,10,10,15,15,15,20]
       The middle 4 threes are considered redundant here: [1,2,3,3,3,3,3,3,5]
    """
    if len(data) < 30:
        return data

    subset = data[1:-1] # Subset of data that never includes first/last
    remove = []
    for idx,item in enumerate( subset ):
                # idx = index before this item in data
                # idx+1 = this item in data
                # idx+2 = next item in data
        last_val = data[ idx ][1]
        next_val = data[ idx+2 ][1]

        if item[1]==last_val and item[1]==next_val:
            # don't need this item!
            remove.append(idx+1)
            # logger.debug("Can remove %d" % (idx+1))

    remove.reverse()
    for remove_index in remove:
        del data[remove_index:(remove_index+1)]
    return data
