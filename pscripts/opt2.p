program OPT2;
var res;
function afunc(n);
var x;
begin
x := n;
x := n + 1;
afunc := x * 2;
x := n * 10;
end;
begin
res := afunc(2);
write(res)
end.
