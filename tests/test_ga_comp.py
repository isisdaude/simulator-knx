
main1 = 3
mid1 = 3
sub1 = 3

main2 = 3
mid2 = 2
sub2 = 2

comp = (sub1 + (mid1<<8) + (main1<<11)) < (sub2 + (mid2<<8) + (main2<<11))

print("ga1 < ga2 :", comp )
