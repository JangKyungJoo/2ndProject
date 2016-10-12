#include <stdio.h>
#include <string.h>

long long N, M;
int arr[10001];
int remain[10001];
int main()
{
	scanf("%lld %lld", &N, &M);
	for(int i=1; i<=M; i++)
		scanf("%d", &arr[i]);
	
	long long left = 0, right = 2000000000LL * 1000000LL;
	
	if(M >= N)
	{
		printf("%lld", N);
		return 0;
	}
	
	while(left <= right)
	{
		long long mid = (left+right)/2;
		long long sum = M;
		int cnt = 0;
		for(int i=1; i<=M; i++)
		{
			sum += mid/arr[i];
			if(mid%arr[i] == 0)
			{
				remain[++cnt] = i;
			}
		}
		
		if(sum >= N)
		{
			if(sum - cnt < N)
			{
				printf("%d", remain[cnt - (sum-N)]);
				return 0;
			}
			right = mid - 1;
		}
		else
		{
			left = mid + 1;
		}
		memset(remain, 0, sizeof(remain));
	}
}