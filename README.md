# コンパイラ作成課題 ソースコード

## 始め方

ply をインストール

```sh
pip install ply
```

PL-X で書かれたプログラムをコンパイル

```sh
python3 parser.py source_file.p
```

## テスト実行

```sh
python3 test.py
```

## 仕様

- to-ex5
  - 四則演算
  - if-else
  - for-loop
  - while-loop
  - 引数なし手続き呼出し
- to-ex6
  - 引数有り手続き呼出し
- to-ex7
  - 関数呼び出し
- to-ex8
  - 配列
- to-ex9
  - FORWARD による手続きと関数の相互参照
- to-ex10
  - 定数伝搬
  - デッドコード削除

## ブランチごとの差分

- [to-ex5 - to-ex6](https://github.com/TakaoNarikawa/CS-Exp-Compiler/compare/to-ex5..to-ex6)

- [to-ex6 - to-ex7](https://github.com/TakaoNarikawa/CS-Exp-Compiler/compare/to-ex6..to-ex7)

- [to-ex7 - to-ex8](https://github.com/TakaoNarikawa/CS-Exp-Compiler/compare/to-ex7..to-ex8)

- [to-ex8 - to-ex9](https://github.com/TakaoNarikawa/CS-Exp-Compiler/compare/to-ex8..to-ex9)

- [to-ex9 - to-ex10](https://github.com/TakaoNarikawa/CS-Exp-Compiler/compare/to-ex9..to-ex10)

## コンパイル結果例

### ex1.p

```pascal
program EX1;
var x, y, z;
begin
   x := 12;
   y := 20;
   z := x + y
end.
```

↓

```llvm
@x = common global i32 0, align 4
@y = common global i32 0, align 4
@z = common global i32 0, align 4
define i32 @main(){
  store i32 12, i32* @x, align 4
  store i32 20, i32* @y, align 4
  %1 = load i32, i32* @x, align 4
  %2 = load i32, i32* @y, align 4
  %3 = add nsw i32 %1, %2
  store i32 %3, i32* @z, align 4
  ret i32 0
}
```

---

### pl0a.p

```pascal
program PL0A;
var n, sum;
begin
    n := 10;
    sum := 0;
    while n > 0 do
    begin
        sum := sum + n;
        n := n - 1
    end
end.
```

↓

```llvm
@n = common global i32 0, align 4
@sum = common global i32 0, align 4
define i32 @main(){
  store i32 10, i32* @n, align 4
  store i32 0, i32* @sum, align 4
  br label %while.init.0
  while.init.0:
  %1 = load i32, i32* @n, align 4
  %2 = icmp sgt i32 %1, 0
  br i1 %2, label %while.body.0, label %while.end.0
  while.body.0:
  %3 = load i32, i32* @sum, align 4
  %4 = load i32, i32* @n, align 4
  %5 = add nsw i32 %3, %4
  store i32 %5, i32* @sum, align 4
  %6 = load i32, i32* @n, align 4
  %7 = sub nsw i32 %6, 1
  store i32 %7, i32* @n, align 4
  br label %while.init.0
  while.end.0:
  ret i32 0
}
```

---

### ex4.p

```pascal
program EX4;
var x;
begin
   x := 2 + 4 * 5 - 7;
end.
```

↓

```llvm
@x = common global i32 0, align 4
define i32 @main(){
  %1 = mul nsw i32 4, 5
  %2 = add nsw i32 2, %1
  %3 = sub nsw i32 %2, 7
  store i32 %3, i32* @x, align 4
  ret i32 0
}
```

---

### ex4.p（定数伝搬）

```pascal
program EX4;
var x;
begin
   x := 2 + 4 * 5 - 7;
end.
```

↓

```llvm
@x = common global i32 0, align 4
define i32 @main(){
  store i32 15, i32* @x, align 4
  ret i32 0
}
```

---

### opt2.p

```pascal
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

```

↓

```llvm
@res = common global i32 0, align 4
@.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
declare dso_local i32 @printf(i8*, ...) #1
define i32 @afunc(i32){
  %2 = alloca i32, align 4
  store i32 %0, i32* %2, align 4
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = load i32, i32* %2, align 4
  store i32 %5, i32* %3, align 4
  %6 = load i32, i32* %2, align 4
  %7 = add nsw i32 %6, 1
  store i32 %7, i32* %3, align 4
  %8 = load i32, i32* %3, align 4
  %9 = mul nsw i32 %8, 2
  store i32 %9, i32* %4, align 4
  %10 = load i32, i32* %2, align 4
  %11 = mul nsw i32 %10, 10
  store i32 %11, i32* %3, align 4
  %12 = load i32, i32* %4, align 4
  ret i32 %12
}
define i32 @main(){
  %1 = call i32 @afunc(i32 2)
  store i32 %1, i32* @res, align 4
  %2 = load i32, i32* @res, align 4
  %3 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %2)
  ret i32 0
}
```

---

### opt2.p（デッドコード削除）

```pascal
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

```

↓

```llvm
@res = common global i32 0, align 4
@.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
declare dso_local i32 @printf(i8*, ...) #1
define i32 @afunc(i32){
  %2 = alloca i32, align 4
  store i32 %0, i32* %2, align 4
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = load i32, i32* %2, align 4
  %6 = add nsw i32 %5, 1
  store i32 %6, i32* %3, align 4
  %7 = load i32, i32* %3, align 4
  %8 = mul nsw i32 %7, 2
  store i32 %8, i32* %4, align 4
  %9 = load i32, i32* %4, align 4
  ret i32 %9
}
define i32 @main(){
  %1 = call i32 @afunc(i32 2)
  store i32 %1, i32* @res, align 4
  %2 = load i32, i32* @res, align 4
  %3 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %2)
  ret i32 0
}
```
