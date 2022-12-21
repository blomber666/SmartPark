import numpy as np

data = np.array([
    [[11, 12, 13], [14, 15, 16], [17, 18, 19]],
    [[21, 22, 13], [24, 25, 26], [27, 28, 29]],
    [[31, 32, 33], [34, 35, 36], [37, 38, 39]],
])
mask = np.array([
    [False, False, True],
    [False, True, False],
    [True, True, False],
])
#stack the mask to match the shape of data
mask2 = np.stack([mask, mask, mask], axis=1)

data[mask] == data[mask2]
output = []
for i in range(len(mask)):
    for j in range(len(mask[i])):
        if mask[i][j] == True:
            output.append(data[i][j])
output = np.array(output)
print(output)