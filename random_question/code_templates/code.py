
nums =  [3, 4, 5]
left = 0
right = len(nums)-1
res = []
for i in range(len(nums)):
    left = 0
    right = len(nums)-1

    if len(res) > 0:
        break
    while left < right :

        total = nums[left] + nums[right]

        if nums[i] == total:
            res.append(nums[i])
            break
        elif nums[i] > total:
            left += 1
        else:
            right -= 1

print(res)