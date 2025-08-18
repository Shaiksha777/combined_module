nums = [0,1]

left = 0
right = 1

for _ in range(90):
    nums.append(nums[left]+nums[right])
    left += 1
    right += 1
print(nums[-1])