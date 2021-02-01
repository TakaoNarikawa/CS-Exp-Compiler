program EXTP;
var n;
forward function fib(n);
forward function fibS(n);
function fibS(n);
begin
 if n=0 then fibS:=1
 else fibS := fib(n-1) + fibS(n-1);
end;
function fib(n);
begin
 if n=0 then fib:=0
 else fib:=fibS(n-1);
end;
begin
 read(n);
 if n<=10 then write(fib(n))
end.
