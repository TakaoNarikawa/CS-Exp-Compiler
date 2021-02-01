program OPT2;
function afunc(n);
var x;
begin
x := n;
x := n + 1;
afunc := x * 2;
x := n * 10;
end;
begin
afunc(2)
end.
