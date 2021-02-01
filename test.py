# -*- coding: utf-8 -*-
import subprocess
import sys
import textwrap
import unittest

from symtab import Symbol


class TestCompiler(unittest.TestCase):

    def execute(self, filename) -> str:
        subprocess.call([sys.executable, 'parser.py', filename], stdout=subprocess.PIPE)
        with open("result.ll") as f:
            return ''.join(f.readlines())

    def test_symbol(self):
        sym1 = Symbol("a", 1, 2)
        sym2 = Symbol("a", 1, 2)

        self.assertEqual(sym1, sym2)


    def test_ex1(self):
        actual = self.execute("pscripts/ex1.p")
        expected = textwrap.dedent(r'''
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
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_ex4(self):
        actual = self.execute("pscripts/ex4.p")
        expected = textwrap.dedent(r'''
            @x = common global i32 0, align 4
            define i32 @main(){
              %1 = mul nsw i32 4, 5
              %2 = add nsw i32 2, %1
              %3 = sub nsw i32 %2, 7
              store i32 %3, i32* @x, align 4
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_global_local(self):
        actual = self.execute("pscripts/global-local.p")
        expected = textwrap.dedent(r'''
            @x = common global i32 0, align 4
            @y = common global i32 0, align 4
            @z = common global i32 0, align 4
            define i32 @A(){
              %1 = alloca i32, align 4
              store i32 1, i32* %1, align 4
              %2 = load i32, i32* %1, align 4
              %3 = add nsw i32 %2, 1
              store i32 %3, i32* %1, align 4
              ret i32 0
            }
            define i32 @B(){
              %1 = alloca i32, align 4
              store i32 2, i32* %1, align 4
              store i32 5, i32* @x, align 4
              ret i32 0
            }
            define i32 @main(){
              store i32 3, i32* @z, align 4
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_if(self):
        actual = self.execute("pscripts/if.p")
        expected = textwrap.dedent(r'''
            @x = common global i32 0, align 4
            @a = common global i32 0, align 4
            @b = common global i32 0, align 4
            define i32 @main(){
              %1 = load i32, i32* @a, align 4
              %2 = load i32, i32* @b, align 4
              %3 = icmp eq i32 %1, %2
              br i1 %3, label %if.true.0, label %if.else.0
              if.true.0:
              store i32 5, i32* @x, align 4
              br label %if.end.0
              if.else.0:
              store i32 3, i32* @x, align 4
              br label %if.end.0
              if.end.0:
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())
    def test_ifif(self):
        actual = self.execute("pscripts/ifif.p")
        expected = textwrap.dedent(r'''
            @a = common global i32 0, align 4
            @b = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            define i32 @main(){
              %1 = load i32, i32* @a, align 4
              %2 = load i32, i32* @b, align 4
              %3 = icmp eq i32 %1, %2
              br i1 %3, label %if.true.0, label %if.else.0
              if.true.0:
              %4 = load i32, i32* @a, align 4
              %5 = load i32, i32* @b, align 4
              %6 = icmp eq i32 %4, %5
              br i1 %6, label %if.true.1, label %if.else.1
              if.true.1:
              %7 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 1)
              br label %if.end.1
              if.else.1:
              %8 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 2)
              br label %if.end.1
              if.end.1:
              br label %if.end.0
              if.else.0:
              %9 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 3)
              br label %if.end.0
              if.end.0:
              %10 = load i32, i32* @a, align 4
              %11 = load i32, i32* @b, align 4
              %12 = icmp ne i32 %10, %11
              br i1 %12, label %if.true.2, label %if.else.2
              if.true.2:
              %13 = load i32, i32* @a, align 4
              %14 = load i32, i32* @b, align 4
              %15 = icmp eq i32 %13, %14
              br i1 %15, label %if.true.3, label %if.else.3
              if.true.3:
              %16 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 1)
              br label %if.end.3
              if.else.3:
              %17 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 2)
              br label %if.end.3
              if.end.3:
              br label %if.end.2
              if.else.2:
              %18 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 3)
              br label %if.end.2
              if.end.2:
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_for(self):
        actual = self.execute("pscripts/for.p")
        expected = textwrap.dedent(r'''
            @n = common global i32 0, align 4
            @m = common global i32 0, align 4
            @sum = common global i32 0, align 4
            define i32 @main(){
              store i32 2, i32* @n, align 4
              br label %for.body.0
              for.condition.0:
              %1 = load i32, i32* @n, align 4
              %2 = add nsw i32 %1, 1
              store i32 %2, i32* @n, align 4
              %3 = icmp sle i32 %2, 10
              br i1 %3, label %for.body.0, label %for.end.0
              for.body.0:
              %4 = load i32, i32* @sum, align 4
              %5 = add nsw i32 %4, 1
              store i32 %5, i32* @sum, align 4
              br label %for.condition.0
              for.end.0:
              store i32 2, i32* @n, align 4
              br label %for.body.1
              for.condition.1:
              %6 = load i32, i32* @n, align 4
              %7 = add nsw i32 %6, 1
              store i32 %7, i32* @n, align 4
              %8 = icmp sle i32 %7, 10
              br i1 %8, label %for.body.1, label %for.end.1
              for.body.1:
              store i32 2, i32* @m, align 4
              br label %for.body.2
              for.condition.2:
              %9 = load i32, i32* @m, align 4
              %10 = add nsw i32 %9, 1
              store i32 %10, i32* @m, align 4
              %11 = icmp sle i32 %10, 10
              br i1 %11, label %for.body.2, label %for.end.2
              for.body.2:
              %12 = load i32, i32* @sum, align 4
              %13 = add nsw i32 %12, 1
              store i32 %13, i32* @sum, align 4
              br label %for.condition.2
              for.end.2:
              br label %for.condition.1
              for.end.1:
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_for_local_var(self):
        actual = self.execute("pscripts/for-local-var.p")
        expected = textwrap.dedent(r'''
            define i32 @A(){
              %1 = alloca i32, align 4
              %2 = alloca i32, align 4
              store i32 10, i32* %2, align 4
              store i32 2, i32* %1, align 4
              br label %for.body.0
              for.condition.0:
              %3 = load i32, i32* %1, align 4
              %4 = add nsw i32 %3, 1
              store i32 %4, i32* %1, align 4
              %5 = icmp sle i32 %4, 100
              br i1 %5, label %for.body.0, label %for.end.0
              for.body.0:
              %6 = load i32, i32* %2, align 4
              %7 = add nsw i32 %6, 1
              store i32 %7, i32* %2, align 4
              br label %for.condition.0
              for.end.0:
              ret i32 0
            }
            define i32 @main(){
              %1 = call i32 @A()
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_while(self):
        actual = self.execute("pscripts/whilewhile.p")
        expected = textwrap.dedent(r'''
            @n = common global i32 0, align 4
            @m = common global i32 0, align 4
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
              %4 = add nsw i32 %3, 1
              store i32 %4, i32* @sum, align 4
              %5 = load i32, i32* @n, align 4
              %6 = sub nsw i32 %5, 1
              store i32 %6, i32* @n, align 4
              br label %while.init.0
              while.end.0:
              store i32 10, i32* @n, align 4
              br label %while.init.1
              while.init.1:
              %7 = load i32, i32* @n, align 4
              %8 = icmp sgt i32 %7, 0
              br i1 %8, label %while.body.1, label %while.end.1
              while.body.1:
              %9 = load i32, i32* @n, align 4
              %10 = sub nsw i32 %9, 1
              store i32 %10, i32* @n, align 4
              store i32 10, i32* @m, align 4
              br label %while.init.2
              while.init.2:
              %11 = load i32, i32* @m, align 4
              %12 = icmp sgt i32 %11, 0
              br i1 %12, label %while.body.2, label %while.end.2
              while.body.2:
              %13 = load i32, i32* @sum, align 4
              %14 = add nsw i32 %13, 1
              store i32 %14, i32* @sum, align 4
              %15 = load i32, i32* @m, align 4
              %16 = sub nsw i32 %15, 1
              store i32 %16, i32* @m, align 4
              br label %while.init.2
              while.end.2:
              br label %while.init.1
              while.end.1:
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl0a(self):
        actual = self.execute("pscripts/pl0a.p")
        expected = textwrap.dedent(r'''
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
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl0b(self):
        actual = self.execute("pscripts/pl0b.p")
        expected = textwrap.dedent(r'''
            @n = common global i32 0, align 4
            @x = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @prime(){
              %1 = alloca i32, align 4
              %2 = load i32, i32* @x, align 4
              %3 = sdiv i32 %2, 2
              store i32 %3, i32* %1, align 4
              br label %while.init.0
              while.init.0:
              %4 = load i32, i32* @x, align 4
              %5 = load i32, i32* @x, align 4
              %6 = load i32, i32* %1, align 4
              %7 = sdiv i32 %5, %6
              %8 = load i32, i32* %1, align 4
              %9 = mul nsw i32 %7, %8
              %10 = icmp ne i32 %4, %9
              br i1 %10, label %while.body.0, label %while.end.0
              while.body.0:
              %11 = load i32, i32* %1, align 4
              %12 = sub nsw i32 %11, 1
              store i32 %12, i32* %1, align 4
              br label %while.init.0
              while.end.0:
              %13 = load i32, i32* %1, align 4
              %14 = icmp eq i32 %13, 1
              br i1 %14, label %if.true.1, label %if.else.1
              if.true.1:
              %15 = load i32, i32* @x, align 4
              %16 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %15)
              br label %if.end.1
              if.else.1:
              br label %if.end.1
              if.end.1:
              ret i32 0
            }
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @n, align 4
              br label %while.init.2
              while.init.2:
              %4 = load i32, i32* @n, align 4
              %5 = icmp slt i32 1, %4
              br i1 %5, label %while.body.2, label %while.end.2
              while.body.2:
              %6 = load i32, i32* @n, align 4
              store i32 %6, i32* @x, align 4
              %7 = call i32 @prime()
              %8 = load i32, i32* @n, align 4
              %9 = sub nsw i32 %8, 1
              store i32 %9, i32* @n, align 4
              br label %while.init.2
              while.end.2:
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl0c(self):
        actual = self.execute("pscripts/pl0c.p")
        expected = textwrap.dedent(r'''
            @n = common global i32 0, align 4
            @x = common global i32 0, align 4
            @i = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @prime(){
              %1 = alloca i32, align 4
              %2 = load i32, i32* @x, align 4
              %3 = sdiv i32 %2, 2
              store i32 %3, i32* %1, align 4
              br label %while.init.0
              while.init.0:
              %4 = load i32, i32* @x, align 4
              %5 = load i32, i32* @x, align 4
              %6 = load i32, i32* %1, align 4
              %7 = sdiv i32 %5, %6
              %8 = load i32, i32* %1, align 4
              %9 = mul nsw i32 %7, %8
              %10 = icmp ne i32 %4, %9
              br i1 %10, label %while.body.0, label %while.end.0
              while.body.0:
              %11 = load i32, i32* %1, align 4
              %12 = sub nsw i32 %11, 1
              store i32 %12, i32* %1, align 4
              br label %while.init.0
              while.end.0:
              %13 = load i32, i32* %1, align 4
              %14 = icmp eq i32 %13, 1
              br i1 %14, label %if.true.1, label %if.else.1
              if.true.1:
              %15 = load i32, i32* @x, align 4
              %16 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %15)
              br label %if.end.1
              if.else.1:
              br label %if.end.1
              if.end.1:
              ret i32 0
            }
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @n, align 4
              %4 = load i32, i32* @n, align 4
              store i32 2, i32* @i, align 4
              br label %for.body.2
              for.condition.2:
              %5 = load i32, i32* @i, align 4
              %6 = add nsw i32 %5, 1
              store i32 %6, i32* @i, align 4
              %7 = icmp sle i32 %6, %4
              br i1 %7, label %for.body.2, label %for.end.2
              for.body.2:
              %8 = load i32, i32* @i, align 4
              store i32 %8, i32* @x, align 4
              %9 = call i32 @prime()
              br label %for.condition.2
              for.end.2:
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl0d(self):
        actual = self.execute("pscripts/pl0d.p")
        expected = textwrap.dedent(r'''
            @n = common global i32 0, align 4
            @temp = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @fact(){
              %1 = alloca i32, align 4
              %2 = load i32, i32* @n, align 4
              %3 = icmp sle i32 %2, 1
              br i1 %3, label %if.true.0, label %if.else.0
              if.true.0:
              store i32 1, i32* @temp, align 4
              br label %if.end.0
              if.else.0:
              %4 = load i32, i32* @n, align 4
              store i32 %4, i32* %1, align 4
              %5 = load i32, i32* @n, align 4
              %6 = sub nsw i32 %5, 1
              store i32 %6, i32* @n, align 4
              %7 = call i32 @fact()
              %8 = load i32, i32* @temp, align 4
              %9 = load i32, i32* %1, align 4
              %10 = mul nsw i32 %8, %9
              store i32 %10, i32* @temp, align 4
              br label %if.end.0
              if.end.0:
              ret i32 0
            }
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @n, align 4
              %4 = call i32 @fact()
              %5 = load i32, i32* @temp, align 4
              %6 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %5)
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl1a(self):
        actual = self.execute("pscripts/pl1a.p")
        expected = textwrap.dedent(r'''
            @n = common global i32 0, align 4
            @temp = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @fact(i32){
              %2 = alloca i32, align 4
              store i32 %0, i32* %2, align 4
              %3 = load i32, i32* %2, align 4
              %4 = icmp sle i32 %3, 1
              br i1 %4, label %if.true.0, label %if.else.0
              if.true.0:
              store i32 1, i32* @temp, align 4
              br label %if.end.0
              if.else.0:
              %5 = load i32, i32* %2, align 4
              %6 = sub nsw i32 %5, 1
              %7 = call i32 @fact(i32 %6)
              %8 = load i32, i32* @temp, align 4
              %9 = load i32, i32* %2, align 4
              %10 = mul nsw i32 %8, %9
              store i32 %10, i32* @temp, align 4
              br label %if.end.0
              if.end.0:
              ret i32 0
            }
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @n, align 4
              %4 = load i32, i32* @n, align 4
              %5 = call i32 @fact(i32 %4)
              %6 = load i32, i32* @temp, align 4
              %7 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %6)
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl2a(self):
        actual = self.execute("pscripts/pl2a.p")
        expected = textwrap.dedent(r'''
            @n = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @fact(i32){
              %2 = alloca i32, align 4
              store i32 %0, i32* %2, align 4
              %3 = alloca i32, align 4
              %4 = alloca i32, align 4
              %5 = alloca i32, align 4
              %6 = alloca i32, align 4
              %7 = load i32, i32* %2, align 4
              %8 = icmp sle i32 %7, 0
              br i1 %8, label %if.true.0, label %if.else.0
              if.true.0:
              store i32 1, i32* %6, align 4
              br label %if.end.0
              if.else.0:
              %9 = load i32, i32* %2, align 4
              %10 = sub nsw i32 %9, 1
              %11 = call i32 @fact(i32 %10)
              %12 = load i32, i32* %2, align 4
              %13 = mul nsw i32 %11, %12
              store i32 %13, i32* %6, align 4
              br label %if.end.0
              if.end.0:
              %14 = load i32, i32* %6, align 4
              ret i32 %14
            }
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @n, align 4
              %4 = load i32, i32* @n, align 4
              %5 = call i32 @fact(i32 %4)
              %6 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %5)
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl2b(self):
        actual = self.execute("pscripts/pl2b.p")
        expected = textwrap.dedent(r'''
            @m = common global i32 0, align 4
            @n = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @power(i32, i32){
              %3 = alloca i32, align 4
              store i32 %0, i32* %3, align 4
              %4 = alloca i32, align 4
              store i32 %1, i32* %4, align 4
              %5 = alloca i32, align 4
              %6 = load i32, i32* %4, align 4
              %7 = icmp sle i32 %6, 0
              br i1 %7, label %if.true.0, label %if.else.0
              if.true.0:
              store i32 1, i32* %5, align 4
              br label %if.end.0
              if.else.0:
              %8 = load i32, i32* %3, align 4
              %9 = load i32, i32* %4, align 4
              %10 = sub nsw i32 %9, 1
              %11 = call i32 @power(i32 %8, i32 %10)
              %12 = load i32, i32* %3, align 4
              %13 = mul nsw i32 %11, %12
              store i32 %13, i32* %5, align 4
              br label %if.end.0
              if.end.0:
              %14 = load i32, i32* %5, align 4
              ret i32 %14
            }
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @m, align 4
              %4 = alloca i32, align 4
              %5 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %4)
              %6 = load i32, i32* %4, align 4
              store i32 %6, i32* @n, align 4
              %7 = load i32, i32* @m, align 4
              %8 = load i32, i32* @n, align 4
              %9 = call i32 @power(i32 %7, i32 %8)
              %10 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %9)
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl3a(self):
        actual = self.execute("pscripts/pl3a.p")
        expected = textwrap.dedent(r'''
            @i = common global i32 0, align 4
            @j = common global i32 0, align 4
            @n = common global i32 0, align 4
            @a = common dso_local global [100 x i32] zeroinitializer, align 16
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @initialize(i32){
              %2 = alloca i32, align 4
              store i32 %0, i32* %2, align 4
              %3 = alloca i32, align 4
              %4 = load i32, i32* %2, align 4
              store i32 1, i32* %3, align 4
              br label %for.body.0
              for.condition.0:
              %5 = load i32, i32* %3, align 4
              %6 = add nsw i32 %5, 1
              store i32 %6, i32* %3, align 4
              %7 = icmp sle i32 %6, %4
              br i1 %7, label %for.body.0, label %for.end.0
              for.body.0:
              %8 = load i32, i32* %3, align 4
              %9 = sub nsw i32 %8, 1
              %10 = getelementptr inbounds [100 x i32], [100 x i32]* @a, i32 0, i32 %9
              %11 = alloca i32, align 4
              %12 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %11)
              %13 = load i32, i32* %11, align 4
              store i32 %13, i32* %10, align 4
              br label %for.condition.0
              for.end.0:
              ret i32 0
            }
            define i32 @swap(i32){
              %2 = alloca i32, align 4
              store i32 %0, i32* %2, align 4
              %3 = alloca i32, align 4
              %4 = load i32, i32* %2, align 4
              %5 = sub nsw i32 %4, 1
              %6 = getelementptr inbounds [100 x i32], [100 x i32]* @a, i32 0, i32 %5
              %7 = load i32, i32* %6, align 4
              store i32 %7, i32* %3, align 4
              %8 = load i32, i32* %2, align 4
              %9 = load i32, i32* %2, align 4
              %10 = add nsw i32 %9, 1
              %11 = sub nsw i32 %10, 1
              %12 = getelementptr inbounds [100 x i32], [100 x i32]* @a, i32 0, i32 %11
              %13 = load i32, i32* %12, align 4
              %14 = sub nsw i32 %8, 1
              %15 = getelementptr inbounds [100 x i32], [100 x i32]* @a, i32 0, i32 %14
              store i32 %13, i32* %15, align 4
              %16 = load i32, i32* %2, align 4
              %17 = add nsw i32 %16, 1
              %18 = load i32, i32* %3, align 4
              %19 = sub nsw i32 %17, 1
              %20 = getelementptr inbounds [100 x i32], [100 x i32]* @a, i32 0, i32 %19
              store i32 %18, i32* %20, align 4
              ret i32 0
            }
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @n, align 4
              %4 = load i32, i32* @n, align 4
              %5 = icmp sle i32 %4, 100
              br i1 %5, label %if.true.1, label %if.else.1
              if.true.1:
              %6 = load i32, i32* @n, align 4
              %7 = call i32 @initialize(i32 %6)
              %8 = load i32, i32* @n, align 4
              store i32 %8, i32* @i, align 4
              br label %while.init.2
              while.init.2:
              %9 = load i32, i32* @i, align 4
              %10 = icmp sle i32 1, %9
              br i1 %10, label %while.body.2, label %while.end.2
              while.body.2:
              store i32 1, i32* @j, align 4
              br label %while.init.3
              while.init.3:
              %11 = load i32, i32* @j, align 4
              %12 = load i32, i32* @i, align 4
              %13 = icmp slt i32 %11, %12
              br i1 %13, label %while.body.3, label %while.end.3
              while.body.3:
              %14 = load i32, i32* @j, align 4
              %15 = sub nsw i32 %14, 1
              %16 = getelementptr inbounds [100 x i32], [100 x i32]* @a, i32 0, i32 %15
              %17 = load i32, i32* %16, align 4
              %18 = load i32, i32* @j, align 4
              %19 = add nsw i32 %18, 1
              %20 = sub nsw i32 %19, 1
              %21 = getelementptr inbounds [100 x i32], [100 x i32]* @a, i32 0, i32 %20
              %22 = load i32, i32* %21, align 4
              %23 = icmp sgt i32 %17, %22
              br i1 %23, label %if.true.4, label %if.else.4
              if.true.4:
              %24 = load i32, i32* @j, align 4
              %25 = call i32 @swap(i32 %24)
              br label %if.end.4
              if.else.4:
              br label %if.end.4
              if.end.4:
              %26 = load i32, i32* @j, align 4
              %27 = add nsw i32 %26, 1
              store i32 %27, i32* @j, align 4
              br label %while.init.3
              while.end.3:
              %28 = load i32, i32* @i, align 4
              %29 = sub nsw i32 %28, 1
              %30 = getelementptr inbounds [100 x i32], [100 x i32]* @a, i32 0, i32 %29
              %31 = load i32, i32* %30, align 4
              %32 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %31)
              %33 = load i32, i32* @i, align 4
              %34 = sub nsw i32 %33, 1
              store i32 %34, i32* @i, align 4
              br label %while.init.2
              while.end.2:
              br label %if.end.1
              if.else.1:
              br label %if.end.1
              if.end.1:
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl3b(self):
        actual = self.execute("pscripts/pl3b.p")
        expected = textwrap.dedent(r'''
            @a = common dso_local global [99 x i32] zeroinitializer, align 16
            @i = common global i32 0, align 4
            @n = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @initialize(){
              %1 = alloca i32, align 4
              store i32 2, i32* %1, align 4
              br label %for.body.0
              for.condition.0:
              %2 = load i32, i32* %1, align 4
              %3 = add nsw i32 %2, 1
              store i32 %3, i32* %1, align 4
              %4 = icmp sle i32 %3, 100
              br i1 %4, label %for.body.0, label %for.end.0
              for.body.0:
              %5 = load i32, i32* %1, align 4
              %6 = sub nsw i32 %5, 2
              %7 = getelementptr inbounds [99 x i32], [99 x i32]* @a, i32 0, i32 %6
              store i32 0, i32* %7, align 4
              br label %for.condition.0
              for.end.0:
              ret i32 0
            }
            define i32 @check(i32){
              %2 = alloca i32, align 4
              store i32 %0, i32* %2, align 4
              %3 = alloca i32, align 4
              %4 = load i32, i32* %2, align 4
              store i32 %4, i32* %3, align 4
              br label %while.init.1
              while.init.1:
              %5 = load i32, i32* %3, align 4
              %6 = icmp sle i32 %5, 100
              br i1 %6, label %while.body.1, label %while.end.1
              while.body.1:
              %7 = load i32, i32* %3, align 4
              %8 = sub nsw i32 %7, 2
              %9 = getelementptr inbounds [99 x i32], [99 x i32]* @a, i32 0, i32 %8
              store i32 1, i32* %9, align 4
              %10 = load i32, i32* %3, align 4
              %11 = load i32, i32* %2, align 4
              %12 = add nsw i32 %10, %11
              store i32 %12, i32* %3, align 4
              br label %while.init.1
              while.end.1:
              ret i32 0
            }
            define i32 @main(){
              %1 = call i32 @initialize()
              %2 = alloca i32, align 4
              %3 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %2)
              %4 = load i32, i32* %2, align 4
              store i32 %4, i32* @n, align 4
              %5 = load i32, i32* @n, align 4
              %6 = icmp sle i32 %5, 100
              br i1 %6, label %if.true.2, label %if.else.2
              if.true.2:
              %7 = load i32, i32* @n, align 4
              store i32 2, i32* @i, align 4
              br label %for.body.3
              for.condition.3:
              %8 = load i32, i32* @i, align 4
              %9 = add nsw i32 %8, 1
              store i32 %9, i32* @i, align 4
              %10 = icmp sle i32 %9, %7
              br i1 %10, label %for.body.3, label %for.end.3
              for.body.3:
              %11 = load i32, i32* @i, align 4
              %12 = sub nsw i32 %11, 2
              %13 = getelementptr inbounds [99 x i32], [99 x i32]* @a, i32 0, i32 %12
              %14 = load i32, i32* %13, align 4
              %15 = icmp eq i32 %14, 0
              br i1 %15, label %if.true.4, label %if.else.4
              if.true.4:
              %16 = load i32, i32* @i, align 4
              %17 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %16)
              %18 = load i32, i32* @i, align 4
              %19 = call i32 @check(i32 %18)
              br label %if.end.4
              if.else.4:
              br label %if.end.4
              if.end.4:
              br label %for.condition.3
              for.end.3:
              br label %if.end.2
              if.else.2:
              br label %if.end.2
              if.end.2:
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl4a(self):
        actual = self.execute("pscripts/pl4a.p")
        expected = textwrap.dedent(r'''
            @sum = common global i32 0, align 4
            @n = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @proc1(){
              %1 = load i32, i32* @sum, align 4
              %2 = load i32, i32* @n, align 4
              %3 = add nsw i32 %1, %2
              store i32 %3, i32* @sum, align 4
              %4 = call i32 @proc2()
              ret i32 0
            }
            define i32 @proc2(){
              %1 = load i32, i32* @n, align 4
              %2 = sub nsw i32 %1, 1
              store i32 %2, i32* @n, align 4
              %3 = load i32, i32* @n, align 4
              %4 = icmp sgt i32 %3, 0
              br i1 %4, label %if.true.0, label %if.else.0
              if.true.0:
              %5 = call i32 @proc1()
              br label %if.end.0
              if.else.0:
              %6 = load i32, i32* @sum, align 4
              %7 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %6)
              br label %if.end.0
              if.end.0:
              ret i32 0
            }
            define i32 @main(){
              store i32 0, i32* @sum, align 4
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @n, align 4
              %4 = call i32 @proc1()
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_pl4_test(self):
        actual = self.execute("pscripts/pl4-test.p")
        expected = textwrap.dedent(r'''
            @n = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @fibS(i32){
              %2 = alloca i32, align 4
              store i32 %0, i32* %2, align 4
              %3 = alloca i32, align 4
              %4 = load i32, i32* %2, align 4
              %5 = icmp eq i32 %4, 0
              br i1 %5, label %if.true.0, label %if.else.0
              if.true.0:
              store i32 1, i32* %3, align 4
              br label %if.end.0
              if.else.0:
              %6 = load i32, i32* %2, align 4
              %7 = sub nsw i32 %6, 1
              %8 = call i32 @fib(i32 %7)
              %9 = load i32, i32* %2, align 4
              %10 = sub nsw i32 %9, 1
              %11 = call i32 @fibS(i32 %10)
              %12 = add nsw i32 %8, %11
              store i32 %12, i32* %3, align 4
              br label %if.end.0
              if.end.0:
              %13 = load i32, i32* %3, align 4
              ret i32 %13
            }
            define i32 @fib(i32){
              %2 = alloca i32, align 4
              store i32 %0, i32* %2, align 4
              %3 = alloca i32, align 4
              %4 = load i32, i32* %2, align 4
              %5 = icmp eq i32 %4, 0
              br i1 %5, label %if.true.1, label %if.else.1
              if.true.1:
              store i32 0, i32* %3, align 4
              br label %if.end.1
              if.else.1:
              %6 = load i32, i32* %2, align 4
              %7 = sub nsw i32 %6, 1
              %8 = call i32 @fibS(i32 %7)
              store i32 %8, i32* %3, align 4
              br label %if.end.1
              if.end.1:
              %9 = load i32, i32* %3, align 4
              ret i32 %9
            }
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @n, align 4
              %4 = load i32, i32* @n, align 4
              %5 = icmp sle i32 %4, 10
              br i1 %5, label %if.true.2, label %if.else.2
              if.true.2:
              %6 = load i32, i32* @n, align 4
              %7 = call i32 @fib(i32 %6)
              %8 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %7)
              br label %if.end.2
              if.else.2:
              br label %if.end.2
              if.end.2:
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_write(self):
        actual = self.execute("pscripts/write.p")
        expected = textwrap.dedent(r'''
            @x = common global i32 0, align 4
            @y = common global i32 0, align 4
            @z = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            define i32 @main(){
              store i32 12, i32* @x, align 4
              %1 = load i32, i32* @x, align 4
              %2 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %1)
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_read(self):
        actual = self.execute("pscripts/read.p")
        expected = textwrap.dedent(r'''
            @x = common global i32 0, align 4
            @y = common global i32 0, align 4
            @z = common global i32 0, align 4
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @y, align 4
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_read_write(self):
        actual = self.execute("pscripts/read-write.p")
        expected = textwrap.dedent(r'''
            @x = common global i32 0, align 4
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            @.str.read = private unnamed_addr constant [3 x i8] c"%d\00", align 1
            declare dso_local i32 @__isoc99_scanf(i8*, ...) #1
            define i32 @main(){
              %1 = alloca i32, align 4
              %2 = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* %1)
              %3 = load i32, i32* %1, align 4
              store i32 %3, i32* @x, align 4
              %4 = load i32, i32* @x, align 4
              %5 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %4)
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

    def test_arr(self):
        actual = self.execute("pscripts/arr.p")
        expected = textwrap.dedent(r'''
            @x = common dso_local global [20 x i32] zeroinitializer, align 16
            @.str.write = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
            declare dso_local i32 @printf(i8*, ...) #1
            define i32 @A(){
              %1 = alloca [8 x i32], align 16
              %2 = sub nsw i32 1, 1
              %3 = getelementptr inbounds [20 x i32], [20 x i32]* @x, i32 0, i32 %2
              store i32 3, i32* %3, align 4
              %4 = sub nsw i32 3, 3
              %5 = getelementptr inbounds [8 x i32], [8 x i32]* %1, i32 0, i32 %4
              store i32 0, i32* %5, align 4
              %6 = sub nsw i32 5, 3
              %7 = getelementptr inbounds [8 x i32], [8 x i32]* %1, i32 0, i32 %6
              store i32 6, i32* %7, align 4
              %8 = sub nsw i32 1, 1
              %9 = getelementptr inbounds [20 x i32], [20 x i32]* @x, i32 0, i32 %8
              %10 = load i32, i32* %9, align 4
              %11 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %10)
              %12 = sub nsw i32 2, 1
              %13 = getelementptr inbounds [20 x i32], [20 x i32]* @x, i32 0, i32 %12
              %14 = load i32, i32* %13, align 4
              %15 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %14)
              %16 = sub nsw i32 3, 3
              %17 = getelementptr inbounds [8 x i32], [8 x i32]* %1, i32 0, i32 %16
              %18 = load i32, i32* %17, align 4
              %19 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %18)
              %20 = sub nsw i32 5, 3
              %21 = getelementptr inbounds [8 x i32], [8 x i32]* %1, i32 0, i32 %20
              %22 = load i32, i32* %21, align 4
              %23 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 %22)
              ret i32 0
            }
            define i32 @main(){
              %1 = call i32 @A()
              ret i32 0
            }
        ''')
        self.assertEqual(expected.strip(), actual.strip())

if __name__ == "__main__":
    unittest.main()
