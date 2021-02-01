program PL1A;
var n, temp;
procedure fact(n);
begin
    if n <= 1 then
        temp:=1
    else
    begin
        fact(n - 1);
        temp := temp * n
    end
end;
begin
    read(n);
    fact(n);
    write(temp)
end.
