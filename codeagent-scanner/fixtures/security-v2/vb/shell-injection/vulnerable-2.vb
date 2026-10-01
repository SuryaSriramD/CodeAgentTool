Imports System.Data.Common
Imports System.Diagnostics
Module Sample
Sub Handle(db As DbConnection, input As String)
System.Diagnostics.Process.Start("cmd.exe", "/c " & input)
End Sub
End Module
