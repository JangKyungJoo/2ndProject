#include <stdio.h>

int visited[101][101];
char mat[101][101];
int n;
int common_cnt, babo_cnt;

void search(int y, int x, char c)
{
	if(visited[y][x] || (c != mat[y][x])) return;
	visited[y][x] = 1;
	
	if(y > 0)
		search(y-1, x, mat[y][x]);
	if(x < n-1)
		search(y, x+1, mat[y][x]);
	if(y < n-1)
		search(y+1, x, mat[y][x]);
	if(x > 0)
		search(y, x-1, mat[y][x]);
}
int main()
{
	scanf("%d", &n);
	for(int i=0; i<n; i++)
		scanf("%s", mat[i]);
	
	for(int i=0; i<n; i++)
		for(int j=0; j<n; j++)
			if(!visited[i][j])
			{
				search(i, j, mat[i][j]);
				common_cnt++;
			}
	for(int i=0; i<n; i++)
		for(int j=0; j<n; j++)
			mat[i][j] = mat[i][j] == 'G' ? 'R' : mat[i][j];
	
	memset(visited, 0, sizeof(visited));
	for(int i=0; i<n; i++)
		for(int j=0; j<n; j++)
			if(!visited[i][j])
			{
				search(i, j, mat[i][j]);
				babo_cnt++;
			}
	printf("%d %d", common_cnt, babo_cnt);
}