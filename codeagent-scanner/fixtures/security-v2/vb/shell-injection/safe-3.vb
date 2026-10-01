Imports System.Data.Common
Imports System.Diagnostics
Module Sample
Sub Handle(db As DbConnection, input As String)
System.Console.WriteLine("sh -c " & input)
End Sub
End Module
