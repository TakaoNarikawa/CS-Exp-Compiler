program PL3A;
var i, j, n, a[1..100];
procedure initialize(n);
var i; 
begin  
    for i := 1 to n do
        read(a[i])
end;
procedure swap(j);
var temp; 
begin	  
    temp := a[j];
    a[j] := a[j+1];
    a[j+1] := temp
end;
begin
    read(n);
    if n <= 100 then
    begin
        initialize(n);
        i := n;
        while 1 <= i do
        begin
            j:=1;
	        write(a[i]);
            if 6 > 5 then
                write(99);
	        i := i - 1
        end
    end
end.
