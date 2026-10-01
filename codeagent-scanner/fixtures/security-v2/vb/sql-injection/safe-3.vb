Imports System.Data.Common
Imports System.Diagnostics
Module Sample
Sub Handle(db As DbConnection, input As String)
Dim sql="SELECT * FROM users WHERE name=" & input
System.Console.WriteLine(sql)
End Sub
End Module
