program PL4A;
var sum, n;
forward procedure proc2;
procedure proc1;
begin
   sum := sum + n;
   proc2
end;
procedure proc2;
begin
   n := n - 1;
   if n > 0 then
      proc1
   else
      write(sum);
end;
begin
   sum :=0;
   read(n);
   proc1
end.
