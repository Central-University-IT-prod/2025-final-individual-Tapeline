def unzip(iterable) -> tuple[list, ...]:
    iterables = [[] for _ in range(len(iterable[0]))]
    for elem in iterable:
        for i, sub_elem in enumerate(elem):
            iterables[i].append(sub_elem)
    return tuple(iterables)
