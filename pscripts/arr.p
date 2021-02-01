program PL0C;
var x[1..20];
procedure A;
var y[3..10];
begin
  x[1] := 3;
  y[3] := 0;
  y[5] := 6;
  write(x[1]);
  write(x[2]);
  write(y[3]);
  write(y[5])
end;
begin
  A
end.