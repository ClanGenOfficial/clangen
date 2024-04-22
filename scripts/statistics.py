def mean(num_list):
    return sum(num_list) / len(num_list)

def median(num_list):
    num_list.sort()
    length = len(num_list)
    if length % 2 == 0:
        return (num_list[length // 2 - 1] + num_list[length // 2]) / 2
    return num_list[length // 2]