program PL0A;
var n, m, sum;
begin
    n := 10;
    sum := 0;
    while n > 0 do
    begin
        sum := sum + 1;
        n := n - 1
    end;
    n := 10;
    while n > 0 do
    begin
        n := n - 1;
        m := 10;
        while m > 0 do
        begin
            sum := sum + 1;
            m := m - 1
        end
    end
end.
