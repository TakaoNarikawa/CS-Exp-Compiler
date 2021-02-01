program PL0C;
var n, x, i;
procedure prime;
var m;
begin
   m := x div 2;
   while x <> (x div m) * m do
      m := m - 1;
   if m = 1 then
      write(x)
end;
begin
   read(n);
   for i := 2 to n do
   begin
      x := i;
      prime;
   end
end.